# Rung 3 prompts

One template per version. All 9 justices get the same template; only `{justice}` changes. Every
prediction file records the version and a fingerprint (`prompt_sha256`) of the exact template used.

| Version | Status | Notes |
|---|---|---|
| `v1.txt` | PROPOSED (D-023) | Not yet approved. Can still be edited; it freezes once approved. |

**Rule:** once a version has been used for any OT2026 prediction, it is never edited. Changes make
a new file (`v2.txt`), and the code refuses to finish a half-done case with a different template.

## v1: the design choices

1. **The justice's name comes after the materials.** The 9 prompts for a case then begin with
   identical text, which keeps them comparable and lets the cached start be reused cheaply.
2. **The reason comes before the vote.** The model writes its 2-4 sentences first, so it reasons
   before it commits, instead of justifying a vote it already picked.
3. **Vote = petitioner or respondent**, with "reverse or vacate, even in part" counted as petitioner.
   This matches how the Supreme Court Database codes a petitioner win (`partyWinning`), which rungs
   1-2 use.
4. **Confidence = probability the stated vote is right, 0.5 to 1.** Turned into "probability of a
   petitioner vote" for calibration scoring.
5. **"outcome_known" flag.** The model says if it thinks it already knows the result. A cheap alarm
   for leakage.
6. **No persona or role-play** ("You are Justice Kagan"). Asked as a forecasting question, which is
   what D-012 rung 3 describes.

## Steelman case against v1

- **Titles differ.** "Chief Justice John G. Roberts, Jr." vs "Justice Clarence Thomas": strictly,
  more than the name changes. Dropping titles would be purer but less natural; the Chief's role
  could also matter to how he votes (he often assigns opinions and seeks narrow rulings).
- **The model may just echo stereotypes.** "What you know in general about the justice" invites
  "Thomas = conservative." But that is what rung 3 is meant to measure; rung 4 adds the justice's
  own writing to see if that does better.
- **Asking each justice separately can give incoherent Courts** (say, 9-0 in a case that is plainly
  close), and a 5-4 split is hard to hit when each vote is judged alone. A single prompt asking for
  all nine votes at once would be more coherent and 9x cheaper, but it breaks the "one model per
  justice" design (D-007) and lets justices' predictions influence each other.
- **The framing may push toward "reverse."** Saying the petitioner "asked the Court to take the
  case" reminds the model that the Court usually reverses. That base rate is real public knowledge,
  so we keep it, but rung 3 may end up close to "always petitioner."
- **Self-reported "outcome_known" is weak.** A model cannot reliably tell what it has memorized.
  The real protection is the timing: every OT2026 decision comes after the model's training data.
- **Short JSON answers may lose quality.** Letting the model think at length before answering might
  predict better. We could allow free reasoning before the JSON, at a higher usage cost.
- **No case-type context.** The model is not told the issue area or the lower court's ideological
  direction; it must work these out. Adding them would mix in rung 2's information.
