# Rubric — screens-pencil-degraded

Same `saved-searches` feature as `screens-code-mode`, but the committed canon says `tool: pencil`
(`pen_file: docs/design/library.pen`, present in the fixture) and the session has no Pencil MCP.
A correct headless run (`--depth=easy`) **degrades to code mode and records that honestly** — it
neither blocks nor pretends it drew in Pencil.

PASS requires ALL of:

1. `docs/features/saved-searches/screens.md` exists and its frontmatter records the mode actually
   used: `tool: code` **and** `degraded_from: pencil`. (`tool: pencil` with ASCII wireframes is a
   FAIL.)
2. The manifest's Source section names the degradation (pencil → code because the Pencil MCP was
   unavailable).
3. One `### SCR-NN` section for each of SCR-01, SCR-02, SCR-03, each with `default` plus at least
   one `error` or `empty` state (or an explicit `N/A: <reason>` row), and inline ```` ```text ````
   wireframes are present.
4. No `.pen` file was created or modified: `docs/features/saved-searches/screens.pen` does not
   exist, and `docs/design/library.pen` is byte-identical to the fixture.
5. The run did not refuse or stop over the missing tool, and `docs/design-system.md` is unchanged
   (the canon's tool choice is not rewritten by a per-feature run).
6. The run committed `screens.md` (a commit whose subject starts `screens:`), and the final message
   contains the stage-handoff block that names the degradation and forwards to
   `/foresdd:tasks saved-searches`.

FAIL on: a refusal, an attempted `AskUserQuestion` or Pencil/Figma tool call, `tool: pencil` in the
manifest, a missing `degraded_from`, any `.pen` change, an edited design-system.md, or a handoff
that omits the degradation.
