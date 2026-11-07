# Rubric — config targeted change writes one key without the interview

PASS requires ALL of:

1. `.claude/sdd.local.md` exists, its YAML frontmatter parses, and `interview_depth` is `hard`.
2. Every other key in the frontmatter holds the documented default from
   `skills/allocations/settings-file.md` (keys commented out there are still commented out) — the
   targeted run changed exactly one value.
3. `.gitignore` still contains `node_modules/` and now contains `.claude/*.local.md` and
   `.worktrees/`, each exactly once.
4. No file other than `.claude/sdd.local.md` and `.gitignore` was created or modified. If a commit
   was made, there is exactly one, it touches only `.gitignore`, and `.claude/sdd.local.md` is not
   tracked.
5. The final message shows the change as `old → new` for `interview_depth` (e.g.
   `medium → hard`), and contains a stage-handoff block (What I did / Review / Run next).
6. The final message does not claim the other setting groups were asked or chosen by the user.

FAIL on a second changed value, a tracked settings file, a missing `.gitignore` entry, or no
handoff block.
