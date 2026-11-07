# foresdd behaviour evals — on-demand, NOT CI

End-to-end scenarios that drive a real headless `claude` session over a fixture repo, then have an
LLM judge check the outcome against a rubric. They test that a **skill's protocol actually
behaves**: gates refuse, artifacts come out in the right shape, commits carry their trailers, and
handoffs are printed. The manifests are checked separately by `scripts/validate_plugin.py`.

> **Why not CI.** Each scenario runs `claude -p` twice: once for the run under test and once for
> the judge. That costs real tokens (≈ $0.30 for a gate refusal, a few dollars for a full stage),
> takes from 30 s to several minutes, and gives non-deterministic results. Run evals locally when you change a
> skill's protocol. CI only runs the free static check, `./evals/run.sh --lint`.

## Quick start

```bash
./evals/run.sh --list                       # every scenario + the skill/agent it exercises
./evals/run.sh design-gate-refusal          # one scenario
./evals/run.sh -j 4                         # all scenarios, 4 in parallel
./evals/run.sh --lint                       # free: scenarios well-formed + skill coverage
SDD_EVAL_MODEL=opus ./evals/run.sh tshirt-size
```

Output per scenario is one ✓/✗ line per rubric item with the judge's evidence, then the turn
count and cost. At the end comes a summary table:

```
PASS design-gate-refusal (31s)
  ✓ 1. sad.md not created
      File tree contains only .size; no sad.md in tree or diff
  ✓ 3. Refusal names specify
      Final message says "Run `specify tiny-toggle` first"
  10 turns, $0.34

Summary
  STATUS SCENARIO                               TIME  WORKDIR
  PASS   design-gate-refusal                     31s  -
  FAIL   plan-tests-gate-refusal                 27s  /tmp/sdd-eval-plan-tests-gate-refusal.Ab12Cd
```

| Option / env | Effect |
|---|---|
| `-l`, `--list` | List scenarios and what they exercise |
| `--lint` | Check every scenario's structure and that each `/foresdd:<skill>` or `{{PLUGIN_ROOT}}` path it names exists; report skills with no scenario. No model calls |
| `-j N`, `--jobs N` | Run N scenarios in parallel (default 1) |
| `-k`, `--keep` | Keep every workdir. By default passing workdirs are deleted and **failing ones are kept** so you can inspect them |
| `SDD_EVAL_MODEL` | Model for both the run and the judge (default: your CLI default) |
| `SDD_EVAL_MAX_TURNS` | Turn cap for the run under test (default 40) |
| `SDD_EVAL_DIFF_LINES` | Diff lines shown to the judge (default 1500; truncation is marked) |
| `NO_COLOR=1` | Plain output |

Exit status: `0` when all scenarios pass, `1` when any fails, `2` on a usage error.

## Prerequisites

- `claude` CLI installed and logged in. The plugin does **not** need to be installed: `run.sh`
  loads it from this checkout with `--plugin-dir`, so you test the working tree. The checkout
  is also passed with `--add-dir` so the run can read referenced instructions.
- `jq` and `git` on PATH. The script runs on macOS's stock bash 3.2.
- Scenarios that run fixture code (`fix-*`, `ship-*`) also need `python3` and `make`.

## How a scenario works

1. **Baseline.** The script copies `scenarios/<name>/fixture/` into a fresh `mktemp` dir, then
   runs `git init` and commits it as `baseline`.
2. **Run under test.** The script runs `claude -p "$(cat prompt.txt)" --permission-mode acceptEdits
   --max-turns 40 --output-format json` inside that dir.
   - `Bash(git:*)` is pre-allowed so the run can commit. Otherwise commit-cadence rubrics would
     pass vacuously.
   - Any rules in the scenario's optional `allowed-tools.txt` are added to that allow list.
   - Interactive skills pin `--depth=easy` and state «headless — no interactive user», because a
     headless run cannot answer `AskUserQuestion`.
   - The run counts as a FAIL before judging when the CLI errors or a read of the plugin's own
     instructions is denied.
3. **Judge.** A second `claude -p` call gets [`judge-prompt.md`](./judge-prompt.md) and the
   rubric, plus this evidence:
   - the file tree;
   - `git log` with each commit's subject, trailers and touched paths;
   - `git status --porcelain` (what the run left uncommitted);
   - the full diff vs the baseline, with a `--stat` header and an explicit marker if truncated;
   - the run's complete final message.

   It answers with one JSON object, `{"verdict": "PASS"|"FAIL", "checks": [...]}`.

Transcripts (`run.json`), the judge prompt, the raw judge reply and the full diff for each scenario
are saved in the run directory, whose path is printed at the start.

## Scenarios

Every skill has at least one scenario (`--lint` reports any gap). Grouped by pipeline stage:

### Discovery and planning

