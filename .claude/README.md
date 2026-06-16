# .claude/

This folder holds Claude Code configuration scoped to the A-Eye repo.

- **Project context for AI sessions lives in [`../CLAUDE.md`](../CLAUDE.md)** — that file is
  auto-loaded by Claude Code at the start of every session. Edit it there, not here.
- This folder is where repo-scoped Claude settings, custom slash-commands, and agents will go
  as the project grows:
  - `settings.json` — shared, committed settings (permissions, env).
  - `settings.local.json` — personal overrides (gitignored).
  - `commands/` — project slash-commands.
  - `agents/` — project subagent definitions.

Nothing required here yet; `CLAUDE.md` is the single source of truth for project context.
