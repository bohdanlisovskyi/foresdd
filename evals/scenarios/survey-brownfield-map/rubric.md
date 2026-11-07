# Rubric — survey-brownfield-map

The fixture is a small existing Go service (`example.com/stockroom`, go 1.22): `cmd/server/main.go`
wires two modules — `internal/orders` (handler / service / repo + a table-driven
`service_test.go` with hand-written fakes) and `internal/inventory` (service / repo) — plus shared
`internal/platform/db` and `internal/platform/apperr` (the one cross-module error type,
`apperr.E(kind, …)`). `orders` calls `inventory.Reserve` directly in-process. Postgres via
`database/sql`. `migrations/` holds golang-migrate pairs `00000N_name.up.sql` / `.down.sql`; the
`Makefile` has `build` (`go build ./...`), `test` (`go test ./...`), `lint`
(`golangci-lint run ./...`) and `migrate` (`migrate -path migrations …`). No frontend, no authored
architecture doc, no idea brief, no roadmap. A correct headless run takes the **brownfield** path
with the owner confirm pre-answered «Looks right».

PASS requires ALL of:

1. `docs/architecture-map.md` exists in the template's shape: YAML frontmatter with `mode: current`
   (NOT `greenfield-bootstrap`), `updated_at`, `reflects_commit`, and the machine keys `language`,
   `build_cmd`, `test_cmd`, `lint_cmd`, `migration_tool`, `frontend`; body sections Stack,
   C4 — system as it is (a ```mermaid C4 block), Module inventory (table), Conventions, Datastores,
   Frontend / UI foundation, Where things live / closest precedents, Constraints & known tech-debt,
   Reconciliation with the authored architecture doc.
2. `reflects_commit` equals (or is a prefix-compatible short form of) the SHA of the fixture
   `baseline` commit shown in the git log — the map reflects the code as it was surveyed.
3. Machine keys are evidence-backed, never guessed: `language` names Go (1.22); `test_cmd` is
   `go test ./...` or `make test`; `lint_cmd` is a `golangci-lint` command or `make lint`;
   `migration_tool` names golang-migrate (or `migrate`); `build_cmd` is `go build ./...` /
   `make build` or `""`; `frontend` is `""`. No key names a tool absent from the fixture
   (e.g. no npm, pytest, alembic, goose, Flyway, React).
4. The Module inventory names the real modules — at least `internal/orders` and
   `internal/inventory` (and the shared `internal/platform/…` packages and/or `cmd/server` as
   wiring) — and contains **no** module/path that does not exist in the fixture tree.
5. Conventions cite real files from the fixture for at least: error handling
   (`internal/platform/apperr/apperr.go`), migrations (`migrations/` golang-migrate up/down naming),
   tests (`internal/orders/service_test.go` — table-driven, fakes), and module wiring /
   inter-module communication (`cmd/server/main.go` and/or the direct `inventory.Reserve` call).
   Every cited path exists in the tree.
6. The Frontend / UI foundation section is marked N/A (no frontend) — not filled with invented UI.
7. **No greenfield artifacts:** no `docs/features/_scaffold/tasks.json`, no `docs/adr/` files, no
   new source/skeleton files; nothing under `cmd/`, `internal/`, `migrations/`, `Makefile`,
   `go.mod` was modified.
8. **Commit:** after `baseline` there is exactly one commit; its subject starts with
   `survey: architecture-map.md`; it carries the trailer `SDD-Stage: survey` and NO
   `SDD-Feature` trailer (repo-level document); it touches `docs/architecture-map.md` and, at
   most, `.gitignore` (the settings-file patch rides in the first commit). `.claude/sdd.local.md`
   is NOT tracked, and if `.gitignore` changed it contains `.claude/*.local.md` and `.worktrees/`
   and still contains `/bin/`.
9. The final message contains a prose summary of the map (stack, modules, key conventions) and
   ends with the stage-handoff block — **What I did** (the commit's short SHA + subject, the scan
   mode `full`, and a `self-check: N/N pass` line), **Review before continuing** (links
   `docs/architecture-map.md`), **Run next** with `/clear` then `/foresdd:specify <slug>` (an
   `/foresdd:interview` skip line is allowed). No pipeline trail is required (repo-level). Run next
   must NOT be `/foresdd:scaffold` or `/foresdd:roadmap`.

FAIL on: `mode: greenfield-bootstrap`, a scaffold `tasks.json` or foundational ADRs, a missing or
wrong `reflects_commit`, a guessed machine key or an invented module/path, a modified source file,
more than one commit or a commit missing `SDD-Stage: survey`, a tracked settings file, an attempted
`AskUserQuestion`, or a missing handoff block.
