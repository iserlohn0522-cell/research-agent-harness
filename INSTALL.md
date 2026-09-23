# Install guide (for the agent doing the installation)

You are Codex or Claude Code, asked by your user to install this repository's research-agent profile on their computer. Work through the steps in order. Speak to the user in Chinese unless they prefer another language; `README.md` explains the profile to them, this file is for you.

## Ground rules

1. Change no security, permission or account setting. In Codex `config.toml`, touch only the key named in step 5; leave `approval_policy`, `sandbox_mode`, `model`, `model_provider`, `[model_providers.*]`, `[projects.*]`, `[mcp_servers.*]`, `notify` and everything else as they are. In Claude Code, do not edit `settings.json` at all (permissions, `defaultMode`, allow and deny lists, hooks, env, model).
2. Never overwrite silently. Before changing an existing file, copy it next to itself as `<name>.bak-YYYYMMDD-HHMMSS`, and list every backup in your final report.
3. Before writing anything, show the user a short plan of the files you will create or change, and wait for one go-ahead. After that, finish the install without asking file by file.
4. Install skills and plugins only as the user picks them in step 7.
5. Replace every `{{GUIDES_DIR}}` and `{{GUIDES_IMPORT}}` placeholder in the files you install; none may remain.

## Step 1 — Look around (read-only)

- Operating system and home directory.
- Codex is in use if `codex --version` works or the Codex home exists. The Codex home is `$CODEX_HOME` when that variable is set, otherwise `~/.codex`.
- Claude Code is in use if `claude --version` works or `~/.claude` exists.
- Existing files this install could touch: in the Codex home `AGENTS.md`, `config.toml` (note whether it has an `[agents]` table) and `agents/*.toml` (note each `name`); `~/.claude/CLAUDE.md`; `~/.claude/agents/*.md` (note each `name`).
- Python 3 (`python --version` or `python3 --version`). Only the workspace helper needs it; without Python everything else still works, and you tell the user the helper will run once Python is installed.

## Step 2 — Ask the user (one message)

1. Which tools to set up: Codex, Claude Code or both (default: whichever is installed).
2. If a global rule file already exists (`AGENTS.md` in the Codex home, `~/.claude/CLAUDE.md`), how to handle it:
   - replace it with this profile (a backup is kept);
   - merge: keep their file and append this profile below it, pointing out any rule of theirs that contradicts it;
   - guides only: install the guides and subagent roles, and leave their global rules unchanged.
3. Reply language (default Chinese), and optionally one line about their research field. Leaving the field empty is fine; the profile is field-neutral.

## Step 3 — Choose the guides folder

- Codex in use: GUIDES_DIR is the Codex home, for example `C:/Users/alice/.codex` or `/Users/alice/.codex`.
- Claude Code only: GUIDES_DIR is `~/.claude/research-agent`, written as an absolute path.
- Write GUIDES_DIR as an absolute path with forward slashes.
- GUIDES_IMPORT is the same folder written relative to `~/.claude/`, for Claude Code imports: `../.codex` when GUIDES_DIR is `~/.codex`, `research-agent` when it is `~/.claude/research-agent`. When `CODEX_HOME` points somewhere else, use the relative path from `~/.claude/` to it.

## Step 4 — Install the profile

Copy these files with the placeholders replaced:

| From this repository | To |
|---|---|
| `profile/GLOBAL_AGENTS.md` | `GUIDES_DIR/AGENTS.md`. When GUIDES_DIR is the Codex home and an `AGENTS.md` is already there, apply the step 2 choice to it (for "guides only", leave it unchanged). In a Claude-Code-only install the file is new here, and the step 2 choice applies to `~/.claude/CLAUDE.md` in step 6. |
| `profile/REPLY_STYLE.md`, `profile/HANDOFF_GUIDE.md`, `profile/THREAD_SPLIT_GUIDE.md`, `profile/DELEGATION.md`, `profile/AUTHORIZATION_TEMPLATE.md`, `profile/WORKSPACE_STANDARD.md` | `GUIDES_DIR/` |
| `profile/workspace-standard/` (the helper script and its templates) | `GUIDES_DIR/workspace-standard/`. The templates contain `{{GUIDES_DIR}}` too: replace it there as well, or every project the helper creates later will carry the literal placeholder. |

- For "guides only", tell the user their global rules do not point to the guides yet, and offer the one line they can add later.
- If the user chose a reply language other than Chinese, change "Talk to the user in plain Chinese" in the installed `AGENTS.md` accordingly, and tell them `REPLY_STYLE.md` is written in Chinese.
- If the user gave a research field, append to the installed `AGENTS.md` a section `## About the user` with their line as a single bullet.
- Check the helper runs: `python GUIDES_DIR/workspace-standard/workspace.py --help` (or `python3`).

## Step 5 — Codex (skip if not in use)

- Copy `codex/agents/*.toml` into `<Codex home>/agents/` with the placeholders replaced. If an existing file there has the same `name`, ask before replacing it.
- The role files name the author's models: `gpt-5.6-luna`, `gpt-5.6-terra` and `gpt-6-astra`. Find which models the user's Codex offers (the model list in the app, or the `/model` command). Replace any missing one with the closest tier — small and fast, balanced, or strongest — and tell the user what you chose.
- Merge `codex/config-snippet.toml` into `<Codex home>/config.toml`: add only its one key, inside the existing `[agents]` table if there is one.
- Tell the user to restart Codex if it is running, so the new rules and roles load.

## Step 6 — Claude Code (skip if not in use)

- Put `claude/GLOBAL_CLAUDE.md` into `~/.claude/CLAUDE.md` as the user chose in step 2, with `{{GUIDES_IMPORT}}` replaced. For "merge", append the import line and the "Claude Code additions" section to the end of their file.
- Copy `claude/agents/*.md` into `~/.claude/agents/`. If an existing agent has the same `name`, ask before replacing it.
- New sessions load the result; the `/memory` command in Claude Code shows which files were loaded.

## Step 7 — Skills (only what the user picks)

- Read `skills/CATALOG.md` and present it to the user as a short Chinese list, grouped as in the catalog, one line per skill.
- Ask which ones to install, for which tool, and where: every project (user level) or one project (ask for its path).
- Install each one from its source as the catalog says, keep its LICENSE when it has one, and delete temporary clones. The install location is always the one from the catalog's table, even when the upstream README names another folder. Never copy Anthropic's docx, pdf, pptx or xlsx skills; install those only through the plugin named in the catalog.
- If one fails, skip it, finish the rest, and report the failure with its reason.

## Step 8 — Verify and report

- Confirm that no `{{` placeholder remains in any installed file.
- Codex: in a new session, ask it to list the custom subagent roles it can spawn; `luna_clerk`, `terra_worker`, `critical_reviewer` and `professional_reviewer` should appear.
- Claude Code: in a new session, ask which subagents are available; `luna_clerk`, `terra_worker` and `critical_reviewer` should appear.
- Report to the user in Chinese: what was installed where, the backups, which model each Codex role uses, which skills were installed, and how to undo (restore the `.bak-*` files and delete the installed files). Suggest a first try: open a project folder and say “按工作区规范初始化这个项目”.

## Updating later

Pull the latest version of this repository and repeat steps 4 to 6. Compare each installed file with the new version first; if the user has edited an installed file, show the differences and ask before replacing it.
