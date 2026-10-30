# Rungs 4 and 5: overhaul plan (PROPOSED, D-034)

This plan replaces the old rung 4 (D-028, D-029) and rung 5 (fine-tuning, D-012). It was written
after a search of earlier work (below), and the team agreed on its direction on 2026-10-30
(D-032, D-033). The details are still open to critique.

## The two questions this project answers

Earlier projects have already asked "can an AI predict how a justice votes?" The answer is "somewhat,
mostly by knowing who is liberal and who is conservative." This project asks two questions that
earlier work hasn't answered. **Every rung is now built to answer them. Vote accuracy is still
reported, but it comes second.**

### 1. The coalition test: does the AI Court split the way the real Court does? (D-013)

The real Court is not a 6-3 machine. About 40% of its decisions are unanimous (197 of 475 in
OT2018-OT2025, from rung 1), and many split
decisions mix the blocs: Gorsuch with the liberals in a criminal or tribal case, Roberts and
Kavanaugh joining Kagan in a statutory case. Nine separate AI justices could each have a decent
accuracy score and still produce a Court that splits 6-3 on everything. The closest earlier study
(Stillwell & Harrington, OT2025) found that current AI models do that: they predict far too
many ideologically divided decisions.

So the first test of an AI Court is: **do its nine justices form the same groups as the real
nine?** We measure that in four ways (details under "How we score"):

- **Pair agreement (the main measure):** how often each of the 36 pairs of justices votes the
  same way, predicted vs actual.
- **Unanimity:** what share of cases the AI Court decides 9-0, vs the real Court.
- **Split type:** unanimous, a split along bloc lines, or a split that mixes the blocs. Can the AI
  predict mixed-bloc splits at all?
- **Who sits in the middle:** which justice is most often in the majority, predicted vs actual.

### 2. The gap: what do human justices do that their AI stand-in doesn't? (Goal 2)

Each rung adds one ingredient to the AI justice: its name (rung 3), its own past writing (rung 4),
the chance to read its colleagues' views (rung 5). After each ingredient, some votes are still
predicted wrong. **Those leftover misses are the gap, and they are the finding.** We ask:

- **Where is the gap?** Which justices, which kinds of cases, unanimous or split cases.
- **What closes it?** How much of the gap each ingredient removes: name, writing, deliberation.
- **What is left, and why?** Every vote the final AI Court gets wrong is coded by three raters
  (Theo, Chuck, Claude), using the published opinions, into fixed categories written down before
  the first decision (D-037). For example: the justice joined a colleague for the Court's sake,
  followed a precedent they had criticized, or decided on a narrow ground no one argued. One
  category is "the AI misread the case," so the AI's mistakes are kept apart from things the
  humans actually did.

The two questions connect: if the AI Court predicts too few unanimous decisions, and deliberation
(rung 5) fixes that, then part of the gap is **collegiality**, something judges do as a group
that no model of one justice can capture.

## What earlier work did (and what we must check)

| Work | What it did | How we differ |
|---|---|---|
| Hamilton, *Blind Judgement* (2023) | 9 models, each trained on one justice's opinions; 96 past cases; better than chance | We test ahead of time, not on past cases, and we separate the name from the writing |
| Stillwell & Harrington (SSRN, 2026) | 4 frontier models on all OT2025 cases | They found accuracy came mostly from ideology and too many divided decisions predicted; our coalition test and rung 5 go after exactly that |
| Berkeley *Court Logic* (2026) | Retrieval plus simulated deliberation, 13 cases | We compare deliberation against a "think again alone" control and score it on coalitions |

**Before this plan is adopted:** read the full Stillwell & Harrington paper. If they already ran
something like the name-hidden test or a deliberation round, we change course. (So far we've only
seen summaries of it.)

## The new ladder

| Rung | The AI justice gets | Answers | Prompts per case |
|---|---|---|---|
| 3 | Case materials + its name | Vote, confidence, chance of writing separately | 9 |
| 4N named | + its own past writing | same + writings relied on | 9 |
| 4B blind | Case materials + past writing, name hidden ("Justice A") | same | 9 |
| 4S swap | Name of one justice + writing of another (4 justices) | same | 4 |
| 5 deliberation | Rung 4N + the other 8 justices' first answers | final vote, changed or not | 9 |
| 5C control | Rung 4N + its own first answer only, asked to think again | same | 9 |

