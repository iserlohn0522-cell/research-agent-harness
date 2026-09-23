#!/usr/bin/env python3
"""Helper for the workspace standard (WORKSPACE_STANDARD.md in the folder above this script, v1.3).

  init   <dir> [--by NAME] [--name NAME] [--migrate] [--allow-git] [--dry-run]
  task   <dir> <slug> [--by NAME] [--date YYYY-MM-DD]
  keep   <task-dir> <slug> (--claude-agent ID | --codex-thread ID)
  check  [<dir>]
  survey <dir>

init, task and keep only add files: they never overwrite, move or delete anything
(init's one edit to an existing file is putting @AGENTS.md at the top of CLAUDE.md).
keep copies a subagent's or thread's brief and final reply from its stored transcript
into <task-dir>/agents/. check and survey only report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

STANDARD_VERSION = "1.3"
STANDARD_MARK = "WORKSPACE_STANDARD.md"
TODO_MARK = "[[TODO"
TEMPLATES = Path(__file__).resolve().parent / "templates"

STANDARD_DIRS = {"work", "log", "docs", "deliverables", "data", "src", "tests", "refs", "archive"}
GENERATED_DIRS = {"node_modules", "__pycache__", "build", "dist", "venv", "env", "target", "out", "site"}
# Common project files that may sit at a workspace root without being declared (lower-case patterns).
ROOT_FILE_PATTERNS = (
    "agents.md", "claude.md", "gemini.md", "start_here.md", "readme*", "license*", "licence*", "copying*",
    "notice*", "citation*", "changelog*", "contributing*", "code_of_conduct*", "security*", "authors*",
    "*.toml", "*.lock", "*.cfg", "*.ini", "requirements*.txt", "environment*.yml", "environment*.yaml",
    "setup.py", "conftest.py", "noxfile.py", "manage.py", "package.json", "package-lock.json",
    "pnpm-workspace.yaml", "tsconfig*.json", "jsconfig*.json", "*.config.js", "*.config.cjs", "*.config.mjs",
    "*.config.ts", "go.mod", "go.sum", "makefile", "justfile", "snakefile", "cmakelists.txt", "dockerfile*",
    "docker-compose*.yml", "docker-compose*.yaml", "compose.yml", "compose.yaml", "index.html",
)
HOME_STANDARD_FOLDERS = {"desktop", "documents", "downloads", "pictures", "music", "videos"}
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
LOG_RE = re.compile(r"^\d{4}-\d{2}\.md$")
# A declaration line: "- `name/`: ..." or "- `a/`, `b.md` and `c/`: ..." (several names may share a line).
DECLARATION_RE = re.compile(r"^\s*-\s*((?:`[^`\n]+`\s*(?:,|、|and)?\s*)+):", re.M)
IMPORT_RE = re.compile(r"^\s*@AGENTS\.md\s*$", re.M | re.I)
ENTRY_RE = re.compile(r"(?i)^.*(start|handoff|readme_first).*\.(md|txt)$")

LIMIT_PER_MONTH = 60
LIMIT_FLAT = 40
LIMIT_DELIVERABLES = 60
LIMIT_LOG_KB = 100
LIMIT_START_KB = 12


# ---------------------------------------------------------------- helpers

def home() -> Path:
    return Path.home().resolve()


def is_drive_root(p: Path) -> bool:
    return p.parent == p


def within(p: Path, base: Path) -> bool:
    return p == base or base in p.parents


def find_root(start: Path) -> Path | None:
    """Find a declared project root; nearest legacy AGENTS is a provisional fallback."""
    legacy = None
    for d in (start, *start.parents):
        if is_drive_root(d) or d == home():
            break
        if location_reason(d):
            break
        p = d / "AGENTS.md"
        if p.is_file():
            if re.search(r"^Workspace-Root:\s*\.\s*$", read_text(p), re.M):
                return d
            if legacy is None:
                legacy = d
    return legacy


def declared_names(agents: str) -> tuple[set[str], set[str]]:
    """Folders and files declared in AGENTS.md, one or several per declaration line."""
    folders: set[str] = set()
    files: set[str] = set()
    for match in DECLARATION_RE.finditer(agents):
        for name in re.findall(r"`([^`]+)`", match.group(1)):
            name = name.strip()
            if name.endswith("/") and "/" not in name[:-1] and "\\" not in name:
                folders.add(name[:-1])
            elif "/" not in name and "\\" not in name:
                files.add(name)
    return folders, files


def common_root_file(name: str) -> bool:
    lower = name.lower()
    return any(fnmatch.fnmatchcase(lower, pattern) for pattern in ROOT_FILE_PATTERNS)


def validate_targets(root: Path, targets: list[tuple[Path, bool]]) -> str | None:
    """Reject targets that resolve outside the workspace and file/folder collisions before any write."""
    for target, want_dir in targets:
        if not within(target.resolve(), root.resolve()):
            return f"target escapes workspace: {target}"
        if target.exists() and target.is_dir() != want_dir:
            return f"file/directory collision: {target}"
        for parent in target.parents:
            if parent.exists() and not parent.is_dir():
                return f"parent is not a directory: {parent}"
            if parent == root:
                break
    return None


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def render(template: str, **values: str) -> str:
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text


def write_new(p: Path, text: str, dry: bool) -> None:
    if dry:
        return
    with p.open("x", encoding="utf-8", newline="") as f:  # "x" never overwrites
        f.write(text)


def append(p: Path, text: str, dry: bool) -> None:
    if dry:
        return
    existing = read_text(p) if p.exists() else ""
    if "\r\n" in existing:
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    if existing and not existing.endswith("\n"):
        text = ("\r\n" if "\r\n" in existing else "\n") + text
    with p.open("a", encoding="utf-8", newline="") as f:
        f.write(text)


def writer(raw: str | None) -> str:
    return (raw or "").strip().strip("[]").strip()


def short(items: list[str], n: int = 8) -> str:
    return ", ".join(items[:n]) + (f" and {len(items) - n} more" if len(items) > n else "")


def rel(p: Path, base: Path) -> str:
    return str(p.relative_to(base)).replace("\\", "/")


def visible(d: Path) -> list[Path]:
    try:
        return [e for e in d.iterdir() if not e.name.startswith(".")]
    except OSError:
        return []


def workspaces_below(d: Path, limit: int) -> list[Path]:
    """Children, or grandchildren under a child without one, that hold AGENTS.md."""
    found: list[Path] = []
    for c in sorted((e for e in visible(d) if e.is_dir()), key=lambda e: e.name.lower()):
        if (c / "AGENTS.md").is_file():
            found.append(c)
        else:
            found += [g for g in visible(c) if g.is_dir() and (g / "AGENTS.md").is_file()]
        if limit and len(found) >= limit:
            break
    return found[:limit] if limit else found


def env_dirs(*names: str) -> list[Path]:
    return [Path(v).resolve() for v in (os.environ.get(n) for n in names) if v]


def location_reason(d: Path) -> str | None:
    """Places that are never a workspace without the user's say-so."""
    h = home()
    if is_drive_root(d):
        return "a drive root"
    if d == h:
        return "the home directory"
    name = d.name.lower()
    if d.parent == h and (name in HOME_STANDARD_FOLDERS or name.startswith("onedrive")):
        return f"a standard folder of the home directory ({d.name})"
    for cfg in (".codex", ".claude"):
        if within(d, h / cfg):
            return f"inside the tool configuration directory ~/{cfg}"
    system = env_dirs("SystemRoot", "ProgramFiles", "ProgramFiles(x86)", "ProgramData")
    if os.name != "nt":
        system += [Path(x) for x in ("/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var")]
    for s in system:
        if within(d, s):
            return f"inside the system directory {s}"
    if d in env_dirs("TEMP", "TMP", "TMPDIR"):
        return "the temporary-files root"
    return None


