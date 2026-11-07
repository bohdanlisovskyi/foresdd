# Fallbacks — when a Claude Code mechanism isn't available in the session

> **Reference-only.** Not a skill. The skills are written against Claude Code's mechanisms
> (`/foresdd:<name>` invocation, `AskUserQuestion`, named plugin subagents, `TeamCreate` /
> `Workflow`, the native task list, design-tool MCPs). Not every session has every one of them —
> a headless run, a plan without a model tier, an MCP that isn't connected. This file is the single
> table of what each stage does instead.

## The table

| Mechanism (as written in the skills) | Normal | When it's unavailable in this session |
|---|---|---|
| Ask the user (`AskUserQuestion`) | the native tool | numbered questions in plain text — **stop and wait** for the answer, never assume one. A non-interactive/headless run (no human can answer) stops before any write — see *Interview interaction exception* |
| Spawn a subagent (`subagent_type: "foresdd:researcher"`) | the named plugin agent | the documented fallback (usually `general-purpose` with the same prompt), or run the agent file's instructions **inline** — an inline run is a self-check, never an independent clean-context critique; name it as such in the handoff |
| `TeamCreate` / `Workflow` (the `implement` engine modes) | native | sequential single-agent TDD — the documented fallback floor |
| `model:` / `effort:` / `judgment_model` tier | honored | retry the dispatch once on `model: inherit` and continue — canonical in [`agent-roster.md`](./agent-roster.md) §Model availability |
| Native task list (`TaskCreate` / `TaskUpdate` — `implement` mirrors task status into it) | the native tools **when the session has them** (newer models expose them only with `CLAUDE_CODE_ENABLE_TODO_TOOLS`) | skip silently; `tasks/tracker.md` + `tasks.json` stay the source of truth |
| Design-tool MCP (Figma / Pencil — used by `design-system` / `screens`) | the session's connected Figma / Pencil MCP tools, per the committed `docs/design-system.md` `tool` choice. ⚠ Pencil MCP writes into the app's **active document** and ignores `filePath` — verify identity via `get_app_state` before any write, and only the user's Cmd+S persists to disk | **`code` mode**: inline markdown wireframes in `screens.md` + a **named degradation** — frontmatter `tool: code` + `degraded_from: <canon tool>`, one line in the manifest §Source and the handoff — never a blocked stage |
| Fresh context between stages | `/clear` | — (always available; recommended, never required — see [`handover.md`](./handover.md)) |

## Interview interaction exception

`interview` detects the **actual available question channel**. Use `AskUserQuestion` if present;
otherwise ask in plain text and wait. Decision questions may have options; factual questions may
be open text. Follow its adaptive exception in [`style.md`](./style.md). A non-interactive/headless
run stops before writes or helpers; a missing `AskUserQuestion` alone does not mean no human can
answer. Inline helper fallback is a self-check, never an independent clean-context critique.

## The rule

When a mechanism is unavailable, **degrade to the fallback in the table — never block the stage**
on a missing session feature. Every degradation is named out loud in the stage-handoff block's
*Needs your attention* section ([`handover.md`](./handover.md)), so the user knows what ran in a
weaker form.
