# Agent roster — model / effort policy + the shared agent contract

> **Reference-only.** Not a skill. Skills and the implement engine read this for the model/effort
> matrix, the override precedence, and the contract every spawned agent follows. The canonical
> agent definitions live in `agents/*.md`; this file is the policy that ties them together.

## Quick recipes — common situations

| Situation | What to set | Where |
|---|---|---|
| No Opus access on your account | `judgment_model: sonnet` | `.claude/sdd.local.md` |
| Fable session, want judgment on Fable | nothing; the floor rule already inherits the session model (or set `judgment_model: fable` to pin it) | `.claude/sdd.local.md` |
| Cut cost on judgment agents | `judgment_model: sonnet` (reviewer only: `model_reviewer: sonnet`) | `.claude/sdd.local.md` |
| A run feels under-reasoned | `CLAUDE_CODE_EFFORT_LEVEL=high` (or `xhigh`) | shell env |
| One role needs more depth | `effort_<role>` for `test_author` / `implementer` / `reviewer`, e.g. `effort_reviewer: xhigh`; other roles use the env var | `.claude/sdd.local.md` |
| A dispatch failed with "model unavailable" | nothing to do now (it retries on `inherit`); to stop the retry, pin a reachable `judgment_model` | `.claude/sdd.local.md` |
| Agents run as `general-purpose` instead of `foresdd:*` | reinstall the plugin as `foresdd` (an old `sdd`-named install registers `sdd:*` ids) | plugin install |

⚠ `CLAUDE_CODE_SUBAGENT_MODEL` overrides **every** role, judgment included. Setting it to `haiku`
for speed also downgrades `reviewer` / `critic`. Prefer the per-role settings keys.

## The roster (model + effort by role)

Model is chosen by the **kind of work**, not by taste — judgment gets the strongest model, execution gets a balanced one, search/scan gets the cheapest. Effort is the reasoning depth that role needs. Skills themselves declare `model: inherit` — they run on the **session model** (run your SDD session on the strongest tier your account has); the `model` column below is each **agent's** frontmatter default (a tier alias), resolved at dispatch per the override precedence.

| Agent | Kind of work | `model` | `effort` | Tools |
|---|---|---|---|---|
| `explorer` | brownfield scan / search (read-only) | `haiku` | `low` | Read, Grep, Glob, Bash |
| `test-author` | write the failing test (execution) | `sonnet` | `medium` → `high` on escalation | + Write, Edit |
| `implementer` | green + refactor + gate (execution) | `sonnet` | `medium` → `high` on escalation | + Write, Edit |
| `reviewer` | independent review (judgment) | `opus` | `high` | Read, Grep, Glob, Bash |
| `critic` | coherence critique (judgment) | `opus` | `high` | Read, Grep, Glob |
| `devils-advocate` | ambiguity / failure / interview-risk critique | `opus` | `high` | Read, Grep, Glob |
| `researcher` | competitive research / bounded fact-checking | `sonnet` | `medium` | Read, Grep, Glob, WebSearch, WebFetch |
| `strategist` | generate the 3 strategic approaches (judgment) | `opus` | `high` | Read, Grep, Glob |
| `analyst` | multi-perspective review of approaches (judgment) | `opus` | `high` | Read, Grep, Glob |
| `pen-keeper` | reconcile the .pen library with the canon (execution) | `sonnet` | `medium` | Read, Grep, Glob, Bash, Pencil MCP |

Rationale: judgment quality (review, critique, ambiguity, strategy, multi-perspective synthesis) is where a stronger model pays off; execution (write code/tests to a clear spec) is well served by a balanced model and escalates only when it gets stuck; a read-only scan is cheap. The **ideation trio** (`specify` step 3, gated by the depth dial) follows the same logic: `researcher` is gathering-and-citing work (balanced model + web tools), while `strategist` and `analyst` are judgment (generating real alternatives, synthesizing across lenses) and get the strongest model. (Treat model-by-role as a sound principle — the headline "stronger orchestrator + cheaper workers wins by X%" claim from the multi-agent literature did not survive verification, so we lean on role-fit, not a magic ratio.)

