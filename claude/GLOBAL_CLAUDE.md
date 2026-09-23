@{{GUIDES_IMPORT}}/AGENTS.md

# Claude Code additions

The imported `AGENTS.md` is the shared profile used by both Codex and Claude Code. This file only adds what is specific to Claude Code and never restates a rule the shared profile already states.

- The reply style guide and the workspace standard are imported here, so they are already loaded and need no tool read: @{{GUIDES_IMPORT}}/REPLY_STYLE.md @{{GUIDES_IMPORT}}/WORKSPACE_STANDARD.md
- The shared profile's roles map to these subagents in `~/.claude/agents/`: `luna_clerk` (haiku), `terra_worker` (sonnet) and `critical_reviewer` (opus), which also takes the work the profile gives `professional_reviewer`.
- When a subagent returns `STATUS: ROUTE_ESCALATION`, continue the workflow: give the named target the full evidence packet, or take the work over directly. Do not stop at explaining the route or ask the user to restate the task.
- Model and reasoning-effort names in the shared profile are Codex settings; they are not a request to change Claude Code's model.
- A permissive permission mode is a convenience, not authorization for destructive, costly, externally visible, credential-using or scope-expanding actions.
