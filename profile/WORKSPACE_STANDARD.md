# Workspace Standard

Shared by Codex and Claude Code. Pointed to by `{{GUIDES_DIR}}/AGENTS.md`; Claude imports it through `~/.claude/CLAUDE.md`. Version 1.3, 2026-09-23. Script and templates: `{{GUIDES_DIR}}/workspace-standard/`.

A workspace is a directory the user gives agents to work in. This standard lets any agent, thread or subagent find the rules, the current state and the place for a new file from the files alone, without the previous session.

## On arrival

1. Look for `AGENTS.md` in the working directory, then in each parent. Stop below the home directory and drive roots: an `AGENTS.md` there holds machine rules, not a workspace. The nearest one containing the line `Workspace-Root: .` marks the workspace root; if none does, the nearest `AGENTS.md` does.
2. Found: read it unless it is already loaded, then the `START_HERE.md` beside it. If that `AGENTS.md` names this standard, use the layout below. Otherwise the workspace keeps its own conventions: use this layout only for what they leave open, and restructure nothing unless the user asks (see Migration).
3. Not found: this is a new workspace; initialize it before other work. Ask the user first instead when the directory is a drive root, the home directory or one of its standard folders (Desktop, Documents, Downloads), a system or tool-configuration directory (such as `C:/Windows`, `~/.codex`, `~/.claude`), a folder holding several projects, or a clone of someone else's repository.

Subagents skip this check and work where their parent points them.

## Initializing

Initialization adds files. It never moves, renames or deletes anything.

1. Run `python {{GUIDES_DIR}}/workspace-standard/workspace.py init <dir> --by <you>`. It creates the required files from the templates, skips files that exist, puts `@AGENTS.md` at the top of an existing `CLAUDE.md`, and writes the first record entry. It refuses the ask-first cases above and says why. A git repository needs `--allow-git` once you know it is the user's own; a subfolder that the user makes a separate project inside a workspace needs `--independent`. Without Python, copy `templates/*.template.md` by hand.
2. Replace every `[[TODO ...]]` in `AGENTS.md` and `START_HERE.md` and keep the template headings: what the workspace is for (from the user's request and what is already there), what is known, and the next step. `AGENTS.md` holds rules and working facts (paths, environments, commands, constraints); results, literature values and notes go to task folders or `refs/` with their sources. If the directory already had an agent instruction file (`CLAUDE.md`, `AGENT.md`, `GEMINI.md`), carry its project facts into `AGENTS.md` and keep only Claude-specific lines below the import in `CLAUDE.md`.
3. Leave existing files where they are and list them under "东西在哪" in `START_HERE.md`. If some clearly belong elsewhere in the layout, propose the moves to the user.
4. Continue with the user's task in a new task folder.

## Layout

```
<workspace>/
  AGENTS.md          rules for all agents, in English; the only rule file
  CLAUDE.md          just `@AGENTS.md`; Claude-only lines, if any, below it
  START_HERE.md      one page in Chinese: purpose, state, next step, where things are
  work/YYYY-MM/YYYY-MM-DD-<slug>/   one folder per task, with README.md
  log/YYYY-MM.md     the workspace record: one file per month, append-only
  docs/              PLAN.md (stages and end points), AUTHORIZATION.md, methods/
  deliverables/YYYY-MM-DD-<name>/   what goes to people: manuscripts, figures, slides, reports
  data/raw/          inputs as received; read-only
  data/processed/    derived data that several tasks reuse, with the script that made it
  src/  tests/       reusable code and its tests
  refs/              literature and page notes
  archive/           material from before the standard; read-only, with an index
```

- Required: `AGENTS.md`, `CLAUDE.md`, `START_HERE.md`, `work/`, `log/`. Create the rest when first needed. Hidden folders (`.git`, `.venv` and the like), generated folders (`node_modules`, `build`, `dist`, `__pycache__`, `venv`) and common project files (README, LICENSE, build, package and environment files) need nothing. Declare any other top-level folder or file in the layout section of `AGENTS.md` as a line starting with ``- `name/`:`` or ``- `file.ext`:``; several names may share one line, as in ``- `old-a/`, `old-b/`: earlier tasks``.
- Keep the rules in the root `AGENTS.md`. Codex also loads an `AGENTS.md` in a subfolder when it works inside that subfolder, so a subfolder gets its own only when the user makes it a separate project: its `AGENTS.md` contains `Workspace-Root: .`, it has its own `CLAUDE.md`, `START_HERE.md`, `work/` and `log/`, and the parent lists it under `## Child workspaces` as ``- `path/`: purpose``.
- `START_HERE.md` is the project's single entry. Update it when the state or the next step changes. Task READMEs and result or status pages it links to are fine; do not create other entry or handoff files.
- A task folder is named by date and a short lowercase hyphenated English slug, with the stage when there is one (`2026-09-22-s3-ablation-batch1`). Its README gives goal and end point, inputs, method, result with fixed paths, and status. The task's scripts, intermediate outputs, run logs and scratch files stay inside it; subagent reports go in its `agents/` and messages to or from other threads in its `messages/`. A workspace that will only ever hold a few tasks may drop the month level.
- A record entry starts with the heading `## YYYY-MM-DD <what> [<writer>]` (writer `Codex`, `Claude` …), followed by one to three bullets: what was done or decided, the result, the task folder or file. Decisions are recorded there when made; `START_HERE.md` carries the ones still in force.

## Working

- Unless the workspace's layout says otherwise, a new file goes into the current task folder. `python {{GUIDES_DIR}}/workspace-standard/workspace.py task <dir> <slug>` creates today's task folder with its README; `workspace.py keep <task-dir> <slug> --claude-agent <id>` (or `--codex-thread <id>`) saves a finished subagent's or thread's brief and final reply into the task's `agents/`.
- A lasting product that later tasks extend or reuse (literature notes, a dataset, a manuscript) lives in its layout folder (`refs/`, `data/processed/`, `docs/`, `deliverables/`) or a folder declared in `AGENTS.md`, never inside one task's folder. A small change to it needs no task folder, only a record entry.
- One writer per shared file: `START_HERE.md`, `docs/PLAN.md` and decisions belong to the main thread (the only thread, when there is one); a task folder belongs to the agent doing that task; a lasting product is changed by one task at a time; subagents write only where their parent says. Everyone else reads.
- Every change to the workspace, however small, ends with its record entry, a complete README when the task has a folder, and an updated `START_HERE.md` when the state or the next step changed.
- `workspace.py check <dir>` lists what is out of place and the files changed after the last record entry; `workspace.py survey <dir>` gives one line per workspace in a folder of projects. Both only report.

## Migration

Restructure an existing workspace only when the user asks. First the additive part: `workspace.py init <dir> --migrate` (creates the missing standard files and leaves `AGENTS.md` alone), a layout section in `AGENTS.md` that names this standard and declares the folders the workspace keeps, and a `START_HERE.md` built from the existing entry files. Then a numbered move list: what goes to `archive/` or into the layout, and which references in scripts, entry files and records change. Nothing moves before the user approves the list; move at a stage boundary, never while jobs run. The old stage log stays read-only, and `log/` starts at the migration date.
