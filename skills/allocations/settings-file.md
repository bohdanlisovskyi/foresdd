# The settings file — `.claude/sdd.local.md`

> **Reference-only.** Not a skill. Every skill that ensures, reads or edits the per-project
> settings file reads this. The template below is written **verbatim** — the frontmatter between
> `---` fences at the top of the file, the «What each key does» section as its body — so the file
> explains itself without opening the plugin docs. The engine-side delta (which keys `implement`
> actually reads, model precedence, `.size` scaling) stays in
> [`../implement/references/settings.md`](../implement/references/settings.md).

## Who creates it, who changes it, who reads it

| Role | Who | What they do with it |
|---|---|---|
| **Create** (unconditional, idempotent) | the six pipeline skills — `interview` · `survey` · `roadmap` · `scaffold` · `specify` · `implement` — **and `config` itself** | first protocol step: absent → write the template below + patch `.gitignore`; present → read, never overwrite. `interview` defers creation to its final write point after real answers; outside a repo, in Plan Mode, or headless it writes nothing, settings included. |
| **Change values** (the only writer of existing keys) | [`config`](../config/SKILL.md) | asks, then patches confirmed keys in place; also the only one that upgrades an older file (§ «Upgrading an older file»). No other skill ever offers to tune a value. |
| **Read** `interview_depth` | `interview` · `specify` · `clarify` · `design` · `ux-flows` · `sequences` · `screens` | question ceiling in `interview`; for a feature with no `docs/features/<slug>/.depth` yet, pre-selects the one depth question (`specify` / `clarify` / `design` / `ux-flows`) or is used directly (`sequences` / `screens`) → [`interview-depth.md`](./interview-depth.md) |
| **Read** `judgment_model` / `model_<role>` / `effort_<role>` | every skill that dispatches an agent | the tier each agent runs at → [`agent-roster.md`](./agent-roster.md) |
| **Read** the engine keys (`tdd`, `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation`, `stop_on_red`, `max_red_retries`, `gate_*`, `require_integration`, `auto_commit`, `branch_strategy`, `cmd_*`) | `implement` (`cmd_*` + gates also `fix`) | → [`../implement/references/settings.md`](../implement/references/settings.md) |
| **Read** `auto_commit` | every skill that writes a document | `off` → no commits, the handoff prints the commands → [`write-and-commit.md`](./write-and-commit.md) |

## Create when absent (the procedure)

Run this **first thing in the skill's protocol, after that skill's own gate**, except `interview`,
which reads settings first and creates them only at its final authorized brief-write point.
`scaffold` clears its hard refuse and `implement` its preconditions first, so a refusal leaves
the repo untouched; other skills with no preceding gate simply run it first. It is unconditional —
a settings file the user never asked for is strictly better than a stage that discovers it is
missing three commands later — and idempotent.

1. **`.claude/sdd.local.md` exists?** → read it and stop here. **Never** overwrite, never
   regenerate it from this template, never «refresh» it because a key looks stale or is missing —
   adding keys to an existing file is `config`'s upgrade step, not a reader's.
2. **Absent** → write it: a `---` line, the documented frontmatter below, a closing `---` line,
   then the «What each key does» section as the file's markdown body. Keep the group headers, the
   inline comments **and the commented-out keys** exactly as written — the comments carry the
   allowed values, and the commented-out keys are how the adaptive defaults stay adaptive.
3. **Patch `.gitignore`** (create it if absent) so it contains `.claude/*.local.md` and
   `.worktrees/` — both are per-developer and must never be committed. The `.claude/*.local.md`
   glob already covers `sdd.local.md`; don't add a redundant explicit line, and don't duplicate a
   line that is already there.
4. **Say this one line** (only when you actually created the file) and move on — no question, no menu:
   «`.claude/sdd.local.md` created with defaults — a commit after every task, medium-depth
   interviews; `/foresdd:config` to tune». It names the two defaults a new user is most likely to
   be surprised by: commits appearing on their own, and how many questions to expect.