## Dispatching (`subagent_type`)

These agents are **plugin-namespaced**. Spawn each with `subagent_type: "foresdd:<name>"` — the id Claude Code registers and shows in the available-agents list — **not** the bare name and **not** an `sdd-…` prefix:

`foresdd:explorer` · `foresdd:test-author` · `foresdd:implementer` · `foresdd:reviewer` · `foresdd:critic` · `foresdd:devils-advocate` · `foresdd:researcher` · `foresdd:strategist` · `foresdd:analyst` · `foresdd:pen-keeper`

So when a skill says «dispatch the `explorer` agent», the call is `subagent_type: "foresdd:explorer"`. If the namespaced agent isn't available at runtime, fall back to the general-purpose (or `Explore`) agent the skill names, passing the same prompt. A fallback agent never reads `agents/*.md` — everything it must know arrives in the prompt, **including the async report-delivery instruction** (shared-contract point 2 below) when the host runs it in background/teammate mode.

### Dispatch when the named agent is missing

The `subagent_type: "foresdd:<name>"` form is the id the plugin loader registers. When it isn't
registered in the session, use the stage's documented fallback (usually `general-purpose` with the
same prompt), or run the agent file's instructions **inline** in the current context. Same
degrade-don't-block rule: [`fallbacks.md`](./fallbacks.md).

## Override precedence (highest wins)

```
env var  >  per-invocation (the Agent call)  >  model_<role>  >  judgment_model  >  frontmatter  >  session
```

