#!/usr/bin/env python3
"""Structural lint for ```mermaid blocks in Markdown files — stdlib only, deterministic.

Used by skills/allocations/mermaid-check.md. It is NOT a full Mermaid parser (that is `mmdc`);
it catches the breakages the pipeline actually hits plus house rules a real parser accepts
(e.g. a misspelled C4 boundary renders as an empty box instead of failing).

Usage:
  mermaid_lint.py FILE [FILE ...]            lint every block
  mermaid_lint.py FILE --only 40-80          only blocks whose opening fence is in lines 40-80
                                             fail the run; findings elsewhere are reported as
                                             `note (out of scope)` and never change the exit code
  mermaid_lint.py FILE --list                list blocks (index, fence line, diagram type)

Output: one finding per line, `path:line: error|warning [type] message — fix hint`, then a summary.
Exit: 0 = no in-scope errors (warnings allowed) · 1 = in-scope errors · 2 = usage / unreadable file.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KNOWN_TYPES = {
    "graph", "flowchart", "sequenceDiagram", "classDiagram", "classDiagram-v2", "erDiagram",
    "stateDiagram", "stateDiagram-v2", "C4Context", "C4Container", "C4Component", "C4Dynamic",
    "C4Deployment", "journey", "gantt", "pie", "mindmap", "timeline", "gitGraph", "quadrantChart",
    "requirementDiagram", "sankey-beta", "xychart-beta", "block-beta", "packet-beta",
    "architecture-beta", "kanban", "radar-beta",
}
HTML_TAGS = {"br", "b", "i", "u", "em", "strong", "sub", "sup", "small", "code", "span", "p"}
# sequences' fixed generic participant vocabulary (skills/sequences/SKILL.md step 3) — intentional, not leftovers
GENERIC_PARTICIPANTS = {"client", "ui", "user", "service", "data-store", "external-system", "message-bus"}
PLACEHOLDER = re.compile(r"(?<!<)<([A-Za-z][A-Za-z0-9 _.-]*)>(?!>)")
QUOTED = re.compile(r'"[^"]*"')

C4_ELEMENT = re.compile(
    r"^\s*(Person|Person_Ext|System|System_Ext|SystemDb|SystemDb_Ext|SystemQueue|SystemQueue_Ext|"
    r"Container|Container_Ext|ContainerDb|ContainerDb_Ext|ContainerQueue|ContainerQueue_Ext|"
    r"Component|Component_Ext|ComponentDb|ComponentDb_Ext|ComponentQueue|ComponentQueue_Ext|"
    r"Boundary|Enterprise_Boundary|System_Boundary|Container_Boundary|Deployment_Node|Node|Node_L|Node_R)"
    r"\s*\(\s*([^,\s)]+)")
C4_REL = re.compile(r"^\s*(Rel|BiRel|Rel_[UDLR]|Rel_Up|Rel_Down|Rel_Left|Rel_Right|Rel_Back|Rel_Neighbor)\s*\((.*)\)\s*$")
C4_TYPOS = {
    "Container_Bondary": "Container_Boundary", "System_Bondary": "System_Boundary",
    "ContainerBoundary": "Container_Boundary", "SystemBoundary": "System_Boundary",
    "Enterprise_Bondary": "Enterprise_Boundary",
}

ER_CARD = r"(?:\|o|\|\||\}o|\}\|)(?:--|\.\.)(?:o\||\|\||o\{|\|\{)"
ER_NAME = r"(?:[\w-]+|<[^<>]+>)"  # <ENTITY> placeholders are reported by the placeholder check
ER_REL = re.compile(rf"^\s*{ER_NAME}\s+{ER_CARD}\s+{ER_NAME}\s*:\s*\S")
ER_KEYS = {"PK", "FK", "UK"}

SEQ_OPENERS = {"alt", "opt", "loop", "par", "critical", "break", "rect", "box"}
UNICODE_ARROWS = "→←↔⇒⇐⇔⟶⟵"
FLOW_ARROW = re.compile(r"(-->|---|-\.->|-\.-|==>|===|--[ox]|<-->|~~~|--\s*\|)")


@dataclass
class Finding:
    line: int
    level: str  # error | warning
    message: str


@dataclass
class Block:
    index: int
    fence_line: int           # 1-based line of the opening ```mermaid
    lines: list[str] = field(default_factory=list)
    closed: bool = True
    dtype: str = ""
    body_start: int = 0       # offset into `lines` of the type-declaration line


def extract_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    cur: Block | None = None
    for no, raw in enumerate(text.splitlines(), start=1):
        s = raw.strip()
        if cur is None:
            if re.match(r"^```\s*mermaid\s*$", s):
                cur = Block(index=len(blocks) + 1, fence_line=no)
        elif s.startswith("```"):
            blocks.append(cur)
            cur = None
        else:
            cur.lines.append(raw)
    if cur is not None:
        cur.closed = False
        blocks.append(cur)
    for b in blocks:
        b.dtype, b.body_start = detect_type(b.lines)
    return blocks


def detect_type(lines: list[str]) -> tuple[str, int]:
    i, n = 0, len(lines)
    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].strip() == "---":           # YAML frontmatter (title/config)
        i += 1
        while i < n and lines[i].strip() != "---":
            i += 1
        i += 1
    while i < n and (not lines[i].strip() or lines[i].strip().startswith("%%")):
        i += 1                                       # blank, %% comments, %%{init}%% directives
    if i >= n:
        return "", i
    return lines[i].strip().split()[0], i


def strip_comment(line: str) -> str:
    return "" if line.strip().startswith("%%") else line


def lint_block(b: Block) -> list[Finding]:
    out: list[Finding] = []
    L = lambda off: b.fence_line + 1 + off  # noqa: E731 — file line of lines[off]

    if not b.closed:
        out.append(Finding(b.fence_line, "error", "unclosed ```mermaid fence — add the closing ``` line"))
    if not b.dtype:
        out.append(Finding(b.fence_line, "error", "empty diagram — no type declaration"))
        return out
    if b.dtype not in KNOWN_TYPES:
        out.append(Finding(L(b.body_start), "error",
                           f"unknown diagram type '{b.dtype}' — first line must be e.g. flowchart LR, "
                           f"sequenceDiagram, erDiagram, C4Context"))
        return out

    body = list(enumerate(b.lines))[b.body_start + 1:]
    for off, raw in body:
        line = strip_comment(raw)
        if not line.strip():
            continue
        for m in PLACEHOLDER.finditer(line):
            tag = m.group(1).strip().rstrip("/").split()[0].lower()
            if tag in HTML_TAGS or m.group(1).strip() in GENERIC_PARTICIPANTS:
                continue
            out.append(Finding(L(off), "error",
                               f"leftover template placeholder '{m.group(0)}' — replace with the real name"))
        if QUOTED.sub("", line).count('"') % 2:
            out.append(Finding(L(off), "error",
                               "unbalanced double quote — close it, or write a literal quote as #quot;"))

    t = b.dtype
    if t in ("graph", "flowchart"):
        out += lint_flowchart(body, L)
    elif t == "sequenceDiagram":
        out += lint_sequence(body, L)
    elif t.startswith("C4"):
        out += lint_c4(body, L)
    elif t == "erDiagram":
        out += lint_er(body, L)
    return out


def bracket_balance(text: str) -> bool:
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def lint_flowchart(body, L) -> list[Finding]:
    out, depth = [], 0
    label_unquoted = re.compile(r"[\w-]+\[(?![\"(\[/\\])([^\]\"]*)\]")
    for off, raw in body:
        line = strip_comment(raw).strip()
        if not line:
            continue
        if re.match(r"^subgraph\b", line):
            depth += 1
            continue
        if line == "end":
            depth -= 1
            if depth < 0:
                out.append(Finding(L(off), "error", "'end' without a matching 'subgraph'"))
                depth = 0
            continue
        bare = QUOTED.sub('""', line)
        bare = re.sub(r"\|[^|]*\|", "||", bare)            # edge labels  -->|text|
        bare = re.sub(r"<[A-Za-z/][^<>]*>", "", bare)       # <br>, <placeholder> (reported separately)
        bare = re.sub(r"(?<![<\w-])\w+>[^\]]*\]", "x", bare)       # asymmetric shape  A>text]
        if not bracket_balance(re.sub(r"[<>]", "", bare)):
            out.append(Finding(L(off), "error",
                               "unbalanced brackets — node shapes must close with the matching "
                               "bracket ([] () {} [[ ]] [( )] {{ }})"))
        if FLOW_ARROW.search(bare) and re.search(r"(^|[\s;&>|-])end($|[\s;&\[({-])", bare):
            out.append(Finding(L(off), "error",
                               "lowercase 'end' used as a node id breaks the flowchart — rename it "
                               "(e.g. End or done)"))
        if re.search(r"[-=.]-[ox][A-Za-z0-9_]", bare):
            out.append(Finding(L(off), "warning",
                               "edge directly followed by a node id starting with 'o'/'x' is read as a "
                               "circle/cross edge — add a space (A --- oNode) or rename the node"))
        for m in label_unquoted.finditer(line):
            if re.search(r"[(){}]", m.group(1)):
                out.append(Finding(L(off), "error",
                                   f"unquoted label '{m.group(1)}' contains brackets — wrap it in quotes: "
                                   f'["{m.group(1)}"]'))
    if depth > 0:
        out.append(Finding(L(body[-1][0]) if body else 0, "error",
                           f"{depth} 'subgraph' without a closing 'end'"))
    return out


def lint_sequence(body, L) -> list[Finding]:
    out, stack = [], []
    for off, raw in body:
        if raw.strip().startswith("%%"):
            continue
        line = raw.strip()
        if not line:
            continue
        word = line.split()[0]
        if word in SEQ_OPENERS:
            stack.append((word, off))
        elif word in ("else", "and", "option"):
            parent = {"else": {"alt"}, "and": {"par"}, "option": {"critical"}}[word]
            if not stack or stack[-1][0] not in parent:
                out.append(Finding(L(off), "error",
                                   f"'{word}' outside a matching {'/'.join(sorted(parent))} block"))
        elif word == "end":
            if not stack:
                out.append(Finding(L(off), "error", "'end' without an open alt/opt/loop/par/critical/break/rect/box"))
            else:
                stack.pop()
        if "%%" in line:
            out.append(Finding(L(off), "error",
                               "inline '%%' comment on a statement line — move the comment to its own line"))
        is_text_line = ":" in line and (re.search(r"-[->x)]|->>", line) or word == "Note")
        if is_text_line:
            text = line.split(":", 1)[1]
            if ";" in text:
                out.append(Finding(L(off), "error",
                                   "';' in message/Note text is a statement separator — use ',' or "
                                   "'and' instead"))
            if any(a in text for a in UNICODE_ARROWS):
                out.append(Finding(L(off), "warning",
                                   "Unicode arrow in text — some renderers choke; use words ('then', 'to')"))
    for word, off in stack:
        out.append(Finding(L(off), "error", f"'{word}' block never closed — add 'end'"))
    return out


def lint_c4(body, L) -> list[Finding]:
    out, declared = [], set()
    for off, raw in body:
        line = strip_comment(raw)
        if not line.strip():
            continue
        for bad, good in C4_TYPOS.items():
            if re.search(rf"\b{bad}\b", line):
                out.append(Finding(L(off), "error",
                                   f"'{bad}' is not a C4 keyword (renders an empty box) — use '{good}'"))
        m = C4_ELEMENT.match(line)
        if m:
            ident = m.group(2).strip("\"'")
            if " " in ident:
                out.append(Finding(L(off), "error", f"C4 id '{ident}' contains a space — ids must be one word"))
            declared.add(ident)
            continue
        r = C4_REL.match(line)
        if r:
            args = [a.strip().strip("\"'") for a in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", r.group(2))]
            if len(args) < 3 or not args[2]:
                out.append(Finding(L(off), "error",
                                   f"{r.group(1)} needs a quoted label: {r.group(1)}(from, to, \"what it does\")"))
            for ident in args[:2]:
                if ident and ident not in declared:
                    out.append(Finding(L(off), "error",
                                       f"{r.group(1)} references '{ident}' before it is declared — declare the "
                                       f"Person/System/Container first"))
    return out


def lint_er(body, L) -> list[Finding]:
    out, in_entity = [], False
    for off, raw in body:
        line = strip_comment(raw).strip()
        if not line:
            continue
        if in_entity:
            if line.startswith("}"):
                in_entity = False
                continue
            no_comment = QUOTED.sub("", line).split()
            if len(no_comment) < 2:
                out.append(Finding(L(off), "error",
                                   f"attribute line '{line}' must be 'type name [PK|FK|UK] [\"comment\"]'"))
                continue
            keys = " ".join(no_comment[2:]).replace(" ", "")
            if keys:
                for k in keys.split(","):
                    if k and k not in ER_KEYS:
                        hint = " — 'PK_FK' is invalid, write 'PK, FK'" if k == "PK_FK" else ""
                        out.append(Finding(L(off), "error",
                                           f"invalid attribute key '{k}' (only PK, FK, UK){hint}"))
            continue
        if re.match(rf"^{ER_NAME}(\s*\[[^\]]*\])?\s*\{{\s*$", line):
            in_entity = True
            continue
        if re.match(r"^(direction|title|accTitle|accDescr)\b", line):
            continue
        if re.match(r"^[\w-]+\s+\S+\s+[\w-]+", line) or "--" in line or ".." in line:
            if not ER_REL.match(line):
                out.append(Finding(L(off), "error",
                                   "relationship must be 'A <card>--<card> B : \"label\"' with valid cardinality "
                                   "glyphs (||--o{, }o--||, |o..o|, …)"))
    if in_entity:
        out.append(Finding(L(body[-1][0]), "error", "entity block '{' never closed — add '}'"))
    return out


def parse_ranges(specs: list[str]) -> list[tuple[int, int]]:
    ranges = []
    for s in specs:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", s.strip())
        if not m:
            raise ValueError(f"bad --only range '{s}' (expected N or N-M)")
        a = int(m.group(1))
        ranges.append((a, int(m.group(2) or a)))
    return ranges


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Structural lint for ```mermaid blocks in Markdown.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--only", action="append", default=[], metavar="N-M",
                    help="scope: only blocks whose opening fence is in these lines can fail the run")
    ap.add_argument("--list", action="store_true", help="list blocks and exit")
    args = ap.parse_args(argv)
    try:
        ranges = parse_ranges(args.only)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    total = errors = warnings = notes = 0
    for f in args.files:
        p = Path(f)
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as e:
            print(f"{f}: cannot read ({e})", file=sys.stderr)
            return 2
        blocks = extract_blocks(text)
        if args.list:
            for b in blocks:
                print(f"{f}:{b.fence_line}: block {b.index} {b.dtype or '(empty)'}")
            continue
        for b in blocks:
            total += 1
            in_scope = not ranges or any(a <= b.fence_line <= z for a, z in ranges)
            for fd in sorted(lint_block(b), key=lambda x: x.line):
                label = f"[{b.dtype or 'mermaid'}]"
                if not in_scope:
                    notes += 1
                    print(f"{f}:{fd.line}: note (out of scope, pre-existing) {label} {fd.message}")
                elif fd.level == "error":
                    errors += 1
                    print(f"{f}:{fd.line}: error {label} {fd.message}")
                else:
                    warnings += 1
                    print(f"{f}:{fd.line}: warning {label} {fd.message}")
    if args.list:
        return 0
    print(f"mermaid-lint: {total} block(s), {errors} error(s), {warnings} warning(s)"
          + (f", {notes} out-of-scope note(s)" if notes else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
