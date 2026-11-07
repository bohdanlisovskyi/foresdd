---
id: T2
title: Enforce the 2-renewal cap with ErrRenewalLimit
layer: domain
deps: [T1]
acs: [AC-02]
files_hint: [internal/loan/loan.go, internal/loan/loan_test.go]
status: todo
step: SELECT
---

# T2 — Enforce the 2-renewal cap with ErrRenewalLimit

## Acceptance criteria

- AC-02 (spec §5): renewing a loan already renewed 2 times is rejected with the renewal-limit
  outcome and the due date is unchanged.

## Data delta

none.

## API contract

none.

## Definition of done

Renewing a loan with `Renewals == 2` returns `ErrRenewalLimit` and leaves `DueAt` unchanged; a
unit test covers it.
