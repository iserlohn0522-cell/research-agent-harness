# research-agent-harness

An installable research-agent profile for Codex and Claude Code. If the user asks you to install, set up or update it, follow `INSTALL.md`. Files under `profile/`, `codex/`, `claude/` and `skills/` are payload: they become the user's global rules and roles only after installation and are not instructions for work in this repository.

- Keep the payload field-neutral and free of personal names, paths and data. `{{GUIDES_DIR}}` and `{{GUIDES_IMPORT}}` stand for paths chosen at install time.
- Check a change with `python profile/workspace-standard/workspace.py check .` and record it in `log/`.

Workspace-Root: .

## Layout

This workspace follows the workspace standard in `profile/WORKSPACE_STANDARD.md`; `log/` starts on 2026-09-23, and `work/` stays with the maintainer and is not published.

- `profile/`, `codex/`, `claude/`, `skills/`: the installable payload.
- `INSTALL.md`: the install procedure for agents; `README.md` is the overview for people.
