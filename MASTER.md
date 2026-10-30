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

**Primary analyses (D-032):** the coalition test (D-013) and the gap (goal 2). Vote and case accuracy are reported but come second. See `docs/rung4_rung5_plan.md`.

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
| D-012 | 2026-10-30 16:11 CET | Method ladder: (1) baselines, (2) statistical model on case data, (3) general AI model asked "how would Justice X vote," (4) the same model given the justice's own past writing, (5) optional fine-tuned open-source model. Same test cases for every rung. | SUPERSEDED (by D-033) |
| D-013 | 2026-10-30 16:11 CET | High-level validity test: do the nine justice-models form the same voting coalitions as the real Court, especially the unusual cross-ideology ones? | ADOPTED (2026-10-30 18:08 CET, made a primary analysis by D-032) |
| D-014 | 2026-10-30 16:11 CET | Data-leakage fix: test prospectively on the October 2026 term, with predictions locked in git before each decision is released. | ADOPTED (2026-10-30) |
| D-015 | 2026-10-30 16:11 CET | Project folder is a git repository; commit history backs up this log. | ADOPTED |
| D-016 | 2026-10-30 16:21 CET | Data: Supreme Court Database release 2026_01 (terms 1946–2025), argued merits cases only. Development set: OT2018–OT2025 (475 cases), each term predicted only from earlier terms. | ADOPTED |
| D-017 | 2026-10-30 16:21 CET | Ideology baseline measures each justice's lean from their own past votes in the database (not external Martin-Quinn scores); appointing party is used only for a first term. Martin-Quinn is run side by side at key points as a comparison, with results reported whichever way they fall. | ADOPTED (2026-10-30 16:28) |
| D-018 | 2026-10-30 16:21 CET | For OT2026 cases we code each lower-court ruling's direction (conservative/liberal) ourselves, before the decision. Three independent coders (Claude + both team members) follow written rules; the averaged rating is the case's direction score and agreement sets its weight. Agreement is reported. | ADOPTED (2026-10-30 16:28) |
| R-001 | 2026-10-30 16:21 CET | Rung 1 results (`results/rung1_baselines.md`): "always petitioner" 67.2% of cases; ideology-only 50.3% of cases but 70.6% of votes in split decisions (vs 57.1%). Ideology predicts Roberts, Gorsuch, Kavanaugh and Barrett worst (54–56%). | RESULT |
| R-002 | 2026-10-30 16:33 CET | Rung 2 results (`results/rung2_model.md`): gradient-boosted trees on coded case facts reach 61.9% of cases, below "always petitioner" (67.2%); 63.0% of votes vs 61.4%. It predicts a petitioner win in 77% of cases, and when it predicts a loss it is right only 39% of the time: the coded facts do not identify which cases get affirmed. Martin-Quinn comparison pending (site down 2026-10-30). | RESULT |
| D-019 | 2026-10-30 16:33 CET | No tuning against the OT2018–OT2025 development terms. Any model tuning uses OT2010–OT2017 as a separate validation set; development numbers are reported once per model version. | PROPOSED |
| D-020 | 2026-10-30 16:58 CET | OT2026 case list (`data/ot2026/cases.csv`): every docket granted for argument as of 2026-10-30 (35). 34 are rated; 25-886 *Genalo* (dismissed) is not. Consolidated dockets (25-238 + 25-566) are rated separately because each has its own lower court. No original-jurisdiction cases this term. Later grants get added as new rows. | ADOPTED (2026-10-30 17:19) |
| D-021 | 2026-10-30 16:58 CET | Coding rules for lower-court direction (`docs/coding_rules.md`): imitate how SCDB coded `lcDispositionDirection`, including where that departs from everyday politics (e.g., preemption, religion, standing), because rungs 1–2 use that SCDB field. Worked examples are past cases with SCDB's actual codes. | ADOPTED (2026-10-30 17:19) |
| D-022 | 2026-10-30 17:09 CET | Human ratings are collected in a shared Google Doc ("OT2026 Lower-Court Direction Ratings", Drive folder "2. Education & Learning / Is Justice Blind", shared with Chuck Rutberg as editor) holding the case list, the coding rules and a Theo/Chuck rating table per case. Claude's ratings stay out of it (committed to git first). Known weakness: each rater can see the other's row, so independence depends on discipline. | ADOPTED (2026-10-30 17:19) |
| D-023 | 2026-10-30 17:27 CET | Rung 3 prompt `prompts/rung3/v1.txt`: one template for all 9 justices, name placed after the case materials; asks for reason, vote (petitioner/respondent), confidence 0.5-1, inputs relied on, and an "outcome_known" flag. Critique in `prompts/rung3/README.md`. Code refuses real runs until approved. | SUPERSEDED (by D-035) |
| D-024 | 2026-10-30 17:27 CET | Rung 3 inputs (`docs/rung3_collection_plan.md`): docket-page PDFs only, cut to a fixed 60k-token packet with fixed slots (QP, lower court 15k, merits briefs 12k+12k+5k, SG 4k, amici 8k, cert stage 4k). Predict once merits briefing ends, at the latest before the decision; minimal packet (QP + lower-court summary) as a labeled fallback. Needs `pypdf`. | PROPOSED |
| D-025 | 2026-10-30 17:27 CET | Rung 3 runner: each prompt answered by a fresh Claude process with no tools, no web, no project files (Claude Code CLI in print mode, Pro subscription, one-time login), model Sonnet 5.5. Alternative: Claude answers inside a session (no setup, but the session holds project context and sees the other justices' answers). API runner left as a stub; no API spending. | PROPOSED |
| D-026 | 2026-10-30 17:27 CET | Rung 3 scoring (`src/rung3_score.py`): a prediction counts only if committed to git, unchanged, and committed before the decision date. Decisions are entered in `data/ot2026/outcomes.csv` and `outcome_votes.csv` (each justice's vote and the opinions they joined, for D-013). Same metrics as rung 2 plus calibration and pairwise coalition agreement; all models scored on the same cases. | PROPOSED |
| R-003 | 2026-10-30 17:27 CET | Rung 3 pipeline test on two past cases (*Medical Marijuana v. Horn*, *Williams v. Reed*), answered in-session from memory: 100% correct, which shows the contamination problem, not skill. Labeled contaminated; never an accuracy number. | RESULT |
| D-027 | 2026-10-30 17:35 CET | Stay with all 9 justices for every rung. A Roberts-only design was considered (sharper test of reasoning, 9x cheaper) and rejected: too few votes per term to tell the rungs apart, it loses the coalition test (D-013), and results from one justice may not generalize. | ADOPTED (2026-10-30 17:35 CET) |
| D-028 | 2026-10-30 17:36 CET | Rung 4 prompt `prompts/rung4/v1.txt`: the rung 3 v1 prompt, plus a section after the justice's name with excerpts from that justice's past opinions and a "writings_relied_on" field. Critique in `prompts/rung4/README.md`. | SUPERSEDED (by D-035) |
| D-029 | 2026-10-30 17:36 CET | Rung 4 writings: only Supreme Court opinions the justice wrote (not just joined), issued before the prediction, never from the same case or dispute (D-009). Chosen per case by word-overlap similarity (TF-IDF) to the question presented and lower-court summary; 30k tokens per justice, at most 6k per opinion. Source: CourtListener. Narrows D-004 for now; the rest of that list can come later. | SUPERSEDED (by D-036) |
| D-030 | 2026-10-30 17:44 CET | Backup on GitHub: private repo `theodoregoodchildmichelman-collab/Is-Justice-Blind-`, branch `main`. Rung 3 pushed as a draft (prompt still PROPOSED). | ADOPTED (2026-10-30 17:44 CET) |
| D-031 | 2026-10-30 17:46 CET | Each finished rung 3 case is pushed to GitHub right after it is committed, because GitHub's record of the push is harder to fake than a local commit time. If a push fails, the script warns and the case stays locked locally until pushed by hand; `status` shows any locked case not yet pushed. | ADOPTED (2026-10-30 17:46 CET) |
| D-032 | 2026-10-30 18:08 CET | Emphasis: the coalition test (D-013) and the gap (goal 2) are the primary analyses for rungs 3-5; vote and case accuracy are secondary. Chosen after a search of earlier work (Hamilton 2023; Stillwell & Harrington 2026, who found AI accuracy comes mostly from ideology and that models predict too many divided decisions). | ADOPTED (2026-10-30 18:08 CET) |
| D-033 | 2026-10-30 18:08 CET | Ladder revised: rung 4 becomes a name x writings test (4N named + writings, 4B name hidden + writings, 4S name of one justice + writings of another); rung 5 becomes one round of deliberation (each justice reads the others' first answers) with a "think again alone" control, replacing fine-tuning. Rung 5 is reported apart from the one-model-per-justice rungs (D-007). | ADOPTED (2026-10-30 18:08 CET; details in D-034-D-037) |
| D-034 | 2026-10-30 18:08 CET | Rung 4-5 plan `docs/rung4_rung5_plan.md`: hypotheses H1-H5 fixed before any decision; main measure is the pair agreement gap (36 pairs, predicted vs actual), main comparison is which ingredient (name, writing, both, deliberation) brings it closest; coalition and gap measures; cost (~4.1M tokens per case) with a cut order; every rung for a case runs in one sitting before the decision; rung 4-5 code target 2026-11-20. Critique in the plan. | PROPOSED |
| D-035 | 2026-10-30 18:08 CET | Prompts: rung 3 `v2.txt` (adds `p_writes_separately`; "Base your prediction..." after the name), rung 4 `v2_named.txt` and `v2_blind.txt` (same opening, same writings, differ only in the justice's identity), `author_probe_v1.txt`. Critiques in `prompts/rung3/README.md` and `prompts/rung4/README.md`. | PROPOSED |
| D-036 | 2026-10-30 18:08 CET | Rung 4 writings: as D-029, plus a fixed mix (at least 2 opinions of the Court and 2 separate opinions when available), case names and all justices' names removed, labels like "Opinion 1 (2019, dissent)", and the same cleaned text in 4N, 4B and 4S. | PROPOSED |
| D-037 | 2026-10-30 18:08 CET | Gap coding: every vote missed by rungs 4N and 5 is coded by three raters (Theo, Chuck, Claude) into fixed categories (AI misread the case; narrow or procedural ground; collegial; precedent; own doctrine; unclear), from the published opinions only. Rules go in `docs/gap_coding_rules.md`, committed before the first OT2026 decision. Agreement reported. | PROPOSED |

## Team & resources

Two people. No formal legal training but well read in law. Basic coding, a little machine learning. Compute: a Claude Pro subscription ($20/month); no API budget or GPU yet.

## Open questions

- Read the full Stillwell & Harrington paper (SSRN, 2026) before adopting D-034: did they already test hiding the name or a deliberation round?
- Is a small pay-as-you-go API budget possible for scripted runs (rungs 3–4)? (Rung 3 can run on Pro via the CLI runner if D-025 is adopted.)
- Martin-Quinn file: download `justices.csv` from mqscores.wustl.edu (site down 2026-10-30) into `data/raw/mq/`, then rerun rung 2.
- Which Mac does the team have? (This decides whether open-source models can run locally.)
