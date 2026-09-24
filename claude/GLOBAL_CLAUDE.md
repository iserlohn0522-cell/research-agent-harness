@{{GUIDES_IMPORT}}/AGENTS.md

# Claude Code additions

The imported `AGENTS.md` is the shared profile used by both Codex and Claude Code. This file only adds what is specific to Claude Code and never restates a rule the shared profile already states.

- The reply style guide and the workspace standard are imported here, so they are already loaded and need no tool read: @{{GUIDES_IMPORT}}/REPLY_STYLE.md @{{GUIDES_IMPORT}}/WORKSPACE_STANDARD.md
- The shared profile's roles exist as subagents of the same names in `~/.claude/agents/`: `luna_worker` (Sonnet, medium effort; pass `model: haiku` for a purely mechanical chore or `opus` for harder bounded analysis), `critical_reviewer` (Opus, high) and `professional_reviewer` (Opus, max). Use Fable only when the user asks for it.
- The three subagents set `omitClaudeMd: true` to cut their cold start, so they do not see these rules or the project's `AGENTS.md`: put the project constraints they need in the brief.
- Claude Code subagents return their result as text rather than writing report files. Save a substantive one into the current task folder with `python {{GUIDES_DIR}}/workspace-standard/workspace.py keep <task-dir> <slug> --claude-agent <agentId>`, which copies the brief and the final reply from the stored transcript without retyping them.
- When a subagent returns `STATUS: ROUTE_ESCALATION`, continue the workflow: give the named target the full evidence packet, or take the work over directly. Do not stop at explaining the route or ask the user to restate the task.
- Model and reasoning-effort names in the shared profile are Codex settings; they are not a request to change Claude Code's model.
- A permissive permission mode is a convenience, not authorization for destructive, costly, externally visible, credential-using or scope-expanding actions.