| Scenario | What it proves |
|---|---|
| `interview-headless-no-writes` | `/foresdd:interview` with no human response channel writes no brief, settings or `.gitignore`, claims no helper output, and fabricates no interview |
| `roadmap-fog-unsized` | `/foresdd:roadmap` on a brief whose second data source has never been inspected writes `fog` in that step's **`Size`** cell and parks it as ONE area in `## Not yet specified` rather than sizing it. It still writes the file even though the fixture has no architecture map |
| `roadmap-same-zone-wave` | `/foresdd:roadmap` keeps two steps that both edit `internal/checkout/pricing.go` out of the same wave, which the dependency graph alone would allow but the codebase doesn't. The `internal/notify/` step still runs in parallel |
| `survey-brownfield-map` | `/foresdd:survey` on an existing Go service writes `docs/architecture-map.md` in template shape:<br>• `mode: current`, `reflects_commit` = the baseline SHA<br>• machine keys backed by evidence; only real modules and conventions<br>• no scaffold `tasks.json`, no foundational ADRs, no source edits<br>• one `survey:` commit with `SDD-Stage: survey`; hands off to `specify` |
| `scaffold-gate-refusal` | `/foresdd:scaffold` on an idea-stage repo with no greenfield `architecture-map.md` and no `_scaffold/tasks.json` refuses and points at `survey`. It writes no foundation, no skeleton and no settings file, and makes no commit |
| `design-system-code-mode` | `/foresdd:design-system` (tool `code`, desktop-first, `src/styles/tokens.css`) writes `docs/design-system.md`:<br>• posture, token source and the exact Button/TextField/Card inventory, each with a `file:line` anchor<br>• no `.pen` file, no MCP writes, no source edits<br>• one `design-system:` commit; utility handoff with `self-check: 5/5 pass` |
| `config-targeted-depth` | `/foresdd:config interview_depth=hard` skips the menu and the interview. It creates the settings file, changes exactly that one key (`old → new`), patches `.gitignore`, and hands off |
| `glossary-lookup-read-only` | `/foresdd:glossary what is …` answers from the feature-level `CONTEXT.md`, names the file, and doesn't confuse `seat` with `seat-pool`. It writes nothing: no stamp, no commit |

### Specification

| Scenario | What it proves |
|---|---|
| `specify-happy-path` | `/foresdd:specify` produces a spec.md with §1–§8, business-observable ACs, `.size` + `.route`, and the handoff block. `spec.md` and `.size`+`.route` land in separate commits, each with `SDD-Stage` / `SDD-Feature` trailers |
| `specify-brief-reuse` | `/foresdd:specify` keeps the accepted brief, doesn't re-ask discovery questions, and preserves the brief's source limits |
| `tshirt-size` | `/foresdd:tshirt-size` writes one-token `.size` and `.route` files and hands off (utility variant) |
| `clarify-judgment-sonnet` | `/foresdd:clarify` with `judgment_model: sonnet` reads and honours the setting, runs the sweep on the sonnet tier, and never claims opus. *Limitation:* covers the configuration path only, not the missing-entitlement fallback |
| `plan-tests-gate-refusal` | `/foresdd:plan-tests` with `.size` + `.route` but **no spec.md** refuses and points at `specify`. It writes no test-plan.md and no spec.md stub, and makes no commit |

### Design

| Scenario | What it proves |
|---|---|
| `design-gate-refusal` | `/foresdd:design` on a folder with `.size` but **no spec.md** refuses, points at `specify`, and writes no sad.md or ADRs |
| `design-commit-per-document` | `/foresdd:design` on route quick + depth easy writes all 12 SAD sections, then commits once per document after the self-check: exactly 1 `sad.md` commit + 1 per ADR, each with trailers. No per-section commits |
| `decide-adr-posthoc` | `/foresdd:decide-adr` records a decision already made in code as a MADR ADR:<br>• blast-radius gate applied; numbered `0002` because `0001` exists<br>• all options listed, with at least one honest Negative<br>• `Proposed` with the pending reviewer; sad.md §9 row added<br>• two commits (ADR, then `sad.md`); utility handoff |
| `ux-flows-code-mode` | `/foresdd:ux-flows` with a `tool: code`, mobile-first canon derives `ux-flows.md`:<br>• valid mermaid flowcharts and an SCR inventory<br>• full AC coverage, mobile-first posture honoured<br>• handoff to `design` |
| `sequences-gate-refusal` | `/foresdd:sequences` with spec.md but **no sad.md** refuses and points at `design`. It draws no sequence diagram and makes no commit |
| `data-model-gate-refusal` | `/foresdd:data-model` with spec.md + live migrations but **no sad.md** refuses and points at `design` (the missing one, not `specify`). It writes no data-model.md, no migrations and no self-served sad.md |
| `api-fastlane-no-datamodel` | `/foresdd:api` on a no-schema-change feature **without** data-model.md does not refuse. It derives the contract from the existing schema, names the legal skip and the «existing schema» origin, and hands off |
| `api-schema-change-refusal` | `/foresdd:api` on a feature **with** a schema change and no data-model.md hard-refuses and names `data-model`. It writes no contract and no self-served data-model.md |
| `screens-code-mode` | `/foresdd:screens` with a `tool: code` canon writes `screens.md`:<br>• one section per SCR id<br>• every non-default state traced to an AC, a §6 branch or a contract error<br>• inventory components or justified `NEW:`; compact wireframes<br>• a `screens:` commit and a handoff to `tasks` |
| `screens-pencil-degraded` | `/foresdd:screens` with a `tool: pencil` canon and no Pencil MCP falls back to code mode **and says so**: `degraded_from: pencil`, the fallback named in the handoff, no `.pen` file touched. *Limitation:* the live active-document gate needs the Pencil app |

