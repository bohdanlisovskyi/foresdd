---
status: current
mode: current
updated_at: "2026-11-01"
reflects_commit: "baseline"
language: "go 1.22"
build_cmd: "go build ./..."
test_cmd: "go test ./..."
lint_cmd: "golangci-lint run ./..."
migration_tool: "golang-migrate"
frontend: ""
---

# Architecture map — stockroom

## Stack

- Language / runtime: Go 1.22 (`go.mod`); Postgres via `database/sql` (`internal/platform/db/db.go`).
- Build / test / lint: `make build` · `make test` · `make lint` (`Makefile`).

## Module inventory

| Module | Responsibility | Entry points |
|---|---|---|
| `internal/orders` | take an order for a SKU and quantity | `handler.go` (HTTP), `service.go` `Place` |
| `internal/inventory` | own stock levels; reserve stock for an order | `service.go` `Reserve` (called in-process by orders) |
| `internal/platform/apperr` | the one cross-module error type | `apperr.E(kind, …)` |
| `cmd/server` | wiring | `main.go` |

## Conventions

- Errors: modules return `apperr.E(kind, …)`; the handler maps kinds to responses (`internal/orders/handler.go`).
- Tests: table-driven unit tests with hand-written fakes, no DB (`internal/orders/service_test.go`).
- Migrations: golang-migrate pairs in `migrations/`.

## Frontend / UI foundation

N/A — no frontend.
