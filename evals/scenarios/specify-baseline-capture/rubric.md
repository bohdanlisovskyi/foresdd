# Rubric — specify-baseline-capture

The fixture is the small Go service `stockroom` (same tree as `survey-brownfield-map`) plus a
current `docs/architecture-map.md` and a root `CONTEXT.md` (roles/terms: Buyer, Order,
Reservation, SKU). The orders area today: `internal/orders/service.go` `Place` rejects a quantity
≤ 0 (line ~33), asks inventory to reserve stock (line ~36; `internal/inventory/service.go`
returns an insufficient-stock error at line ~23–24 when stock is short), then records the order
with an app-generated id (line ~38–40). `internal/orders/service_test.go` pins the
positive-quantity and zero-quantity cases; nothing pins the insufficient-stock case. There is
**no** permission/ownership check anywhere. A correct headless run takes **baseline mode** with
every rule confirmed «Intended».

PASS requires ALL of:

1. `docs/features/orders/spec.md` exists with frontmatter `kind: baseline` and `status: Baseline`,
   and follows the baseline template's shape (§1–§8 plus a **§9 Evidence** table).
2. §5 holds observed ACs for at least: (a) a valid order is recorded and confirmed (happy),
   (b) a non-positive quantity is rejected with a plain-language reason (error), and (c) an order
   is refused when inventory cannot reserve the stock (cross-context). Each AC heading carries a
   coverage-type word and `observed`. Roles/terms use the glossary (Buyer, Order, SKU,
   Reservation) — no invented `user`/`admin`.
3. **No invented behaviour:** there is **no** authorization AC (the code has no permission check);
   instead §8 (or §6.1 plus a §8 row) records the missing authorization check as a finding with an
   owner and a due. No AC describes behaviour absent from the code (e.g. cancellation, stock
   release, rate limits). §6 sets no invented numeric targets (`N/A` or only numbers the code fixes).
4. §5 contains **no forbidden tokens**: no HTTP verbs, no URL paths (e.g. `/orders`), no status
   numerics (400/409/201/500), no error-code strings (e.g. `insufficient_stock`), no JSON, no SQL,
   and no file paths (evidence belongs in §9).
5. §9 has one row per §5 AC with a real `file:line` anchor that exists in the fixture
   (`internal/orders/service.go`, `internal/inventory/service.go`); the quantity ACs cite
   `internal/orders/service_test.go` as «Pinned by»; the insufficient-stock AC is `unpinned`.
   No anchor names a file that does not exist.
6. **No backbone artifacts:** no `docs/features/orders/.size` or `.route`, no `sad.md`,
   `tasks.json`, `test-plan.md`; nothing under `cmd/`, `internal/`, `migrations/`, `Makefile`,
   `go.mod` was modified; no `docs/roadmap.md` was created.
7. **Commits:** after `baseline`, the spec is committed with subject `specify: orders baseline
   spec.md` (or `specify: orders spec.md`) carrying trailers `SDD-Stage: specify` and
   `SDD-Feature: orders`; a `CONTEXT.md` commit is allowed only if the glossary changed; no commit
   touches files outside `docs/features/orders/`, `CONTEXT.md`, `docs/features/orders/CONTEXT.md`
   or `.gitignore`; nothing under `docs/features/orders/` is left uncommitted. `.claude/sdd.local.md`
   is not tracked.
8. The final message ends with the stage-handoff block: **What I did** (area, counts of US/AC,
   how many unpinned, the coverage gap, the commit SHAs), **Needs your attention** (the unpinned
   insufficient-stock AC and the missing authorization check), **Review before continuing**
   (links `docs/features/orders/spec.md`), and **Run next** = `/clear` then
   `/foresdd:specify orders-cancel` (a `/foresdd:fix` alternative line is allowed). Run next must
   NOT be `/foresdd:design orders` or `/foresdd:clarify orders`.

FAIL on: a normal (non-baseline) spec, an invented authorization AC, an AC with no evidence row,
a forbidden token or file path in §5, a `.size`/`.route` file, a modified source file, a missing
`SDD-Stage`/`SDD-Feature` trailer, an attempted `AskUserQuestion`, or a missing handoff block.