### Build and ship

| Scenario | What it proves |
|---|---|
| `tasks-compile-coupled-lane` | `/foresdd:tasks` on a Go feature extending a shared interface emits no standalone interface-only task. It either folds the contract change in or marks the compile-coupled pair with a shared `files_hint` |
| `implement-gate-refusal` | `/foresdd:implement` with spec.md + sad.md but **no tasks.json** refuses and points at `tasks`. It writes no code, no settings file and no `.gitignore` (settings are only created after the gate), and makes no commit |
| `review-gate-refusal` | `/foresdd:review` on a feature with the full upstream chain but **nothing implemented** refuses and points at `implement`. It writes no `_review/` record, gives no verdict and makes no commit |
| `fix-regression-red-green` | `/foresdd:fix` on a Python feature whose code violates AC-01 (free shipping at "50.00 or more", code uses `>`):<br>• triages it as a **regression**<br>• pins it with a boundary test that fails on the baseline<br>• applies the minimal `>`→`>=` fix; `spec.md` untouched<br>• writes `_fixes/…md`; two commits (fix with `SDD-Fix` + `SDD-AC`, then record) |
| `ship-proposes-pr` | `/foresdd:ship` on an implemented, PASS-reviewed feature with no remote:<br>• re-runs the gate and runs the CLI against at least 3 ACs<br>• writes `changelog.md`, a root `CHANGELOG.md` line and the roadmap `shipped` row, as 3 single-document `ship:` commits<br>• **proposes** the PR (body links spec, ACs, ADR, review) without pushing or merging; terminal Done handoff |

### Agent contracts

These scenarios exercise an agent's instructions directly (via `{{PLUGIN_ROOT}}/agents/<name>.md`),
not through a skill.

| Scenario | What it proves |
|---|---|
| `researcher-fact-check-conflict` | Fact-check mode keeps conflicting source applicability and the limits of owner reports, and does not turn into competitive research |
| `interview-critic-grounded` | Explicit interview mode returns at most three grounded risk findings, not an invented breach or a legacy quota |

### What headless evals cannot prove

A headless run cannot answer `AskUserQuestion`. Every interactive checkpoint is therefore either
pre-answered in the prompt or tested only for refusal. Examples are survey's owner confirm, fix's
"Proceed" checkpoint and ship's staleness check. For real adaptive questioning use the manual protocol in
[`interactive/interview.md`](./interactive/interview.md), and keep the transcript (past results:
[`results/`](./results/)). Never report a headless scenario as proof of interactive behaviour.

## Adding a scenario

Create `scenarios/<kebab-name>/` with:

- `fixture/`: the starting repo tree, committed as the baseline. Keep it minimal. If the run
  must execute code, make sure the fixture's own tests pass first.
- `prompt.txt`: the exact `-p` prompt. Start with the `/foresdd:<skill>` command line, then add
  the headless framing: state the idea and answers inline, and pin `--depth=easy` for interactive
  skills. Agent scenarios name `{{PLUGIN_ROOT}}/agents/<name>.md` and the explicit mode instead;
  `{{PLUGIN_ROOT}}` resolves to the checkout under test.
- `rubric.md`: numbered PASS conditions, followed by a «FAIL on …» line. The judge must be able
  to verify each item from the tree, git log, diff or final message alone. «The model tried» is
  not a rubric item.
- `allowed-tools.txt` (optional): extra `--allowedTools` rules, one per line, for runs that must
  execute the fixture's tests or app, e.g. `Bash(make test)`. Keep them as narrow as possible.

Then run `./evals/run.sh --lint`, and run the scenario once for real before committing it.

## Troubleshooting

- **`the run under test failed`**: check `run.json` and `run.stderr` in the run directory.
  `error_max_turns` means you should raise `SDD_EVAL_MAX_TURNS` or tighten the prompt.
- **`judge reply was not valid JSON`**: the raw reply is in `judge.txt`. Re-run; if it keeps
  happening, pin a stronger judge with `SDD_EVAL_MODEL`.
- **A check fails on evidence that should exist**: open the kept workdir. If the change was
  bigger than the diff limit, raise `SDD_EVAL_DIFF_LINES`.
