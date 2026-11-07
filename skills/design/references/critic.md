# design — delta over the shared critic

Read [`../../allocations/critic.md`](../../allocations/critic.md) for the canonical dispatch (`subagent_type: "foresdd:critic"`, fallback `general-purpose` with the same prompt; clean context; Reads the draft + upstream files itself), the F1–F6 skeleton, the outcomes table and the resolution flow. design supplies only the deltas below; the skill fills the placeholders and dispatches.

## Placeholders

- **`{{ARTIFACT_NAME}}`** = "Software Architecture Document (Arc42 12 sections)".
- **`{{DRAFT_PATH}}`** = `docs/features/<slug>/sad.md` — the final post-Socratic SAD, already on disk (all 12 sections). Never inline its body.
- **`{{EDITS_LOG}}`** = the Socratic edits-log.
- **`{{EXTRA_INPUTS}}`** = the **ADR-spawns log** (`{adr_id, title, section, triggered_by}` per spawn) so the critic can cross-check which decisions became ADRs.
- **`{{UPSTREAM_FILES}}`** (the critic Reads these itself — paths only, never bodies):
  - `docs/features/<slug>/spec.md` — §2 Goals, §3 Non-goals, §6 NFR (numeric targets + measurement), §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, and any §1 ¶4 «Decision override» bullets.
  - `docs/features/<slug>/CONTEXT.md` — canonical glossary (roles, domain terms).
  - `docs/features/<slug>/adr/` — `ls` it, then read each ADR's Status / Title / Considered options / Decision outcome.
  - `docs/features/<slug>/.size` — the declared size class (F2).
- **`{{F5_FLOOR}}`** = the F5 section below. **`{{F6_RULES}}`** = the F6 section below. **`{{EXTRA_PROBES}}`** = the F1 specialization below.
- **Override slot** = `sad.md` §1 ¶4 («Decision override» bullets).

## F5 structural floor → `{{F5_FLOOR}}`

After applying all drops + OQ-migrations, the draft must still satisfy every line below — one finding per gap:

- All **12 Arc42 sections** filled with real content OR marked `<!-- N/A: <reason> -->`. An empty section with no N/A note is a gap.
- §3 has a real **`C4Context`** Mermaid block and §5 has a real **`C4Container`** Mermaid block — real names from CONTEXT + the brownfield scan, **not** template stubs (no `<placeholder>` substrings, no `Container_Bondary`/`ContainerBoundary` typos that render empty).
- §6 has **≥1 `sequenceDiagram`** Mermaid block (design seeds the primary flow(s); the `sequences` stage completes full §5-AC coverage — no cap).
- §9 ADR table is **closed against the `adr/` dir**: every file in `adr/` has a §9 row, every §9 row points to an existing file (no orphans either way).
- §11 carries a row for **every `save_as_oq`** entry in the edits-log, each with owner + due filled (literal `Open question` in the severity column).

## F6 specialization → `{{F6_RULES}}`

Three sub-probes — cite the offending line + the upstream source it contradicts for each hit:

- **NFR-number leak.** §10 Quality scenarios cite a number that is **not** in spec §6 NFR (an invented target — e.g. a p99 figure when the spec only specifies p95). The spec's numbers go in verbatim; no rounding, no inventing.
- **Strawman ADR.** Any ADR in `adr/` lists a `Considered options` line that an existing constraint already excludes (e.g. a datastore the §2/CONTEXT constraints rule out; a cache tier with no §4 strategic seed for it). Strawmen dilute the ADR genre.
- **§2-constraint-vs-repo contradiction.** §2 Constraints contradicts the repo's conventions (as reported by the step-3 brownfield scan / `architecture-map.md`, or the project convention file if known) **without** an Override note pointing at §11 Risks or a §1 ¶4 override bullet.

## F1 specialization — strategic-vector drift → `{{EXTRA_PROBES}}`

Compare §4 Solution strategy + §1 quality goals against §5–§10. If a §4 choice was Approved/Edited but a later section silently contradicts it (e.g. §4 picks async module coupling but the §6 happy-path flow shows a synchronous call with no emit step; §1's dominant quality goal is availability but every §10 scenario measures only latency), that is drift — cite the §4/§1 commitment + the contradicting draft line.
