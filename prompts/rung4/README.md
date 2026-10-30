# Rung 4 prompts

Rung 4 (D-012) is rung 3 plus each justice's own past writing. To make the two rungs a clean
comparison, the rung 4 template is the rung 3 v1 template with one section added (the writings) and
three sentences that mention them; everything else is word for word the same. Any gap between rung 3 and rung 4 should come from the writings.

| Version | Status | Notes |
|---|---|---|
| `v1.txt` | PROPOSED (D-028) | Built on rung 3 `v1.txt`. If the rung 3 prompt changes before approval, this one changes to match. |

## What goes in the writings section (D-029, PROPOSED)

- **Which writing:** only opinions the justice *wrote* on the Supreme Court: opinions of the Court,
  concurrences, dissents, and written statements (for example, on a denial of cert). Not opinions they
  only joined, and nothing from before they joined the Court. Source: CourtListener, a free public
  database of court opinions.
- **Cutoff:** only opinions issued before the prediction is made.
- **Nothing about this case (D-009):** we leave out any writing in the same case or an earlier stage
  of the same dispute, such as an emergency-docket order. Example: *DHS v. D.V.D.* (26-426) produced
  written opinions on an emergency application in 2025, and those are excluded. A script flags
  matches by docket number and party names; we check the flagged ones by hand.
- **How they're chosen (by topic):** a script compares this case's question presented and
  lower-court summary with every eligible opinion by that justice. It uses word-overlap similarity
  (TF-IDF, already part of scikit-learn, so nothing new to install) and takes the closest opinions
  first.
- **How long:** 30k tokens per justice. Each opinion is capped at 6k tokens, kept from its
  beginning, so about 5 or more opinions fit. Together with the 60k case bundle, each prompt is at
  most about 90k tokens. The case bundle comes before the justice's name, so it is identical in all
  9 prompts and can be reused cheaply; only the writings differ.
- **Recorded with each prediction:** which opinions went in, their similarity scores, and how much
  of each was cut, so anyone can see exactly what the model saw.

## Steelman case against v1

- **The model has probably read all of these opinions already.** Every opinion before mid-2026 is
  likely in its training data. Rung 4 may only *remind* it of what it knows, so a small gap between
  rungs 3 and 4 wouldn't mean the writings are useless. That is a finding in itself, but it limits
  what rung 4 can show. A fine-tuned open model (rung 5) is the cleaner test.
- **Choosing separate opinions skews toward disagreement.** Concurrences and dissents are written
  when a justice disagrees, so they can make a justice look more extreme than their votes do. The
  note on majority opinions in the prompt tells the model this but does not fix it. An alternative
  is a fixed mix, such as at least two opinions of the Court in every selection.
- **Word overlap is a crude measure of topic.** Two cases can share words ("Title IX", "preemption")
  but turn on different questions, and the closest match for a brand-new issue may be poor. We
  chose it because it is simple, neutral, and the same for everyone. Better matching methods would
  need new tools or extra model calls.
- **Uneven material.** Justice Jackson has written far fewer opinions than Justice Thomas, so her
  selections draw on a smaller, more recent pool. The prompt doesn't say so; the results by justice
  should.
- **Older opinions may be out of date.** Views change over 20-30 years. Topic matching ignores dates.
  We could break ties in favor of recent opinions, at the cost of another tuning choice.
- **Cutting from the start keeps facts and procedure, and often loses the reasoning.** Opinions
  usually open with background, and the justice's real argument comes later. Keeping the opening
  and a later stretch, or the opinion's own summary, would be better but harder to do the same way
  every time.
- **Longer prompts can bury the case.** At about 90k tokens, the model may give the writings more
  weight than the briefs, or lose details in the middle of the prompt.