The settings file itself is **never committed** (it's gitignored). The `.gitignore` patch is, and
rides along in the stage's first commit ([`write-and-commit.md`](./write-and-commit.md)).

## The documented frontmatter

<!-- This block is written verbatim between `---` fences at the top of `.claude/sdd.local.md`; the
     «What each key does» section below becomes the file's body. Keep the group headers, the inline
     comments (they list the allowed values) and the commented-out keys (they are the adaptive
     defaults — a written value would pin them). -->

```yaml
settings_version: 1        # schema version of this file — managed by /foresdd:config, don't edit by hand

# ── Interview ──────────────────────────────────────────────────────────────
interview_depth: medium    # easy | medium | hard — how many questions the Q&A skills ask you

# ── TDD & gates ────────────────────────────────────────────────────────────
tdd: true                  # true | false — write a failing test before the code
stop_on_red: true          # true | false — halt when a task stays red after retries (false = skip it, continue)
max_red_retries: 3         # integer ≥1 — attempts to turn a red test green before escalating
gate_lint: true            # true | false — run lint after every task
gate_vet: true             # true | false — run static analysis after every task
require_integration: auto  # auto | always | never — integration tests (auto = only when Docker answers)

# ── Execution ──────────────────────────────────────────────────────────────
team_mode: false           # true | false — run tasks as an agent team
workflow_mode: auto        # auto | off — parallelize a wide task graph with a Workflow
max_parallel_agents: 3     # integer ≥1 — agents at once (1 = strictly sequential)
isolation: worktree        # worktree | inplace — inplace forces one agent at a time

# ── Git ────────────────────────────────────────────────────────────────────
auto_commit: per_task      # per_task | per_phase | off — off = nothing is committed, commands are printed
branch_strategy: feature   # feature | current — where implement commits code

# ── Models — commented = adaptive default; uncomment a line to pin it ─────
# judgment_model: opus        # haiku | sonnet | opus | fable | inherit | <model id> — all 5 judgment agents
# model_test_author: sonnet   # same values — one role; wins over judgment_model
# model_implementer: sonnet
# model_reviewer: opus
# effort_test_author: medium  # low | medium | high | xhigh | max — unset = raised automatically on L/XL features
# effort_implementer: medium
# effort_reviewer: high

# ── Commands — empty = autodetect from the repo (recommended) ─────────────
cmd_test_unit: ""
cmd_test_integration: ""
cmd_lint: ""
cmd_vet: ""
```

**Why the model keys ship commented out.** Two rules only work while a key is **unset**: the
`judgment_model` floor (an unset key never runs judgment below a stronger session tier) and the
L/XL effort scaling (an explicit `effort_<role>` always wins over it). A per-role `model_reviewer`
also wins over `judgment_model` for the reviewer. Writing those values out would pin every new
file and silently switch both rules off, so the template documents the default as a comment and
leaves the key unset. A commented-out key reads exactly like a missing key: its documented default,
adaptive rules included.

## What each key does

<!-- Written verbatim as the file's body. Plain language for the person editing the file; links are
     absolute because the plugin's own files don't exist in the user's repo. -->

> This file is yours: edit it by hand or run `/foresdd:config`. Comments, key order and keys the
> plugin doesn't know are always kept. A missing or commented-out key means «use the default».
> Full docs: <https://github.com/bohdanlisovskyi/foresdd/tree/main/skills/allocations>

**Interview**

- **`interview_depth`** — `easy | medium | hard`, default `medium`. How much the question-asking
  skills (`specify`, `clarify`, `design`; also how `sequences` / `ux-flows` confirm diagrams) decide on
  their own and how much they ask you. `easy` asks only what it can't infer and lists its
  assumptions for you to veto; `hard` walks every decision. It only sets the default for **new**
  features — each feature is asked once and remembers its answer in `docs/features/<slug>/.depth`;
  say «deeper» / «faster» during a run, or pass `--depth=` for one run. Every acceptance criterion is still required at every depth. `interview`
  uses it as a question ceiling.

**TDD & gates**

- **`tdd`** — `true`: every task starts with a failing test, then the code that makes it pass.
  `false`: code is written straight away (you get a warning every run — the failing test is what
  proves the test really checks something).
- **`stop_on_red`** — `true`: a task whose test stays red after the retries stops the run.
  `false`: that task is dropped, the tasks that depend on it are blocked, everything else continues.
- **`max_red_retries`** — how many attempts to turn a red test green before escalating.
- **`gate_lint` / `gate_vet`** — run lint / static analysis after every task. Skipped quietly when
  the repo has no such command.
- **`require_integration`** — `auto`: run integration tests when a Docker daemon answers, otherwise
  skip them without failing. `always`: refuse to start without Docker. `never`: never run them.

**Execution**

- **`team_mode` / `workflow_mode`** — how `implement` runs the task graph. `team_mode: true` uses an
  agent team; `workflow_mode: auto` parallelizes a wide graph and runs a narrow one in sequence.
  When both could apply, `team_mode` wins. If the session lacks the tool, the run falls back to
  sequential.
- **`max_parallel_agents`** — the most agents running at once. `1` = strictly sequential.
- **`isolation`** — `worktree`: each parallel agent gets its own copy of the repo under
  `.worktrees/`. `inplace`: work happens in your checkout, one agent at a time.

**Git**

- **`auto_commit`** — `per_task` (default): a commit after each task, and one commit per document
  for the document stages. `per_phase`: code commits batched per dependency layer. `off`: nothing
  is committed — each stage prints the ready-to-run commit commands instead.
- **`branch_strategy`** — `feature`: `implement` moves onto a feature branch if you're on the
  default branch. `current`: it commits where you are. Document stages always commit on the
  current branch.

**Models** (commented out by default — uncomment a line to pin it)

- **`judgment_model`** — the model for all five agents that judge work: `reviewer`, `critic`,
  `devils-advocate`, `strategist`, `analyst`. Values: `haiku | sonnet | opus | fable`, `inherit`
  (the session's model), or a full model id. Unset = `opus`, **or your session's model when it is
  stronger** — judgment never runs below the session unless you pin it. Pin `sonnet` if your
  account has no Opus access. An unavailable model falls back to the session model once, without
  blocking.
- **`model_<role>`** — the model for one role (`test_author`, `implementer`, `reviewer`); wins over
  `judgment_model` for that role. Unset = the role's default shown in the comment.
- **`effort_<role>`** — how hard that role thinks: `low | medium | high | xhigh | max`. Unset = the
  role's default, raised automatically on large (L/XL) features; a pinned value is never raised.

**Commands**

- **`cmd_test_unit` / `cmd_test_integration` / `cmd_lint` / `cmd_vet`** — leave empty: the commands
  are detected from your Makefile, package scripts or language manifests. Fill one in only when
  detection gets it wrong — a pinned command is one more thing to keep in sync.

**Meta**

- **`settings_version`** — which version of this template the file follows. `/foresdd:config` uses
  it to offer keys added in later versions. Don't edit it.

## Editing an existing file (only `config` does this)

The file is the user's. It carries their edits, their comments, and possibly keys this version of
the plugin has never heard of. So:

- **Patch key by key.** Rewrite only the lines whose values the user just confirmed. Never
  regenerate the file from the template — that is how a hand-written comment or a hand-added key
  silently disappears.
- **Commented-out keys are edited in place.** Pinning a commented-out key = uncomment that line and
  set the value; returning a key to its adaptive default = comment the line back out (keep the
  value as the documented default). Never add a second, uncommented copy of a key below its
  commented one.
- **Preserve comments, group headers, key order, and unknown keys** exactly as they are. An unknown
  key is a forward-compatibility feature, not garbage to clean up.
- **Write each value in its documented form** — bare `off`, not `"off"`; bare `3`, not `"3"`. The
  template above is the reference spelling; a re-quoted value reads as a different setting on the
  next diff.
- **Show `old → new`** for every key you touch, and separately name anything that was **derived
  rather than asked** (a host clamp, an autodetect left empty, a key left on its adaptive default) —
  a value the user didn't choose must never appear as if they had.
- **A malformed frontmatter is never fixed silently.** Show what failed to parse and offer the
  choice: rewrite from the template (stating what will be lost) or stop and let the user fix it
  by hand.

## Upgrading an older file (only `config` does this)

A file with no `settings_version`, or an older one than the template, may lack keys added since.
Readers don't care — a missing key is its default — but the user can't see a key that isn't in
their file. So `config`, after reading the file:

1. **Lists what's missing** — every template key (commented or not) absent from the file, by group.
2. **Lists pinned defaults that switch off an adaptive rule** — an uncommented `judgment_model`,
   `model_reviewer` or `effort_<role>` whose value equals the documented default. In a file from
   before `settings_version: 1` these were written by the old template, not chosen by the user;
   they quietly disable the floor and the L/XL scaling.
3. **Offers both in one question**: append the missing keys (each under its group header, appending
   the header when the file has none, with its inline comment, commented out when the template
   has it commented out), comment out the pinned defaults, both, or neither. Then set
   `settings_version` to the template's — even on «neither», so the same offer isn't repeated.
   Everything else is patched per the rules above; nothing is reordered.

## Reading semantics

- **Unknown keys** are ignored (forward-compatible).
- **A missing or commented-out key** falls back to its documented default, adaptive rules included.
- **An invalid value for one key** (`auto_commit: yes`, `max_parallel_agents: 0`, an `effort_*`
  outside its set) → that key alone falls back to its default; warn in one line naming the key, the
  bad value and the default used, and continue. The other keys keep their values.
- **A malformed file** (the frontmatter doesn't parse at all) → warn and fall back to all-defaults
  rather than failing the run.
- **A reader never rewrites the file** to repair, reformat or upgrade it — the warning points at
  `/foresdd:config`.
