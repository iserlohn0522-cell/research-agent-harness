@{{GUIDES_IMPORT}}/AGENTS.md

# Claude Code additions

The imported `AGENTS.md` is the shared profile used by both Codex and Claude Code. This section only adds what is specific to Claude Code.

- The reply style guide is imported because nearly every session reports to the user: @{{GUIDES_IMPORT}}/REPLY_STYLE.md
- The shared profile's roles exist as subagents of the same names in `~/.claude/agents/`: `luna_worker` (Sonnet, medium effort; pass `model: haiku` for a purely mechanical chore or `opus` for harder bounded analysis), `critical_reviewer` (Opus, high) and `professional_reviewer` (Opus, max).
- They skip CLAUDE.md files, so the brief carries the project constraints they need.
- They return text: save a substantive reply with `python {{GUIDES_DIR}}/workspace-standard/workspace.py keep <task-dir> <slug> --claude-agent <agentId>`.
- On `STATUS: ROUTE_ESCALATION`, pass the evidence packet to the named target or take the work over; do not stop to explain the route or ask the user to restate the task.
- A permissive permission mode is a convenience, not authorization for destructive, costly, externally visible, credential-using or scope-expanding actions.
