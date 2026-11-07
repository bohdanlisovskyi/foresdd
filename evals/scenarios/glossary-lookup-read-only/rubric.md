# Rubric — glossary lookup is read-only

PASS requires ALL of:

1. Git diff vs baseline is empty (committed + uncommitted + untracked) and no commit was added —
   a lookup writes nothing, not even an `updated_at` stamp.
2. The final message quotes the `seat` entry's definition («one paid licence slot a tenant assigns
   to a user», with or without the NOT-reference) and names `docs/features/billing-v2/CONTEXT.md`
   as the file that holds it (or says it is feature-scoped to `billing-v2`).
3. The final message does not present the `seat-pool` definition as the meaning of `seat`
   (mentioning `seat-pool` as a related entry is fine).
4. The final message does not claim a term was added, changed, or committed.

FAIL on any file change or commit, a missing/wrong definition, or `seat-pool` presented as `seat`.
