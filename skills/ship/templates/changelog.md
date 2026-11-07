# Changelog — <slug>

<!-- instruction: written to docs/features/<slug>/changelog.md (links below are relative to that
folder). If the repo has a root CHANGELOG.md, ship ALSO adds one line there in that file's own
format, linking back here — never create a root changelog the repo doesn't have.
What changed + why, not a file list. Link the spec and the load-bearing ADRs.
Include the operational note (migrations, feature flags) the deployer needs. Keep it readable by
someone who didn't write the feature. -->

## <slug> — <one-line summary>

**What:** <the user-facing capability that now exists, in plain language>.

**Why:** <the problem it solves — link [spec](./spec.md) §1/§2; cite the key decision(s) — [ADR-NNNN](./adr/<NNNN-title>.md)>.

**How to use:** <the endpoint/flow + an example, from [openapi.yaml](./contracts/openapi.yaml)>.

**Operational notes:**
- Migration: <e.g. "adds 000023_create_notification_preferences — applied on deploy; reverts cleanly">, or `<!-- none -->`.
- Feature flag / config: <any>, or `<!-- none -->`.
- Rollback: <how to back out — usually `migrate down` + revert the deploy>.
- Review: <PASS — [review-<date>](./_review/review-<date>.md)>, or «⚠ shipped without a PASS review — <reason>».

**Acceptance criteria delivered:** <AC-01 … AC-NN — the business outcomes now guaranteed>.