def content_reason(d: Path, allow_git: bool) -> str | None:
    """Directories whose contents say they are not a single new workspace."""
    if not d.is_dir():
        return None
    nested = workspaces_below(d, limit=2)
    if len(nested) >= 2:
        return f"a folder holding several projects ({short([rel(p, d) for p in nested])} ...)"
    if (d / ".git").exists() and not allow_git:
        return ("a git repository. If it is the user's own, rerun with --allow-git; "
                "if it is a clone of someone else's project, ask the user first")
    return None


# ---------------------------------------------------------------- init

def cmd_init(a: argparse.Namespace) -> int:
    d = Path(a.dir).expanduser().resolve()
    dry = a.dry_run
    if d.exists() and not d.is_dir():
        print(f"REFUSED: {d} is a file, not a directory.")
        return 2
    reason = location_reason(d)
    if reason:
        print(f"REFUSED: {d} is {reason}. Ask the user before initializing here.")
        return 2
    root = find_root(d)
    if a.independent and (d / "AGENTS.md").is_file() and not re.search(r"^Workspace-Root:\s*\.\s*$", read_text(d / "AGENTS.md"), re.M):
        print(f"REFUSED: {d / 'AGENTS.md'} exists without the line `Workspace-Root: .`; add that line, "
              "then run with --migrate.")
        return 2
    if a.migrate and root != d:
        print(f"REFUSED: --migrate needs an AGENTS.md in {d} itself.")
        return 2
    if not a.migrate and root is not None and not (a.independent and root != d):
        if root == d:
            print(f"REFUSED: {d} already has AGENTS.md; read it instead. "
                  "Use --migrate only when the user asked to restructure this workspace.")
        else:
            print(f"REFUSED: {d} is inside the workspace {root}; read {root / 'AGENTS.md'} and work there.")
        return 2
    reason = content_reason(d, a.allow_git or a.migrate)
    if reason:
        advice = "" if "--allow-git" in reason else " Ask the user before initializing here."
        print(f"REFUSED: {d} is {reason}.{advice}")
        return 2

    day = dt.date.today().isoformat()
    targets = [(d / name, False) for name in ("AGENTS.md", "CLAUDE.md", "START_HERE.md")]
    targets += [(d / name, True) for name in ("work", "log")]
    targets += [(d / "log" / f"{day[:7]}.md", False)]
    problem = validate_targets(d, targets)
    if problem:
        print(f"REFUSED: {problem}")
        return 2
    month = day[:7]
    name = a.name or d.name
    existing = sorted((e.name + ("/" if e.is_dir() else "")) for e in visible(d)) if d.exists() else []
    created: list[str] = []
    kept: list[str] = []
    claude_edited = False

    if not d.exists() and not dry:
        d.mkdir(parents=True)

    def make(relpath: str, template: str) -> None:
        p = d / relpath
        if p.exists():
            kept.append(relpath)
        else:
            write_new(p, render(template, name=name, date=day, month=month), dry)
            created.append(relpath)

    if not a.migrate:
        make("AGENTS.md", "AGENTS.template.md")
    claude = d / "CLAUDE.md"
    if claude.exists():
        if IMPORT_RE.search(read_text(claude)):
            kept.append("CLAUDE.md")
        else:
            claude_edited = True
            if not dry:
                raw = claude.read_bytes()
                bom = raw.startswith(b"\xef\xbb\xbf")
                body = raw[3:] if bom else raw
                nl = b"\r\n" if b"\r\n" in body else b"\n"
                claude.write_bytes((b"\xef\xbb\xbf" if bom else b"") + b"@AGENTS.md" + nl + nl + body)
    else:
        make("CLAUDE.md", "CLAUDE.template.md")
    make("START_HERE.md", "START_HERE.template.md")
    for sub in ("work", "log"):
        p = d / sub
        if p.is_dir():
            kept.append(sub + "/")
        elif p.exists():
            print(f"WARNING: {p} exists and is not a folder; left alone.")
        else:
            if not dry:
                p.mkdir(parents=True)
            created.append(sub + "/")

    logdir = d / "log"
    if logdir.is_dir() or (dry and not logdir.exists()):
        logfile = logdir / f"{month}.md"
        if not logfile.exists():
            write_new(logfile, render("LOG.template.md", month=month), dry)
            created.append(f"log/{month}.md")
        title = "补齐工作区规范文件" if a.migrate else "工作区初始化"
        lines = [f"- 按工作区规范 v{STANDARD_VERSION} 新建：{'、'.join(created) or '无'}。"
                 + ("AGENTS.md 未改动。" if a.migrate else "")]
        if claude_edited:
            lines.append("- 已有的 CLAUDE.md 顶部加了 `@AGENTS.md`，其余内容未动。")
        if existing:
            shown = "、".join(existing[:15]) + (" 等" if len(existing) > 15 else "")
            lines.append(f"- 目录里原有 {len(existing)} 项，均未移动：{shown}。")
        elif not a.migrate:
            lines.append("- 目录原为空。")
        append(logfile, f"\n## {day} {title} [{writer(a.by) or 'agent'}]\n\n" + "\n".join(lines) + "\n", dry)

    print(f"{'[dry run] ' if dry else ''}{'Migrated (additive part)' if a.migrate else 'Initialized'} "
          f"{d} to workspace standard v{STANDARD_VERSION}.")
    print(f"  created: {', '.join(created) or 'nothing'}")
    if kept:
        print(f"  kept as is: {', '.join(kept)}")
    if claude_edited:
        print("  CLAUDE.md: put @AGENTS.md at the top. Move its project facts into AGENTS.md "
              "and keep only Claude-specific lines below the import.")
    if existing:
        print(f"  existing entries left in place: {len(existing)} (list them in START_HERE.md)")
    if a.migrate:
        print("Next: add a layout section naming the standard to AGENTS.md, build START_HERE.md from the "
              "existing entry files, and prepare a numbered move list for the user.")
    else:
        print("Next: replace every [[TODO]] in AGENTS.md and START_HERE.md, then start a task folder "
              "with `workspace.py task <dir> <slug>`.")
    return 0


