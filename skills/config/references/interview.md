# The config interview — four questions, three calls, 20 of 24 keys

> **Reference-only.** Read by [`../SKILL.md`](../SKILL.md) steps 2–4 (step 2 uses the option
> labels as the «Current» column of the settings table). Every question here is
> phrased per [`../../allocations/style.md`](../../allocations/style.md): English, action-form
> labels, every technical term glossed inline, the trade-off spelled out in the description.
> Sessions without `AskUserQuestion` ask the same questions as **numbered plain text, one at
> a time, stop and wait** — same shape, same glosses, nothing skipped.

## Three standing rules

- **On a repeat run the current value is the first option, marked «(Recommended)»** — so re-running
  `/foresdd:config` shows what the project is set to today and changes nothing by accident.
- **Group by decision, not by key.** A person tunes «how strict are the gates», not `gate_vet`.
  One answer therefore writes several keys, and the `old → new` output names each one.
- **When the current state matches no option exactly** — for example after someone hand-edited one key of a bundle — do **not** force it into the nearest option.
  Prepend a «Keep as is» option that spells out the actual current values of that group,
  mark it «(Recommended)», and say in the question text which key is the odd one out. Silently
  re-bundling a hand-edited value back into a preset is the way this skill loses a user's edit.

## Question → keys map

| # | Call | Question (the decision) | Keys it writes |
|---|---|---|---|
| 0 | opening | Stay on defaults, or tune? | none — the fork |
| 1 | 1 | Which model tier should the agents run at? | `judgment_model` · `model_test_author` · `model_implementer` · `model_reviewer` · `effort_test_author` · `effort_implementer` · `effort_reviewer` |
| 2 | 2 | How strict should the tests and gates be? | `tdd` · `stop_on_red` · `max_red_retries` · `gate_lint` · `gate_vet` · `require_integration` |
| 3 | 2 | How should tasks execute and commit? | `team_mode` · `workflow_mode` · `max_parallel_agents` · `isolation` · `auto_commit` · `branch_strategy` |
| 4 | 3 | How deeply should the pipeline interview you? | `interview_depth` |
| 0b | after Q0 | Which group do you want to change? (only on «Change one group») | none — picks Q1–Q4 |

**20 keys.** The remaining four — `cmd_test_unit`, `cmd_test_integration`, `cmd_lint`, `cmd_vet` —
are **never asked**. Empty means the command-detection cascade reads the repo's own Makefile,
package scripts and language manifests, which is a better answer than a command pinned once and
left to rot. They stay in the derived list of the step-5 output, named as «left empty for
autodetect».

## Group aliases — targeted runs (step 3)

A request that names a group or a key skips the fork. Match case-insensitively, in any language
the user writes in. A bare key name always resolves to its own group.

| Group | Question | Aliases (argument or plain words) |
|---|---|---|
| Interview depth | Q4 | `depth` · `interview` · `questions` · «how many questions» · `easy` / `medium` / `hard` |
| Model tier | Q1 | `model` · `models` · `tier` · `judges` · `judgment` · `opus` / `sonnet` / `fable` / `inherit` |
| Tests and gates | Q2 | `gates` · `tdd` · `lint` · `vet` · `strict` · `strictness` · `integration` · «stop on red» |
| Execution and commits | Q3 | `execution` · `parallel` · `team` · `workflow` · `worktree` · `commits` · `commit` · `branch` |

**Value-bearing requests write one key, no question** — the user has already decided. Examples:

| Request | Writes |
|---|---|
| `interview_depth=hard` · «set interview depth to hard» · `/foresdd:config depth hard` | `interview_depth: hard` |
| «turn off the lint gate» | `gate_lint: false` |
| «don't stop on red» | `stop_on_red: false` |
| «put the judges on sonnet» | `judgment_model: sonnet` (uncommented) |
| «don't commit for me» | `auto_commit: off` |

A request that maps to a whole preset by name («light gates», «everything on sonnet») writes that
preset's keys, exactly as if the option had been picked. A value outside the key's set (see the
canon) is never written: name the valid values and ask the group's question. A `cmd_*` key given
explicitly with a value (`cmd_lint="make lint"`) is the one case where a `cmd_*` key is written.
The user pinned it on purpose, so write it and note that empty means autodetect.

---

## Q0 — the fork (step 3, before anything is asked)

> **CONTEXT.** `.claude/sdd.local.md` is already on disk with documented defaults, so the pipeline
> works right now — medium-depth interviews, TDD on, opus-tier judgment agents,
> a commit per task. The question is only whether we walk through the settings together and change
> some of them. **WHY IT MATTERS.** Nothing here is irreversible: every key can be changed later by
> running `/foresdd:config` again, and each one carries its meaning inline in the file itself, so you
> can also just open it in an editor. The cost of tuning now is about four questions.
> **READ OPTIONS.**

