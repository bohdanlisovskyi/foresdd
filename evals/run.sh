#!/usr/bin/env bash
# foresdd eval harness — on-demand, NOT CI (each scenario invokes `claude` and costs tokens).
# Run `./evals/run.sh --help` for usage.
#
# Portability: must run on macOS's bash 3.2 — no `wait -n`, no associative arrays, and an
# EMPTY array under `set -u` must be expanded as ${arr[@]+"${arr[@]}"}.
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$EVALS_DIR/.." && pwd)"   # the plugin under test — loaded via --plugin-dir
SCEN_DIR="$EVALS_DIR/scenarios"
MAX_TURNS="${SDD_EVAL_MAX_TURNS:-40}"
DIFF_LINES="${SDD_EVAL_DIFF_LINES:-1500}"
TMP_ROOT="${TMPDIR:-/tmp}"; TMP_ROOT="${TMP_ROOT%/}"
MODEL_ARGS=()
[ -n "${SDD_EVAL_MODEL:-}" ] && MODEL_ARGS=(--model "$SDD_EVAL_MODEL")

JOBS=1
KEEP=0
MODE=run

usage() {
  cat <<'EOF'
Usage: ./evals/run.sh [options] [scenario ...]

Runs each scenario headlessly against this checkout, then has an LLM judge grade
the outcome against the scenario's rubric. No scenario names → all scenarios.

Options:
  -l, --list     List scenarios with the skill/agent each one exercises, then exit
      --lint     Check every scenario is well-formed and report skill coverage
                 (no model calls — this is what CI runs)
  -j, --jobs N   Run N scenarios in parallel (default 1)
  -k, --keep     Keep every workdir (default: passing workdirs are deleted,
                 failing ones are kept for inspection)
  -h, --help     Show this help

Environment:
  SDD_EVAL_MODEL=<model>     Model for the run under test and the judge
  SDD_EVAL_MAX_TURNS=<n>     Turn cap for the run under test (default 40)
  SDD_EVAL_DIFF_LINES=<n>    Diff lines shown to the judge (default 1500)

Exit status: 0 when every scenario passes, 1 when any fails, 2 on usage errors.
EOF
}

# ---------- output helpers ----------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_OK=$'\033[32m'; C_BAD=$'\033[31m'; C_DIM=$'\033[2m'; C_B=$'\033[1m'; C_0=$'\033[0m'
else
  C_OK=''; C_BAD=''; C_DIM=''; C_B=''; C_0=''
fi
die() { echo "${C_BAD}error:${C_0} $*" >&2; exit 2; }

all_scenarios() { ls "$SCEN_DIR"; }

# What a scenario exercises: the /foresdd:<skill> in its prompt, else the agent file it reads.
scenario_target() {
  local p="$SCEN_DIR/$1/prompt.txt" t
  t="$(grep -oE '/foresdd:[a-z0-9-]+' "$p" 2>/dev/null | head -1 || true)"
  [ -n "$t" ] && { echo "${t#/foresdd:}"; return; }
  t="$(grep -oE '\{\{PLUGIN_ROOT\}\}/agents/[a-z0-9-]+\.md' "$p" 2>/dev/null | head -1 || true)"
  [ -n "$t" ] && { t="${t##*/}"; echo "agent:${t%.md}"; return; }
  echo "?"
}

# ---------- --list ----------
list_scenarios() {
  local s
  for s in $(all_scenarios); do
    printf '  %-36s %s\n' "$s" "$(scenario_target "$s")"
  done
}