# ---------------------------------------------------------------- task

def slugify(raw: str) -> str:
    s = re.sub(r"[\s_]+", "-", raw.strip().lower())
    s = re.sub(r"[^a-z0-9-]", "", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def month_mode(work: Path) -> bool:
    names = [e.name for e in visible(work) if e.is_dir()] if work.is_dir() else []
    if any(MONTH_RE.match(n) for n in names):
        return True
    return not any(DATED_RE.match(n) for n in names)


def cmd_task(a: argparse.Namespace) -> int:
    start = Path(a.dir).expanduser().resolve()
    reason = location_reason(start)
    if reason:
        print(f"REFUSED: {start} is {reason}")
        return 2
    root = find_root(start)
    if root is None:
        print(f"REFUSED: no AGENTS.md in {start} or above; initialize the workspace first.")
        return 2
    slug = slugify(a.slug)
    if not slug:
        print("REFUSED: the slug needs ASCII letters or digits, e.g. relax-batch1.")
        return 2
    try:
        day = (dt.date.fromisoformat(a.date) if a.date else dt.date.today()).isoformat()
    except ValueError:
        print("REFUSED: --date must be YYYY-MM-DD.")
        return 2
    work = root / "work"
    folder = (work / day[:7] if month_mode(work) else work) / f"{day}-{slug}"
    if folder.exists():
        print(f"EXISTS: {folder}. Continue there only if it is your task; otherwise choose another slug.")
        return 1
    problem = validate_targets(root, [(root / "work", True), (folder, True), (folder / "README.md", False)])
    if problem:
        print(f"REFUSED: {problem}")
        return 2
    folder.mkdir(parents=True)
    by = writer(a.by) or "[[TODO: 线程或代理，例如 Codex 主对话、Claude]]"
    write_new(folder / "README.md", render("TASK_README.template.md", slug=slug, date=day, by=by), False)
    if STANDARD_MARK not in read_text(root / "AGENTS.md"):
        print("NOTE: this workspace's AGENTS.md does not name the standard; make sure its own conventions "
              "do not put new work elsewhere.")
    print(folder)
    return 0


# ---------------------------------------------------------------- keep

def text_of(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    return "".join(c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text")


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                records.append(json.loads(line))
            except ValueError:
                continue
    return records


def claude_agent_record(agent_id: str) -> tuple[Path, str, str, str] | None:
    """Transcript path, brief, final reply and model of a Claude Code subagent."""
    found = sorted((Path.home() / ".claude" / "projects").glob(f"*/*/subagents/agent-{agent_id}.jsonl"),
                   key=lambda p: p.stat().st_mtime)
    if not found:
        return None
    records = read_jsonl(found[-1])
    brief = next((text_of(r.get("message") or {}) for r in records if r.get("type") == "user"
                  and text_of(r.get("message") or {})), "")
    final = next((r for r in reversed(records) if r.get("type") == "assistant"
                  and text_of(r.get("message") or {})), None)
    if final is None:
        return None
    return found[-1], brief, text_of(final["message"]), (final["message"].get("model") or "")


def codex_thread_record(thread_id: str) -> tuple[Path, str] | None:
    """Rollout path and last agent message of a Codex thread or subagent."""
    home_dir = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    found = [p for sub in ("sessions", "archived_sessions") if (home_dir / sub).is_dir()
             for p in (home_dir / sub).rglob(f"rollout-*-{thread_id}.jsonl")]
    if not found:
        return None
    path = max(found, key=lambda p: p.stat().st_mtime)
    finals = [r["payload"].get("last_agent_message") for r in read_jsonl(path)
              if r.get("type") == "event_msg" and (r.get("payload") or {}).get("type") == "task_complete"
              and r["payload"].get("last_agent_message")]
    return (path, finals[-1]) if finals else None


def cmd_keep(a: argparse.Namespace) -> int:
    task = Path(a.dir).expanduser().resolve()
    root = find_root(task)
    if root is None or not (within(task, root / "work") and task != root / "work") or not task.is_dir():
        print(f"REFUSED: {task} is not a task folder under a workspace's work/; give the current task folder.")
        return 2
    slug = slugify(a.slug)
    if not slug:
        print("REFUSED: the slug needs ASCII letters or digits, e.g. reviewer-barrier-check.")
        return 2
    now = dt.datetime.now()
    if a.claude_agent:
        got = claude_agent_record(a.claude_agent)
        if got is None:
            print(f"NOT FOUND: no finished Claude Code subagent transcript for {a.claude_agent}.")
            return 1
        source_path, brief, result, model = got
        source = f"Claude Code 子代理 {a.claude_agent}" + (f"（{model}）" if model else "")
    else:
        got = codex_thread_record(a.codex_thread)
        if got is None:
            print(f"NOT FOUND: no finished Codex thread or subagent rollout for {a.codex_thread}.")
            return 1
        source_path, result = got
        brief = "Codex 不在本地保存子代理收到的任务说明；需要时见派发它的主线程。"
        source = f"Codex 线程 {a.codex_thread}"
    target = task / "agents" / f"{now:%Y-%m-%d-%H%M}-{slug}.md"
    problem = validate_targets(root, [(task / "agents", True), (target, False)])
    if problem:
        print(f"REFUSED: {problem}")
        return 2
    if target.exists():
        print(f"EXISTS: {target}; choose another slug.")
        return 1
    target.parent.mkdir(exist_ok=True)
    write_new(target, f"# {slug}\n\n- 保存于：{now:%Y-%m-%d %H:%M}\n- 来源：{source}\n- 原始记录：`{source_path}`\n\n"
                      f"## 任务说明\n\n{brief.strip()}\n\n## 结果\n\n{result.strip()}\n", False)
    print(target)
    return 0


# ---------------------------------------------------------------- check and survey

class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.standard = False
        self.problems: list[str] = []
        self.notes: list[str] = []
        self.claude = "-"
        self.entry = "-"
        self.root_files = 0
        self.root_dirs = 0


def inspect(root: Path) -> Report:
    r = Report(root)
    agents = read_text(root / "AGENTS.md")
    r.standard = STANDARD_MARK in agents
    entries = visible(root)
    r.root_files = sum(1 for e in entries if e.is_file())
    r.root_dirs = sum(1 for e in entries if e.is_dir())
    serious = r.problems if r.standard else r.notes

    claude = root / "CLAUDE.md"
    if not claude.exists():
        r.claude = "missing"
        serious.append("[claude] no CLAUDE.md: use an explicit import for cross-version consistency; "
                       "create CLAUDE.md with the single line @AGENTS.md")
    elif IMPORT_RE.search(read_text(claude)):
        r.claude = "ok"
    else:
        r.claude = "no-import"
        r.problems.append("[claude] CLAUDE.md does not import AGENTS.md, so the explicit shared-rule import is missing for this "
                          "workspace's rules; put @AGENTS.md at its top")

    start_here = root / "START_HERE.md"
    if start_here.exists():
        r.entry = "START_HERE.md"
        kb = start_here.stat().st_size / 1024
        if kb > LIMIT_START_KB:
            r.problems.append(f"[size] START_HERE.md is {kb:.0f} KB; keep it to one page and history in the record")
        if TODO_MARK in read_text(start_here):
            r.problems.append("[todo] START_HERE.md still has [[TODO]] markers")
    else:
        others = sorted(e.name for e in entries if e.is_file() and ENTRY_RE.search(e.name))
        r.entry = ", ".join(others) if others else "none"
        serious.append("[missing] START_HERE.md" + (f" (entry files now: {r.entry})" if others else ""))
    if TODO_MARK in agents:
        r.problems.append("[todo] AGENTS.md still has [[TODO]] markers")

    if not r.standard:
        r.notes.append(f"[legacy] AGENTS.md does not name the workspace standard; the root holds "
                       f"{r.root_files} files and {r.root_dirs} folders. Restructure only when the user asks.")
        return r

    declared, declared_files = declared_names(agents)
    for req in ("work", "log"):
        if not (root / req).is_dir():
            r.problems.append(f"[missing] {req}/")
    odd = []
    for e in sorted(entries, key=lambda x: x.name.lower()):
        if e.is_dir():
            if e.name not in STANDARD_DIRS | GENERATED_DIRS and e.name not in declared:
                odd.append(e.name + "/")
        elif not common_root_file(e.name) and e.name not in declared_files:
            odd.append(e.name)
    if odd:
        r.problems.append(f"[root] {len(odd)} item(s) outside the layout: {short(odd)}. Move files into a task "
                          "folder, declare folders in AGENTS.md, or propose moving them to archive/")
    check_work(root / "work", r)
    check_log(root / "log", r)
    changed, truncated = unrecorded(root)
    if changed:
        r.notes.append(f"[record] {len(changed)} file(s) changed after the last record entry: {short(changed, 5)}. "
                       "Add an entry if the change is not recorded yet")
    if truncated:
        r.notes.append("[record] stopped scanning for unrecorded changes after 20000 files")
    deliverables = root / "deliverables"
    if deliverables.is_dir() and len(visible(deliverables)) > LIMIT_DELIVERABLES:
        r.problems.append(f"[size] deliverables/ holds {len(visible(deliverables))} entries "
                          f"(limit {LIMIT_DELIVERABLES}); group them by year")
    return r


def check_work(work: Path, r: Report) -> None:
    if not work.is_dir():
        return
    subdirs = [e for e in visible(work) if e.is_dir()]
    months = [e for e in subdirs if MONTH_RE.match(e.name)]
    dated = [e for e in subdirs if DATED_RE.match(e.name)]
    other = [e for e in subdirs if e not in months and e not in dated]
    tasks = list(dated)
    for m in months:
        inner = visible(m)
        folders = [e for e in inner if e.is_dir()]
        if len(folders) > LIMIT_PER_MONTH:
            r.problems.append(f"[size] work/{m.name} holds {len(folders)} task folders (limit {LIMIT_PER_MONTH})")
        loose = [e.name for e in inner if e.is_file()]
        if loose:
            r.problems.append(f"[work] files directly in work/{m.name}: {short(loose)}; they belong in a task folder")
        tasks += folders
    if dated and not months and len(dated) > LIMIT_FLAT:
        r.problems.append(f"[size] work/ holds {len(dated)} task folders; switch to month folders work/YYYY-MM/")
    loose = [e.name for e in visible(work) if e.is_file()]
    if loose:
        r.problems.append(f"[work] files directly in work/: {short(loose)}; they belong in a task folder")
    unfinished = [rel(t, work.parent) for t in tasks if TODO_MARK in read_text(t / "README.md")]
    if unfinished:
        r.problems.append(f"[todo] unfinished task README: {short(unfinished)}")
    no_readme = [rel(t, work.parent) for t in tasks if not (t / "README.md").is_file()]
    if no_readme:
        r.problems.append(f"[work] {len(no_readme)} task folder(s) without README.md: {short(no_readme)}")
    if other:
        r.notes.append(f"[work] {len(other)} folder(s) in work/ not named by month or date "
                       f"(pre-standard?): {short([e.name for e in other])}")


def check_log(log: Path, r: Report) -> None:
    for e in visible(log) if log.is_dir() else []:
        if e.is_file() and LOG_RE.match(e.name):
            kb = e.stat().st_size / 1024
            if kb > LIMIT_LOG_KB:
                r.problems.append(f"[size] log/{e.name} is {kb:.0f} KB; keep entries short, details in task folders")
        else:
            r.problems.append(f"[log] log/{e.name} is not a monthly record file (YYYY-MM.md)")


def unrecorded(root: Path, tolerance: float = 10.0, cap: int = 20000) -> tuple[list[str], bool]:
    """Files modified after the newest monthly record file (START_HERE.md, log/, archive/, data/raw/ excluded)."""
    logdir = root / "log"
    logs = [e for e in visible(logdir) if e.is_file() and LOG_RE.match(e.name)] if logdir.is_dir() else []
    if not logs:
        return [], False
    last = max(e.stat().st_mtime for e in logs)
    changed: list[str] = []
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        dirnames[:] = [n for n in dirnames if not n.startswith(".")
                       and not (here == root and n in ("log", "archive"))
                       and not (here == root / "data" and n == "raw")]
        for f in filenames:
            if f.startswith(".") or (here == root and f == "START_HERE.md"):
                continue
            seen += 1
            if seen > cap:
                return changed, True
            p = here / f
            try:
                if p.stat().st_mtime > last + tolerance:
                    changed.append(rel(p, root))
            except OSError:
                pass
    return changed, False


def cmd_check(a: argparse.Namespace) -> int:
    start = Path(a.dir).expanduser().resolve()
    reason = location_reason(start)
    if reason:
        print(f"REFUSED: {start} is {reason}")
        return 2
    root = find_root(start)
    if root is None:
        print(f"No workspace: no AGENTS.md in {start} or its parents (the home directory and drive roots "
              "do not count). A new workspace is set up with `workspace.py init`.")
        return 1
    r = inspect(root)
    print(f"Workspace: {root} ({'workspace standard' if r.standard else 'not on the standard'})")
    for line in r.problems + r.notes:
        print("  " + line)
    if not r.problems and not r.notes:
        print("  nothing to report")
    return 1 if r.problems else 0


def cmd_survey(a: argparse.Namespace) -> int:
    base = Path(a.dir).expanduser().resolve()
    rows = []
    for child in sorted((e for e in visible(base) if e.is_dir()), key=lambda e: e.name.lower()):
        targets = [child] if (child / "AGENTS.md").is_file() else workspaces_below(child, limit=0)
        if not targets:
            n = visible(child)
            rows.append((child.name, "none", "-", "-", str(sum(e.is_file() for e in n)),
                         str(sum(e.is_dir() for e in n)), "-"))
            continue
        expanded = list(targets)
        for parent in targets:
            body = read_text(parent / "AGENTS.md")
            match = re.search(r"^## Child workspaces\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
            if match:
                for child_rel in re.findall(r"^\s*-\s*`([^`]+/)`", match[1], re.M):
                    candidate = (parent / child_rel).resolve()
                    if within(candidate, parent) and candidate != parent and candidate not in expanded:
                        expanded.append(candidate)
        for t in expanded:
            r = inspect(t)
            rows.append((rel(t, base), "standard" if r.standard else "legacy", r.claude, r.entry,
                         str(r.root_files), str(r.root_dirs), str(len(r.problems))))
    header = ("workspace", "status", "CLAUDE.md", "entry file", "root files", "root dirs", "problems")
    widths = [max(len(h), *(len(row[i]) for row in rows)) if rows else len(h) for i, h in enumerate(header)]
    widths[3] = min(widths[3], 40)
    for row in (header, *rows):
        cells = [c if len(c) <= widths[i] else c[: widths[i] - 1] + "…" for i, c in enumerate(row)]
        print("  ".join(c.ljust(widths[i]) for i, c in enumerate(cells)).rstrip())
    return 0


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("init", help="set up a new workspace (additive only)")
    pi.add_argument("dir")
    pi.add_argument("--by", default="agent", help="who initializes, e.g. Codex or Claude")
    pi.add_argument("--name", help="workspace name for the templates (default: the folder name)")
    pi.add_argument("--migrate", action="store_true",
                    help="existing workspace: add the missing standard files and leave AGENTS.md alone")
    pi.add_argument("--allow-git", action="store_true", help="the directory is a git repository the user owns")
    pi.add_argument("--independent", action="store_true", help="user explicitly designated a separate child workspace")
    pi.add_argument("--dry-run", action="store_true", help="show what would be created")
    pt = sub.add_parser("task", help="create today's task folder with its README")
    pt.add_argument("dir")
    pt.add_argument("slug", help="short English name, e.g. relax-batch1")
    pt.add_argument("--by", help="who does the task, e.g. Codex or Claude")
    pt.add_argument("--date", help="YYYY-MM-DD, default today")
    pk = sub.add_parser("keep", help="save a subagent's or thread's brief and final reply into <task-dir>/agents/")
    pk.add_argument("dir", help="the current task folder")
    pk.add_argument("slug", help="short English name, e.g. reviewer-barrier-check")
    src = pk.add_mutually_exclusive_group(required=True)
    src.add_argument("--claude-agent", help="agent ID of a finished Claude Code subagent")
    src.add_argument("--codex-thread", help="thread ID of a finished Codex subagent or thread")
    pc = sub.add_parser("check", help="report what is out of place (read-only)")
    pc.add_argument("dir", nargs="?", default=".")
    ps = sub.add_parser("survey", help="one line per workspace in a folder of projects (read-only)")
    ps.add_argument("dir")
    a = p.parse_args(argv)
    return {"init": cmd_init, "task": cmd_task, "keep": cmd_keep, "check": cmd_check, "survey": cmd_survey}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
