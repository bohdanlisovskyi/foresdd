<!-- PR body scaffold. Forge-agnostic — same body for `gh pr create --body-file` or `glab mr create --description`. -->

## Summary

<1–3 sentences: what this PR ships and why. Link [spec](docs/features/<slug>/spec.md).>

## Acceptance criteria

<the AC this PR satisfies, each one line — the reviewer checks these against the diff>

- AC-01 — <business outcome> ✓
- AC-0N — <business outcome> ✓

## Design

- Spec: `docs/features/<slug>/spec.md`
- Architecture: `docs/features/<slug>/sad.md`
- Decisions: `docs/features/<slug>/adr/`
- Data model + migration: `docs/features/<slug>/data-model.md` (migration `<NNNN>`)
- API: `docs/features/<slug>/contracts/openapi.yaml`

## Review

- Review record: `docs/features/<slug>/_review/review-<date>.md` — <PASS (full | delta)>
- Fixes since review / during the feature: <`_fixes/<date>-<short>.md` — one line each>, or none.
- <only when applicable: ⚠ shipped without a PASS review — <reason> · ⚠ unreviewed commits after the review: <sha list>>

## Tasks (SDD-Task / SDD-Fix trailers)

<the per-task and fix commits — `git log --grep 'SDD-Task\|SDD-Fix'`>

## Verification

- Unit: <result>
- Integration: <result, or "CI — Docker-backed">
- Lint + vet: <result>
- Ran the feature: <per spot-checked AC — «AC-NN: <action> → <observed>», or what was deferred and why>

## Operational notes

- Migration: <run-on-deploy + rollback>, or none.
- Feature flag / config: <any>, or none.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