# ---------- --lint ----------
lint_scenarios() {
  local s d errs=0 n=0 ref skill covered="" missing=""
  for s in $(all_scenarios); do
    d="$SCEN_DIR/$s"; n=$((n + 1))
    local bad=""
    [[ "$s" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || bad="$bad; name is not kebab-case"
    [ -d "$d/fixture" ]   || bad="$bad; missing fixture/"
    [ -s "$d/prompt.txt" ] || bad="$bad; missing or empty prompt.txt"
    if [ -s "$d/rubric.md" ]; then
      grep -qE '^[0-9]+\.' "$d/rubric.md" || bad="$bad; rubric.md has no numbered items"
    else
      bad="$bad; missing or empty rubric.md"
    fi
    if [ -s "$d/prompt.txt" ]; then
      while read -r ref; do
        [ -n "$ref" ] || continue
        skill="${ref#/foresdd:}"
        [ -f "$REPO_ROOT/skills/$skill/SKILL.md" ] || bad="$bad; prompt invokes $ref but skills/$skill/SKILL.md does not exist"
        covered="$covered $skill"
      done < <(grep -oE '/foresdd:[a-z0-9-]+' "$d/prompt.txt" | sort -u || true)
      while read -r ref; do
        [ -n "$ref" ] || continue
        [ -e "$REPO_ROOT/${ref#\{\{PLUGIN_ROOT\}\}/}" ] || bad="$bad; prompt reads $ref which does not exist"
      done < <(grep -oE '\{\{PLUGIN_ROOT\}\}/[A-Za-z0-9_/-]+(\.[A-Za-z0-9_-]+)*' "$d/prompt.txt" | sort -u || true)
      grep -qE '/foresdd:|\{\{PLUGIN_ROOT\}\}' "$d/prompt.txt" || bad="$bad; prompt names no /foresdd:<skill> and no {{PLUGIN_ROOT}} file"
    fi
    if [ -n "$bad" ]; then
      echo "  ${C_BAD}✗${C_0} $s${bad/#;/:}"; errs=$((errs + 1))
    else
      echo "  ${C_OK}✓${C_0} $s"
    fi
  done
  # Coverage: every skill (except the shared allocations/ library) should have >=1 scenario.
  for d in "$REPO_ROOT"/skills/*/; do
    skill="$(basename "$d")"
    [ "$skill" = allocations ] && continue
    case " $covered " in *" $skill "*) ;; *) missing="$missing $skill" ;; esac
  done
  echo
  if [ -n "$missing" ]; then
    echo "${C_DIM}coverage: skills with no scenario:${missing}${C_0}"
  else
    echo "coverage: every skill has at least one scenario"
  fi
  if [ "$errs" -gt 0 ]; then
    echo "${C_BAD}FAILED${C_0}: $errs of $n scenarios are malformed"; return 1
  fi
  echo "${C_OK}PASSED${C_0}: $n scenarios well-formed"
}

# ---------- one scenario ----------
# Writes a human log to stdout and "<STATUS> <seconds> <workdir>" to $RUN_DIR/<name>/status.
run_scenario() {
  local name="$1" dir="$SCEN_DIR/$1" meta="$RUN_DIR/$1" started work status=ERROR
  started="$(date +%s)"
  mkdir -p "$meta"
  work="$(mktemp -d "${TMP_ROOT}/sdd-eval-$name.XXXXXX")"
  finish() {
    local secs=$(( $(date +%s) - started ))
    if [ "$status" = PASS ] && [ "$KEEP" -eq 0 ]; then rm -rf "$work"; work="-"; fi
    echo "$status $secs $work" > "$meta/status"
  }

  # 1. Fixture → git baseline.
  cp -R "$dir/fixture/." "$work/"
  git -C "$work" init -q
  git -C "$work" add -A
  git -C "$work" -c user.email=eval@sdd -c user.name=sdd-eval commit -qm baseline

  # 2. The run under test — headless (prompts pin --depth=easy; a headless run cannot answer
  #    AskUserQuestion). --plugin-dir loads THIS checkout, not an installed version.
  #    Bash(git:*) is pre-allowed so the run can commit in the throwaway workdir — without it
  #    acceptEdits blocks commits and commit-cadence rubrics pass vacuously.
  #    A scenario that must run the fixture's tests/app lists the extra rules, one per line,
  #    in an optional allowed-tools.txt next to prompt.txt (keep them narrow).
  local out="$meta/run.json" prompt run_rc=0 allowed="Bash(git:*)" rule
  if [ -f "$dir/allowed-tools.txt" ]; then
    while IFS= read -r rule || [ -n "$rule" ]; do
      case "$rule" in ''|'#'*) continue ;; esac
      allowed="$allowed,$rule"
    done < "$dir/allowed-tools.txt"
  fi
  prompt="$(cat "$dir/prompt.txt")"
  prompt="${prompt//\{\{PLUGIN_ROOT\}\}/$REPO_ROOT}"
  ( cd "$work" && claude -p "$prompt" \
      --plugin-dir "$REPO_ROOT" --add-dir "$REPO_ROOT" \
      --permission-mode acceptEdits --max-turns "$MAX_TURNS" \
      --allowedTools "$allowed" \
      --output-format json ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} > "$out" 2> "$meta/run.stderr" ) || run_rc=$?

  # --output-format json is an object in some CLI versions, an array of messages (result
  # last) in others — accept both.
  local last='if type=="array" then last else . end'
  if [ "$run_rc" -ne 0 ] || ! jq -e "$last | .is_error == false" "$out" >/dev/null 2>&1; then
    local why
    why="$(jq -r "$last | .subtype // .result // empty" "$out" 2>/dev/null | head -1 || true)"
    echo "  ${C_BAD}✗ the run under test failed${C_0} (exit $run_rc${why:+, $why})"
    echo "    ${C_DIM}see $out and $meta/run.stderr${C_0}"
    finish; return 1
  fi
  if jq -e --arg root "$REPO_ROOT/" "$last |
      any((.permission_denials // [])[]; .tool_name == \"Read\" and
        ((.tool_input.file_path // \"\") | startswith(\$root)))" "$out" >/dev/null 2>&1; then
    echo "  ${C_BAD}✗ a read of the plugin's own instructions was denied${C_0} — see $out"
    finish; return 1
  fi
  local cost turns
  cost="$(jq -r "$last | .total_cost_usd // empty" "$out" 2>/dev/null || true)"
  turns="$(jq -r "$last | .num_turns // empty" "$out" 2>/dev/null || true)"

  # 3. Evidence for the judge.
  local final_msg tree gitlog gitstatus diff base diff_total
  final_msg="$(jq -r "$last | .result // empty" "$out")"
  tree="$(cd "$work" && find . -path ./.git -prune -o -type f -print | sort)"
  # Subject + trailers + touched paths per commit, so rubrics can check commit contents and
  # the SDD-* trailers, not just the subject line.
  gitlog="$(git -C "$work" log --format='%h %s%n%(trailers:only,unfold)' --name-only | head -200 || true)"
  # Captured BEFORE the `add -A` below, so the judge sees what the run left uncommitted.
  gitstatus="$(git -C "$work" status --porcelain)"
  # Diff vs the FIXTURE BASELINE (root commit), not HEAD — committed + uncommitted.
  base="$(git -C "$work" rev-list --max-parents=0 HEAD)"
  git -C "$work" add -A
  git -C "$work" diff --cached "$base" > "$meta/full.diff" || true
  diff_total="$(wc -l < "$meta/full.diff" | tr -d ' ')"
  diff="$(git -C "$work" diff --cached --stat "$base" | tail -60 || true)
$(head -n "$DIFF_LINES" "$meta/full.diff")"
  if [ "$diff_total" -gt "$DIFF_LINES" ]; then
    diff="$diff
[... diff truncated: showing $DIFF_LINES of $diff_total lines — the --stat above lists every touched file ...]"
  fi

  # 4. The judge — rubric + observed outcome → one JSON verdict.
  local jp="$meta/judge-prompt.md"
  # shellcheck disable=SC2016  # backticks are literal markdown
  {
    cat "$EVALS_DIR/judge-prompt.md"
    printf '\n## Rubric\n\n'; cat "$dir/rubric.md"
    printf '\n## File tree after the run\n\n```\n%s\n```\n' "$tree"
    printf '\n## Git log after the run (newest first; "baseline" is the fixture commit; per commit: `<sha> <subject>`, its trailers, then the paths it touched)\n\n```\n%s\n```\n' "$gitlog"
    printf '\n## Uncommitted changes the run left (`git status --porcelain`; empty = clean)\n\n```\n%s\n```\n' "$gitstatus"
    printf '\n## Git diff vs the fixture baseline (committed + uncommitted)\n\n```\n%s\n```\n' "$diff"
    printf '\n## The run'\''s final message\n\n```\n%s\n```\n' "$final_msg"
  } > "$jp"

  local judge_raw verdict_json verdict
  judge_raw="$(claude -p "$(cat "$jp")" --output-format json ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} 2>>"$meta/run.stderr" \
                | jq -r "$last | .result // empty" 2>/dev/null || true)"
  printf '%s\n' "$judge_raw" > "$meta/judge.txt"
  # Tolerate a stray code fence or prose around the object: keep from the first { to the last }.
  verdict_json="$(printf '%s' "$judge_raw" | awk '
      { buf = buf $0 "\n" }
      END { s = index(buf, "{"); e = 0
            for (i = length(buf); i > 0; i--) if (substr(buf, i, 1) == "}") { e = i; break }
            if (s && e > s) printf "%s", substr(buf, s, e - s + 1) }')"
  verdict="$(printf '%s' "$verdict_json" | jq -r '.verdict // empty' 2>/dev/null || true)"

  if [ -z "$verdict" ]; then
    echo "  ${C_BAD}✗ judge reply was not valid JSON${C_0} — see $meta/judge.txt"
    finish; return 1
  fi
  printf '%s' "$verdict_json" | jq -r --arg ok "${C_OK}✓${C_0}" --arg bad "${C_BAD}✗${C_0}" --arg dim "$C_DIM" --arg z "$C_0" '
      .checks[]? | "  \(if .pass then $ok else $bad end) \(.name)\n      \($dim)\(.note // "")\($z)"'
  [ -n "$turns" ] && echo "  ${C_DIM}${turns} turns${cost:+, \$$cost}${C_0}"
  status="$verdict"
  [ "$status" = PASS ] || status=FAIL
  finish
  [ "$status" = PASS ]
}

print_result() {
  local name="$1" st secs work
  read -r st secs work < "$RUN_DIR/$name/status"
  case "$st" in
    PASS) echo "${C_OK}${C_B}PASS${C_0} $name ${C_DIM}(${secs}s)${C_0}" ;;
    *)    echo "${C_BAD}${C_B}${st}${C_0} $name ${C_DIM}(${secs}s)${C_0}" ;;
  esac
  cat "$RUN_DIR/$name/log"
  [ "$work" != "-" ] && echo "  ${C_DIM}workdir: $work${C_0}"
  echo
}

# ---------- arg parsing ----------
NAMES=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -l|--list) MODE=list ;;
    --lint)    MODE=lint ;;
    -k|--keep) KEEP=1 ;;
    -j|--jobs) [ "$#" -ge 2 ] || die "$1 needs a number"; JOBS="$2"; shift ;;
    -j*)       JOBS="${1#-j}" ;;
    --jobs=*)  JOBS="${1#--jobs=}" ;;
    -*)        die "unknown option $1 (see --help)" ;;
    *)         NAMES+=("$1") ;;
  esac
  shift
done
[[ "$JOBS" =~ ^[1-9][0-9]*$ ]] || die "--jobs must be a positive integer, got '$JOBS'"

case "$MODE" in
  list) list_scenarios; exit 0 ;;
  lint) lint_scenarios; exit $? ;;
esac

command -v claude >/dev/null 2>&1 || die "claude CLI not found on PATH"
command -v jq >/dev/null 2>&1 || die "jq not found on PATH"

if [ "${#NAMES[@]}" -eq 0 ]; then
  # shellcheck disable=SC2207  # scenario dirs are kebab-case; word splitting is safe
  NAMES=($(all_scenarios))
fi
for s in "${NAMES[@]}"; do
  [ -d "$SCEN_DIR/$s" ] || die "no such scenario: $s (run --list to see them)"
done

RUN_DIR="$(mktemp -d "${TMP_ROOT}/sdd-eval-run.XXXXXX")"
echo "${C_B}Running ${#NAMES[@]} scenario(s)${C_0}, $JOBS at a time${SDD_EVAL_MODEL:+, model $SDD_EVAL_MODEL}"
echo "${C_DIM}transcripts + judge prompts: $RUN_DIR${C_0}"
echo

started_all="$(date +%s)"
launched=0
printed=" "
flush_done() {   # print every finished-but-unprinted scenario, in completion order
  local s
  for s in "${NAMES[@]}"; do
    case "$printed" in *" $s "*) continue ;; esac
    [ -f "$RUN_DIR/$s/status" ] || continue
    print_result "$s"; printed="$printed$s "
  done
}
for s in "${NAMES[@]}"; do
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "$JOBS" ]; do flush_done; sleep 1; done
  mkdir -p "$RUN_DIR/$s"
  [ "$JOBS" -gt 1 ] && echo "${C_DIM}▶ $s${C_0}"
  [ "$JOBS" -eq 1 ] && echo "${C_DIM}▶ $s …${C_0}"
  ( run_scenario "$s" > "$RUN_DIR/$s/log" 2>&1 || true
    [ -f "$RUN_DIR/$s/status" ] || echo "ERROR 0 -" > "$RUN_DIR/$s/status" ) &
  launched=$((launched + 1))
done
wait
flush_done

# ---------- summary ----------
pass=0; fail=0
echo "${C_B}Summary${C_0}"
printf '  %-6s %-36s %6s  %s\n' STATUS SCENARIO TIME WORKDIR
for s in "${NAMES[@]}"; do
  read -r st secs work < "$RUN_DIR/$s/status"
  if [ "$st" = PASS ]; then pass=$((pass + 1)); col="$C_OK"; else fail=$((fail + 1)); col="$C_BAD"; fi
  printf '  %s%-6s%s %-36s %5ss  %s\n' "$col" "$st" "$C_0" "$s" "$secs" "$work"
done
echo
echo "$pass passed, $fail failed in $(( $(date +%s) - started_all ))s"
[ "$fail" -eq 0 ]