- **«Keep defaults» (Recommended)** — I change nothing. `.claude/sdd.local.md` is already in the repo with documented values, and every key in it carries a comment explaining it. The pipeline works right away: medium-depth questions, TDD on, a commit after every task. You can come back and tune any time with the same `/foresdd:config`.
- **«Walk the four questions»** — I ask four grouped questions and after each answer patch the matching keys, showing `old → new`. The groups: model tier, test and gate strictness, execution and commit mode, interview depth. Your comments and unknown keys in the file stay untouched. Takes a few minutes.
- **«Change one group»** — You pick one group (interview depth, model tier, tests and gates, or execution and commits) and I ask only that question. The other groups stay exactly as they are. Tip for next time: `/foresdd:config depth` (or `model`, `gates`, `execution`) goes straight there.

On a repeat run where the file already differs from the defaults, the first option becomes
**«Keep as is» (Recommended)**: «I change nothing. The table above is what the project runs on.»

### Q0b — which group (only after «Change one group»)

> **CONTEXT.** One question, four options, one per group. Each description starts with that
> group's current value from the step-2 table, so the user sees what they would be changing.
> **READ OPTIONS.**

- **«Interview depth»** — *Now: <current>.* How many questions `specify`, `clarify` and `design` ask you. The setting people change most often.
- **«Model tier»** — *Now: <current>.* Which models the judging agents and the test/code writers run on. Trades cost against review depth.
- **«Tests and gates»** — *Now: <current>.* TDD on or off, which checks run after each task, and whether a red test stops the run.
- **«Execution and commits»** — *Now: <current>.* Sequential, agent team or Workflow; worktrees; how and when work is committed.

---

## Call 1 — the ground the rest stands on

### Q1 — model tier

