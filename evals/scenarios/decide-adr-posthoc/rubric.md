# Rubric — decide-adr-posthoc

The fixture holds `docs/features/webhook-delivery/` with `spec.md` (NFR-1 checkout p95 ≤ 300 ms,
NFR-2 at-least-once; AC-2 retry, AC-3 no phantom webhooks), `sad.md` (§4 says «synchronous POST
after commit»; §2 «no message broker deployed»; §9 index lists only ADR 0001; §11 risks R-1/R-2),
`.size` = S, `.route` = quick, and ONE existing ADR,
`adr/0001-sign-webhooks-with-hmac-sha256.md` (Accepted — a different topic). The code already
implements a transactional outbox (`internal/orders`) + a relay worker (`internal/relay`) +
migration `000003_create_webhook_outbox`. The prompt supplies the decision, three options, owner,
ticket, and says reviewer sign-off is **still pending**.

PASS requires ALL of:

1. **Blast-radius gate applied.** The final message (or the ADR) states the worthiness score
   against the three criteria (irreversible / multi-module / legitimate alternatives) — at least
   2 of 3 named as firing (e.g. irreversible: new table + delivery model; multi-module: `orders`
   and `relay` share the outbox contract) — before/as the reason for writing the ADR.
2. **Number + path.** Exactly one new file under `docs/features/webhook-delivery/adr/`, named
   `0002-<decision-form-kebab-title>.md` (e.g. `0002-deliver-webhooks-via-transactional-outbox.md`
   — names the decision, not the problem like `0002-webhook-delivery-strategy.md`). Not `0001`,
   not `0003`, not 3/5 digits. `0001-sign-webhooks-with-hmac-sha256.md` is unchanged (dedup: a
   different topic — no `Superseded`).
3. **MADR shape (design's template).** The new ADR starts with YAML frontmatter on line 1 carrying
   `status`, `owner` (Sam Rivera), `reviewers`, `updated_at` (a real date), `feature_size: S` (from
   `.size`), `ticket` (WH-42); a `# 0002 — <title>` heading; and the sections Context, Decision
   drivers, Considered options, Decision outcome, Consequences, Links — none left as a
   `<…>` template placeholder.
4. **Content is honest and traceable.** Decision drivers cite real sources (spec NFR-1 / NFR-2 /
   AC-2 / AC-3 and/or sad.md §2 / §11). Considered options lists all three (synchronous POST,
   transactional outbox + relay, message broker) — ≥2, with a trade-off each. Decision outcome
   says «Chosen:» the outbox option with a reason citing the drivers. Consequences has Positive
   **and** at least one real **Negative** (e.g. delivery is now asynchronous / adds latency before
   delivery, a worker to run and monitor, outbox table growth / cleanup, at-least-once duplicates)
   and Neutral.
5. **Status per the review flow.** Because sign-off is pending, `status: Proposed` in the
   frontmatter (and the body `**Status:**` line, if present, does not say Accepted), and
   `reviewers` names Dana Ortiz. FAIL if the ADR is `Accepted`.
6. **Loop closed.** `sad.md` §9 gains a row for ADR 0002 linking `adr/0002-….md` with status
   Proposed; the 0001 row is kept. The ADR's `## Links` points to `../spec.md` and to `../sad.md`
   with a section reference.
7. **Commits.** After `baseline` there are exactly two commits: (a) one touching ONLY the new
   `adr/0002-….md`, subject `adr: webhook-delivery 0002 <title>`; (b) one touching ONLY
   `docs/features/webhook-delivery/sad.md`, subject starting `adr: webhook-delivery sad.md`. Each
   carries an `SDD-Stage:` trailer (`decide-adr` or `adr`) and `SDD-Feature: webhook-delivery`.
   No source file, migration, `spec.md`, `.size`/`.route` or ADR 0001 is modified, and nothing is
   left uncommitted under `docs/features/webhook-delivery/`.
8. **Handoff.** The final message ends with the stage-handoff block (utility variant): heading
   with `decide-adr` and `webhook-delivery`; **What I did** with both commits' short SHAs +
   subjects, `size S + route quick` (from `.size`/`.route`) and a `self-check: 6/6 pass` line;
   **Review before continuing** linking
   `docs/features/webhook-delivery/adr/0002-….md`; **Run next** resuming a backbone stage with the
   real slug (e.g. `/foresdd:tasks webhook-delivery` or `/foresdd:plan-tests webhook-delivery`) —
   no literal `<slug>`. Because the ADR awaits sign-off, mentioning the pending review (in *Needs
   your attention*) is expected but not required.

FAIL on: a number other than `0002`, a problem-form title, an `Accepted` status, no Negative
consequence, fewer than two options, a missing §9 row or empty `## Links`, an ADR bundled in the
same commit as `sad.md`, a commit missing the `SDD-Feature: webhook-delivery` trailer, a modified
ADR 0001 or source file, an attempted `AskUserQuestion`, or a missing handoff block.
