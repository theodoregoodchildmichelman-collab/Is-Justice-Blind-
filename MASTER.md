# Is Justice Blind — Master Log

Short manifest of every major project decision. One line per entry where possible; newest at the bottom.
Purpose: nothing slips through the cracks, and the project history can later become the methods section of a paper.

## Process rule

Nothing becomes part of the real project until it has gone through:
**Proposal → Claude's steelman critique → team response → consensus → logged as ADOPTED.**

Statuses: `PROPOSED` · `UNDER CRITIQUE` · `ADOPTED` · `REJECTED` · `SUPERSEDED (by D-xxx)` · `RESULT` (R-xxx rows record findings)

## Goals

1. **Prediction:** build models that predict U.S. Supreme Court outcomes and individual justices' votes.
2. **The gap:** compare each human justice with an AI stand-in, measured empirically, to find what (if anything) human judges do that the model cannot.

## Decision log

| ID | Date & time | Decision | Status |
|----|-------------|----------|--------|
| D-001 | 2026-10-30 16:01 CET | Project started. Goals 1 and 2 above. | ADOPTED |
| D-002 | 2026-10-30 16:01 CET | Critique-before-adoption process (see Process rule). | ADOPTED |
| D-003 | 2026-10-30 16:01 CET | `MASTER.md` in the project root is the single decision log. | ADOPTED |
| D-004 | 2026-10-30 16:01 CET | Per-justice models for the 9 sitting justices, trained on: every opinion the justice wrote, every case those opinions cite, their law review articles, and the works those articles cite. | UNDER CRITIQUE |
| D-005 | 2026-10-30 16:01 CET | Hold out the most recent 2 terms of decisions as the test set; train only on earlier material. | SUPERSEDED (by D-014) |
| D-006 | 2026-10-30 16:01 CET | Candidate methods: (a) classic machine learning on case features, (b) language models trained or conditioned on each justice's corpus. | SUPERSEDED (by D-012) |
| D-007 | 2026-10-30 16:11 CET | Primary goal: one model per justice that approximates that justice's reasoning, beyond "conservative or liberal." Case prediction is secondary and may later split into its own track. | ADOPTED |
| D-008 | 2026-10-30 16:11 CET | Targets: (1) case win/loss, (2) each justice's vote. Opinion text and reasoning matter but are secondary. | ADOPTED |
| D-009 | 2026-10-30 16:11 CET | At prediction time the model may use only material from outside the Court: cert petition, merits and amicus briefs, lower-court opinions. No oral argument, and nothing a justice said or wrote about that case. | ADOPTED |
| D-010 | 2026-10-30 16:11 CET | "Always reverse" is the first baseline every model must beat. | ADOPTED |
| D-011 | 2026-10-30 16:11 CET | Target: a standard academic paper (empirical / computational social science), not a law review. | ADOPTED |
| D-012 | 2026-10-30 16:11 CET | Method ladder: (1) baselines, (2) statistical model on case data, (3) general AI model asked "how would Justice X vote," (4) the same model given the justice's own past writing, (5) optional fine-tuned open-source model. Same test cases for every rung. | UNDER CRITIQUE |
| D-013 | 2026-10-30 16:11 CET | High-level validity test: do the nine justice-models form the same voting coalitions as the real Court, especially the unusual cross-ideology ones? | UNDER CRITIQUE |
| D-014 | 2026-10-30 16:11 CET | Data-leakage fix: test prospectively on the October 2026 term, with predictions locked in git before each decision is released. | ADOPTED (2026-10-30) |
| D-015 | 2026-10-30 16:11 CET | Project folder is a git repository; commit history backs up this log. | ADOPTED |
| D-016 | 2026-10-30 16:21 CET | Data: Supreme Court Database release 2026_01 (terms 1946–2025), argued merits cases only. Development set: OT2018–OT2025 (475 cases), each term predicted only from earlier terms. | ADOPTED |
| D-017 | 2026-10-30 16:21 CET | Ideology baseline measures each justice's lean from their own past votes in the database (not external Martin-Quinn scores); appointing party is used only for a first term. | PROPOSED |
| D-018 | 2026-10-30 16:21 CET | For OT2026 cases we must code each lower-court ruling's direction (conservative/liberal) ourselves, before the decision, because the database adds it only afterward. | PROPOSED |
| R-001 | 2026-10-30 16:21 CET | Rung 1 results (`results/rung1_baselines.md`): "always petitioner" 67.2% of cases; ideology-only 50.3% of cases but 70.6% of votes in split decisions (vs 57.1%). Ideology predicts Roberts, Gorsuch, Kavanaugh and Barrett worst (54–56%). | RESULT |

## Team & resources

Two people. No formal legal training but well read in law. Basic coding, a little machine learning. Compute: a Claude Pro subscription ($20/month); no API budget or GPU yet.

## Open questions

- Is a small pay-as-you-go API budget possible for scripted runs (rungs 3–4)?
- Which Mac does the team have? (This decides whether open-source models can run locally.)