Rungs 3 and 4N together with 4B make a 2x2: name yes/no x writing yes/no (the "no name, no
writing" cell would be 9 identical prompts, so it's left out). The swap and the control are
there to tell explanations apart, as described below.

## Rung 4: name or writing? (D-033, D-035, D-036)

**The question:** when the AI predicts a justice's vote, is it reasoning from the justice's
jurisprudence or repeating their reputation? And which of the two produces the real Court's
coalitions?

### Conditions

- **4N named:** rung 3 plus the writings. Prompt `prompts/rung4/v2_named.txt`.
- **4B blind:** the same writings, the same case materials, but the justice is "Justice A" and the
  model is told not to try to identify them. Prompt `prompts/rung4/v2_blind.txt`.
- **4S swap:** the named prompt, with another justice's writings. Two pairs, both directions, every
  case:
  - Thomas and Sotomayor (opposite ends of the Court: does the name or the writing win?)
  - Gorsuch and Alito (same bloc, different doctrine: can the writing move a vote within a bloc,
    which is where mixed-bloc coalitions come from?)

  We report, for each swapped prompt, whether the vote follows the name or the writing.
- **Author probe (6 cases):** the blind writings alone, with the question "which current justice
  wrote these?" (`prompts/rung4/author_probe_v1.txt`). If the model names the author most of the
  time, the blind condition isn't really blind, and we say so instead of hiding it.

### The writings (changes from D-029)

Kept from D-029: only opinions the justice wrote on the Supreme Court; issued before the
prediction; nothing from the same case or dispute; chosen by word-overlap similarity (TF-IDF) to the
question presented and lower-court summary; 30k tokens per justice, 6k per opinion; CourtListener.

Changed:

1. **Fixed mix.** At least 2 opinions of the Court and at least 2 separate opinions (concurrences,
   dissents, statements) when the justice has written them; the rest by similarity. Concurrences and
   dissents are written when a justice parts from colleagues, so a set of only those makes every
   justice look more isolated than they are, which pushes the AI Court toward too many splits:
   the very error the coalition test measures.
2. **Names taken out.** Case names, the author line ("JUSTICE GORSUCH, concurring"), and every
   justice's name inside the text are replaced with "[a justice]". Each excerpt is labeled
   "Opinion 1 (2019, dissent)". Without this, a label like "*Bruen*, opinion of the Court" tells the
   model the author is Thomas.
3. **Same text in every condition.** 4N, 4B and 4S use the exact same cleaned writings, so the only
   difference between 4N and 4B is the name.

### What rung 4 tells us (hypotheses, fixed before any decision)

- **H1:** the named conditions (3, 4N) predict fewer unanimous cases and more bloc-line splits than
  the real Court. The blind condition (4B) predicts fewer bloc-line splits than 4N.
- **H2:** the writing (4N and 4B) predicts mixed-bloc splits better than the name alone (rung 3).
- **H3 (swap):** for Thomas and Sotomayor the name wins; for Gorsuch and Alito the writing moves
  votes more often.

Whatever happens, each result goes into the gap analysis: the 4B vs 4N difference is how much of
the AI's skill (and its errors) comes from reputation.

## Rung 5: one round of deliberation (D-033)

**The question:** after the justices vote independently, does letting each one read the others'
views make the AI Court's coalitions more like the real Court's, especially on unanimity?
If so, part of the gap is collegiality.

### How it works

1. Rung 4N runs first: 9 independent answers.
2. **Deliberation (5):** each justice gets its own rung 4N prompt word for word, its own first
   answer, then the other eight justices' first votes and reasons, in order of seniority (the order
   they speak at the Court's real conference). It is asked for a final vote and may keep or change
   it. The prompt does not push either way.
3. **Control (5C):** the same, but without the colleagues' answers: "think about it once more." Any
   change from simply thinking twice shows up here, so the deliberation effect is 5 minus 5C.
4. One round only. Second-round answers never see each other.
5. The case prediction is the majority of the 9 final votes.

Building on rung 4N (not 4B) because the conference is among known colleagues. The rung 5
prompt (`prompts/rung5/v1.txt`) is drafted only after the rung 4 prompts are agreed, since it
contains them.

### Hypotheses

- **H4:** rung 5 moves the predicted unanimity rate toward the real one and lowers the pair
  agreement gap, by more than the control 5C does.
- **H5 (the risk):** deliberation overshoots. The majority's view pulls in everyone and the AI
  Court becomes unanimous too often. We report it either way.

Rung 5 is reported separately from the one-model-per-justice rungs (D-007): its justices aren't
independent.

## How we score (D-034)

All rungs are scored on the same cases: those with every rung locked before the decision.

### Main measure (decided now, before any data)

**Pair agreement gap:** for each of the 36 pairs of justices, the share of cases where they voted
the same way; the measure is the average distance between predicted and actual over the 36 pairs
(0 = the AI Court's alliances match the real Court's exactly). Already computed in
`src/rung3_score.py`. Reported for every rung, with a 95% interval from resampling cases, and the
paired difference between rungs.

The main comparison: **which ingredient brings the AI Court's alliances closest to the real
Court's: name (3), writing (4B), both (4N), or deliberation (5)?**

### Coalition measures (secondary)

| Measure | What it is |
|---|---|
| Unanimity rate | Share of cases with no dissent, predicted vs actual |
| Split type | Each case labeled unanimous / one-bloc dissent (all dissenters from the same bloc, e.g. the classic 6-3) / mixed-bloc dissent; table of predicted vs actual type |
| Mixed-bloc recall | Of the real mixed-bloc splits, how many the AI Court predicted as mixed-bloc |
| Middle of the Court | Each justice's share of votes in the majority, predicted vs actual; who ranks first |

Blocs for this purpose: Roberts, Thomas, Alito, Gorsuch, Kavanaugh, Barrett / Sotomayor, Kagan,
Jackson (by appointing party, fixed now).

### Gap measures

| Measure | What it is |
|---|---|
| Gap by justice | Share of each justice's votes the rung gets wrong |
| Beyond ideology | Accuracy on the votes where the ideology baseline (B1) is wrong |
| What closes the gap | Change in each justice's misses from 3 to 4B, 4N, 5 |
| Direction of misses | Whether a justice's misses lean one way in an issue area (e.g., the AI keeps placing Gorsuch on the government's side in criminal cases) |
| Coded misses (D-037) | Every miss in rungs 4N and 5, coded into fixed categories by 3 raters; agreement reported |