> **CONTEXT.** The pipeline runs two kinds of agents. Executors (`test-author`, `implementer`)
> write tests and code. Judges (`reviewer`, `critic`, `devils-advocate`, `strategist`, `analyst`)
> evaluate: they look for holes in the spec, review diffs, attack the idea. One key, `judgment_model`,
> sets the model tier for all five judges at once, and `model_<role>` sets each executor separately.
> **WHY IT MATTERS.** I ask directly because the session fundamentally cannot see the list of models
> available to your account: guessing blindly would produce a setting that fails on the very first dispatch.
> If the chosen model turns out to be unavailable, the dispatch is retried once on `inherit` (the current
> session's model) and does not block the stage. **READ OPTIONS.**

- **«Adaptive defaults: judges on opus, executors on sonnet» (Recommended)** — All seven model / effort keys stay **commented out** (or are commented back out), so the roster defaults apply: judges on `opus`, `test-author` and `implementer` on `sonnet`, `reviewer` on `opus`. The logic is simple: judgment pays for a stronger model, mechanically writing a test does not. Effort stays `medium` for executors and `high` for the reviewer, and on large features (L/XL) the engine raises it by itself. Because nothing is pinned, `opus` is a floor, not a ceiling: if the session runs on a stronger tier, judges go to `inherit` instead of being silently downgraded.
- **«Everything on sonnet»** — uncomments `judgment_model: sonnet` plus all three `model_*` on `sonnet` (`effort_*` stay on their adaptive defaults). This is the supported path for accounts without Opus access: the pipeline runs end to end, reviews become somewhat shallower. Cheaper and faster. If you don't have Opus, pick this rather than the default, so you see the real tier up front instead of via degradation.
- **«Inherit the session model»** — `judgment_model` and all three `model_*` are uncommented as `inherit`: every agent runs on whatever model the session uses. The `effort_*` keys are **not changed**: `inherit` is not in their value set (`low | medium | high | xhigh | max` or a number), so they stay as they were — this is named in the «derived, not asked» list. The simplest option when you don't want to think about tiers at all, and the most predictable in cost. Downside: judges lose their separate lever, so a review can no longer be stronger than the rest of the work.
- **«Judges on fable»** — uncomments `judgment_model: fable`: all five judges go to the Fable tier, the other keys stay on their adaptive defaults (executors on `sonnet`). If `model_reviewer` is pinned, it is commented back out so the reviewer follows the judges. Makes sense when the pain is specifically review and spec-critique quality. Requires the account to have access to that tier, otherwise the dispatch falls back to `inherit` once.

---

## Call 2 — how the work is actually done

### Q2 — strictness and gates

> **CONTEXT.** After every task the engine runs the gates: unit tests, integration tests (if the
> Docker daemon responds), lint (a style check) and vet (static analysis that catches suspicious
> constructs without running the code). Plus the TDD cycle itself: a red test first, then minimal code
> to turn it green. **WHY IT MATTERS.** Stricter gates catch more, but every extra tier adds time per
> task and can block work in a repo where lint isn't set up yet. Gates with no detected command are
> skipped on their own, without failing. **READ OPTIONS.**

- **«Full gates, stop on red» (Recommended)** — `tdd: true`, `stop_on_red: true`, `max_red_retries: 3`, `gate_lint: true`, `gate_vet: true`, `require_integration: auto`. The test is written first; if it is still red after three attempts, the run stops and you see the problem right away. Integration tests run when Docker responds and are silently skipped when it doesn't. This is the default, and in most repos there's no reason to change it.
- **«Don't stop on red»** — The same, but `stop_on_red: false`. A task that stays red is dropped, its dependents are blocked automatically, and the other DAG branches keep going. Useful on a long overnight run, where finishing 8 tasks out of 10 beats stopping at the second. Downside: at the end you have to read the report carefully, because part of the work isn't done.
- **«Light gates»** — `gate_lint: false`, `gate_vet: false`, `require_integration: never`, the rest as in the default. Only unit tests remain. Makes sense in a repo where lint and static analysis aren't set up yet, so every run would otherwise spew noise. The cost is obvious: style and static errors will be caught by review, not by the gates.
- **«No TDD»** — `tdd: false`: the engine writes code straight away, with no red test first. Faster, but you lose the safety net — the red test is exactly what proves the test really checks what it should rather than passing by accident. I'll warn about this in the banner every time. Pick it only if tests in this repo are written differently.

### Q3 — execution and commits

> **CONTEXT.** `implement` takes `tasks.json`, builds a dependency graph and runs the tasks. It can go
> sequentially with one agent, with an agent team (`team_mode`), or with a dynamic Workflow that
> parallelizes independent branches. Parallel agents each work in their own git worktree — a separate
> working copy of the repo, so two of them don't edit the same files. **WHY IT MATTERS.** Parallelism
> saves time on a wide graph and gives nothing on a narrow one, but it always makes the log harder to
> read. Commit granularity decides how finely you can roll the work back later.
> **READ OPTIONS.**

- **«Let the engine decide, commit per task» (Recommended)** — `team_mode: false`, `workflow_mode: auto`, `max_parallel_agents: 3`, `isolation: worktree`, `auto_commit: per_task`, `branch_strategy: feature`. This is the default, and the name is literal: the mode is chosen by the shape of the graph. A narrow chain of tasks runs sequentially, but **a wide independent graph runs as a Workflow and really does start up to three agents at once**, each in its own worktree under `.worktrees/`. If you want a guaranteed single stream, that's the next option, not this one. Each task closes with its own commit carrying `SDD-Task` and `SDD-AC` trailers, and the work happens on a separate feature branch.
- **«Agent team»** — `team_mode: true`: `test-author` → `implementer` → `reviewer` over the graph, coordinated through a shared task list, one worktree per agent. The fastest mode on a large feature with many independent tasks. Downside: the log becomes harder to read, and on a narrow graph there's no gain at all.
- **«Strictly sequential, one stream»** — `team_mode: false`, `workflow_mode: off`, `max_parallel_agents: 1`, `isolation: inplace`: one working copy, no worktrees, tasks one after another, no exceptions. The easiest to read and debug, slower on a wide graph. Pick it when you want to see exactly one stream of work.
- **«Leave commits to me»** — `auto_commit: off` plus the defaults for the rest: the engine writes code and runs the gates but commits nothing. The document steps (`specify`, `design`, `tasks` and the rest) also stop committing their documents and only print ready-made commands in the handoff — the printed commands already carry the `SDD-Stage` / `SDD-Feature` trailers, so running them as-is keeps document history traceable. You decide what to commit and how. Downside: the `SDD-Task` / `SDD-AC` trailers disappear from code commits, and those are what the «acceptance criterion → commit» traceability is built from later.

---

## Call 3 — the key people change most often

### Q4 — interview depth

> **CONTEXT.** The depth dial decides how many questions `specify`, `clarify` and `design` ask, and
> how much they decide on their own. On `easy` the skill takes sensible defaults and writes them into an
> assumptions ledger that you veto in one move; on `hard` it walks every decision and shows the
> trade-off each time. **WHY IT MATTERS.** This is the most noticeable setting in day-to-day work, and it
> removes nothing from coverage: every acceptance criterion stays mandatory at every level, only the
> number of questions changes. The value here is a default that can always be overridden on the spot with
> the `--depth=` argument. Each feature is asked once and remembers its own level, so changing this
> value affects only features you start from now on. **READ OPTIONS.**

- **«Medium» (Recommended)** — `interview_depth: medium`. The skill walks every real decision but doesn't belabor the obvious: typically 3–5 questions per stage. It asks about the ideological forks, takes conventional defaults itself and names them. This is the balance most people work with.
- **«Easy»** — `interview_depth: easy`. I ask only what can't be inferred from context; the rest I decide myself and collect into an assumptions ledger that you review as one block at the end. The fastest pass. The risk is obvious: an assumption you didn't notice in the list travels on into the spec.
- **«Hard»** — `interview_depth: hard`. I walk every decision, surface the trade-off every time, and on `specify` run the full set of ideation agents (market researcher, strategist, analyst, devil's advocate). The most complete result and the longest dialogue. Makes sense on a feature where the cost of a mistake is high.