**`judgment_model`** (`.claude/sdd.local.md`) is the one-switch tier for the **judgment agents** —
`reviewer` / `critic` / `devils-advocate` / `strategist` / `analyst`. Its value is **open, not a
closed enum**: a tier alias (`haiku | sonnet | opus | fable`), `inherit` (the session model), or a
full model id — the same value-set as `CLAUDE_CODE_SUBAGENT_MODEL` below. Default `opus`.
`sonnet` is the **supported path for accounts without Opus access**; `fable` for accounts with
Fable access. One key sets all five without touching `agents/*.md` (their frontmatter stays the
tier-alias default); a per-role `model_<role>` key still wins for its role. It never applies to
execution (`test-author` / `implementer`) or gathering (`explorer` / `researcher`) roles. See the
settings doc: [`settings-file.md`](./settings-file.md) (the key's semantics) and
[`../implement/references/settings.md`](../implement/references/settings.md) (how it resolves at dispatch).

**The default is a floor, not a pin:** when `.claude/sdd.local.md` sets no `judgment_model`
(missing, or commented out as the template ships it) and
the session model is a stronger tier than `opus` (tier order `haiku < sonnet < opus < fable`),
dispatch judgment agents with `inherit` — never silently downgrade judgment below the session. An
explicit `judgment_model` is always honored literally (a user on a Fable session may deliberately
set `sonnet` for cost).

- **`model`** env: `CLAUDE_CODE_SUBAGENT_MODEL`. Values: `haiku|sonnet|opus|fable|inherit|<full-model-id>`.
  It sits at the top of the precedence and applies to **all** roles, so it overrides `judgment_model` too.
  When it is set and resolves below the judgment default, the dispatching skill names this in its
  banner/handoff (e.g. «judgment agents on `haiku` via `CLAUDE_CODE_SUBAGENT_MODEL`»). It never
  silently downgrades judgment.
- **`effort`** env: `CLAUDE_CODE_EFFORT_LEVEL`. Values: `low|medium|high|xhigh|max|<number>` (`xhigh`/`max` exist only on the stronger tiers — current Opus/Sonnet/Fable generations, not Haiku; if the resolved model rejects the level, cap at `high`).
- Per-project overrides live in `.claude/sdd.local.md` as `model_<role>` / `effort_<role>` keys (see the implement settings).

> **Caveat (verify on your build).** Some Claude Code builds have reported the `effort:` *frontmatter*
> having no observable runtime effect (GitHub claude-code#43083). The field is documented and we set
> it, but treat the **env path** (`CLAUDE_CODE_EFFORT_LEVEL`) as the reliable lever, and the per-role
> `effort_*` settings keys map to it. If a run feels under-reasoned, set the env var.

## Model availability — degrade, don't block

**Canonical here** — other files link to this rule, never restate it. If a dispatch fails because
the selected model is unavailable to this account (no entitlement for the tier, or a variant like
`[1m]` outside the plan), **retry the same prompt once with `model: inherit`** (the session model),
name the degradation in the banner/handoff, and recommend pinning a reachable `judgment_model` in
`.claude/sdd.local.md`. A missing model tier never blocks a stage — this is the model-tier arm of
the degrade-don't-block rule in [`fallbacks.md`](./fallbacks.md).

## Scale with feature size

Default effort/model scale with the feature `.size` (see [`tshirt-sizing.md`](./tshirt-sizing.md)):

- **XS/S** → keep the roster defaults (cheap; the work is small).
- **M** → roster defaults; escalation handles the hard tasks.
- **L/XL** → bump execution effort to `high`; **the critical verifications go to `xhigh`** — the
  `reviewer` (dispatched by `review`) and the `critic` (dispatched by `design` / `specify`) run at
  `effort: xhigh`, passed **per-invocation** on that Agent call (the env var is session-wide and
  cannot target one role). If the build ignores per-call effort (see the caveat above), the handoff
  tells the user to re-run with `CLAUDE_CODE_EFFORT_LEVEL=xhigh` (or, for the reviewer, set
  `effort_reviewer: xhigh`). An explicit `effort_<role>` setting or the env var still wins per the
  precedence. The other judgment agents stay `high`. Cap at the highest effort level the resolved judgment model
  supports. A cross-module change is where reasoning depth pays off, and the final review/critique
  is where it pays off most.

A skill/engine that knows the size applies this before dispatch and says so in its banner.

## The shared agent contract (every spawned agent)

1. **Clean, isolated context by default.** A spawned agent does **not** see the parent conversation, tool results, system prompt, invoked skills, or files already read — the **only channel is the Agent prompt string**. So the dispatching skill must inline paths, the draft/diff, and decisions explicitly; the agent re-reads upstream artifacts itself. Only the agent's final message returns. This isolation *is* the "fork" for independent review/critique — fresh eyes are the point.
   - **Fork mode** (`CLAUDE_CODE_FORK_SUBAGENT`, experimental) inherits the full conversation + shares the prompt cache. Use it **only** for a live side-task that genuinely needs the running context — never for `reviewer` / `critic` / `devils-advocate`, whose value is independence.
2. **The report must reach the dispatcher.** The final message IS the deliverable. When the host runs subagents asynchronously (background/teammate mode), the dispatching skill appends to the prompt: «also send your full final report as a message to your dispatcher (main)». An idle/completion signal without content is NOT a verdict — the dispatcher pulls the report through the host's messaging channel before proceeding.
3. **Worker preamble.** When an orchestrator (the implement team/workflow) delegates, it wraps the task: «execute directly, do not spawn sub-agents, use tools directly, report results with absolute file paths». A subagent cannot spawn subagents, so the lead owns fan-out.
4. **Verify before claiming done.** Before saying "done / fixed / passing": IDENTIFY the command that proves it → RUN it → READ the output → only then claim, with the evidence. Words like "should / probably / seems" are a red flag that verification hasn't run.
5. **Cite or drop.** Read-only judgment agents (reviewer/critic/devil's-advocate) emit only cited findings (`file:line` + the artifact/AC clause). An uncited finding is dropped, not shipped.