### Also scored

Case and vote accuracy (as rungs 1-3), calibration of confidence, and the new
`p_writes_separately` against who actually wrote a concurrence or dissent.

### Reference points we can compute now, without any AI

The coalition measures for B0, B1 and R2 on the development terms (OT2018-OT2025): how often does
an ideology-only Court come out unanimous, how often mixed-bloc? That tells us what "just ideology"
produces before the AI rungs are scored.

### The honest limit

About 35 cases. A 95% interval on case accuracy is about +/-16 points; pair agreement is steadier
but still rough. Comparing rungs on the same cases helps. We name one main comparison in advance
(above) and call the rest exploratory.

## Gap coding rules (D-037, written before the first decision)

`docs/gap_coding_rules.md`, to be written and committed before the first OT2026 decision (late
November at the earliest). Draft categories, one per missed vote:

1. **AI misread the case:** the AI's reason gets the law or the facts wrong. An AI failure, not
   something the justice did.
2. **Narrow or procedural ground:** the justice decided on a ground the AI didn't foresee
   (jurisdiction, dismissal, vacate and remand on a different standard).
3. **Collegial:** the justice voted with a majority or unanimous Court against the AI's expected
   lean, without writing separately, or writing only to note reservations.
4. **Precedent:** the justice followed a precedent they have criticized.
5. **Own doctrine:** the justice's consistent method or commitment (textualism, a view of
   criminal procedure) cut against the side the AI expected; shown in their separate writing.
6. **Unclear.**

Three raters code each miss independently from the opinions only, as with direction ratings
(D-018); agreement is reported.

## Cost on the Pro subscription

Input tokens per case (1 token is about 3/4 of a word):

| Part | Prompts | Tokens each | Per case |
|---|---|---|---|
| Rung 3 | 9 | 60k | 0.5M |
| Rung 4N | 9 | 90k | 0.8M |
| Rung 4B | 9 | 90k | 0.8M |
| Rung 4S swap | 4 | 90k | 0.4M |
| Rung 5 | 9 | ~92k | 0.8M |
| Rung 5C control | 9 | ~92k | 0.8M |
| **Total** | 49 | | **~4.1M** |

For 35 cases that is about 145M tokens before savings, plus about 1.6M for the author probe.
Within a case every rung 4 and 5 prompt begins with the same 60k of case materials, and rung 5
begins with the whole rung 4N prompt, so much of it can be reused from a cache. We don't know how
cached tokens count against Pro usage limits. **First step: run one dev case through all rungs and
measure how much of the weekly limit it uses.**

If it doesn't fit, cut in this order (last = cut first):

1. Rungs 3, 4N, 4B on every case (never cut: the 2x2)
2. Rung 5 and 5C on every case
3. Swap on every case → swap on half the cases
4. Writings 30k → 20k per justice (applies to all rung 4-5 conditions alike)

Or settle the open question in MASTER.md: a small API budget for scripted runs. Price it with
current published rates before deciding.

## Timing

Every rung for a case has to be locked before that case is decided. Cases argued in October can be
decided from late November. So:

- **Each case runs through all rungs in one sitting**, in argument order, then is committed and
  pushed (D-031).
- If rung 4-5 code isn't ready when an early case must be predicted, that case gets rung 3 only
  and drops out of the rung comparison (the scorer compares rungs only on shared cases). Target:
  rung 4 and 5 code working on the dev cases by **2026-11-20**.

## Build steps

| # | Step | Files | Needs |
|---|---|---|---|
| 1 | Read the full Stillwell & Harrington paper; adjust this plan | this file | - |
| 2 | Critique round on this plan and the prompts; log the outcome | `MASTER.md` | team |
| 3 | Coalition reference points for B0/B1/R2 on OT2018-OT2025 | `src/coalitions.py`, `results/coalition_baselines.md` | - |
| 4 | Switch rung 3 to prompt v2 (new field `p_writes_separately`) | `src/rung3_predict.py` | step 2 |
| 5 | Fetch each justice's opinions from CourtListener; clean names; pick by similarity with the fixed mix | `src/writings.py`, `data/writings/` | free CourtListener account |
| 6 | Rung 4 runner: 4N, 4B, 4S, author probe; same locking as rung 3 | `src/rung4_predict.py` | steps 4-5 |
| 7 | Rung 5 prompt and runner: deliberation + control | `prompts/rung5/v1.txt`, `src/rung5_predict.py` | step 6 |
| 8 | One dev case through all rungs; measure usage | `predictions/*_contaminated/` | steps 6-7 |
| 9 | Gap coding rules, committed before the first decision | `docs/gap_coding_rules.md` | team |
| 10 | Scorer for all rungs: coalition and gap measures | `src/score_ot2026.py` (replaces `rung3_score.py`) | step 3 |

## Steelman case against this plan

- **35 cases may be too few to see anything.** Differences between rungs on pair agreement may
  sit inside the error band. Then the paper reports a well-measured null, plus the descriptive
  coalition and gap findings, which is still worth publishing but less exciting.
- **The blind condition may not be blind.** Opinions by Thomas or Gorsuch are recognizable by
  style, and the model has likely read them all. The author probe measures this, but if
  recognition is high, H1-H3 can't be cleanly tested.
- **The swap condition lies to the model.** It says the writings are by one justice when they
  aren't. That's the point of the test, but a reviewer may see it as an artificial setup, and the
  model may notice the mismatch and react oddly. Recorded as a design choice.
- **Deliberation is a weak copy of the real thing.** Real justices circulate drafts over months,
  bargain over wording, and the Chief assigns opinions. One round of reading eight short reasons
  is not that. If rung 5 fails, it doesn't show collegiality doesn't matter, only that this version
  doesn't capture it.
- **Coding the gap is subjective.** "Collegial" vs "own doctrine" is a judgment call, and raters
  who know the AI's prediction may be biased. Fixed categories, independent raters and reported
  agreement limit this but don't remove it.
- **Cost.** At ~4M tokens per case, the full plan may not fit on Pro. The cut order above protects
  the 2x2, but losing rung 5 would remove the cleanest test of the collegiality explanation.
- **Bloc labels by appointing party are crude.** Roberts or Barrett in a "conservative bloc" is a
  simplification; mixed-bloc splits are defined against that line. It is fixed in advance so it
  can't be tuned, at the cost of nuance.
