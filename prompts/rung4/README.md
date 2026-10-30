# Rung 4 prompts

Rung 4 asks whether the AI predicts a justice from their reputation (the name) or from their
jurisprudence (their own past writing), and which of the two produces the real Court's coalitions.
The full design, hypotheses and scoring are in `docs/rung4_rung5_plan.md`.

| File | Status | Used for |
|---|---|---|
| `v1.txt` | SUPERSEDED (by D-035) | Never used. |
| `v2_named.txt` | PROPOSED (D-035) | 4N (name + writings) and 4S (name + another justice's writings) |
| `v2_blind.txt` | PROPOSED (D-035) | 4B (writings, name hidden: "Justice A") |
| `author_probe_v1.txt` | PROPOSED (D-035) | Author probe on 6 cases: can the model tell who wrote the cleaned writings? |

## How the prompts line up

- **Rung 3 v2 to 4N:** 4N is rung 3 v2 with the writings section added, the first paragraph
  mentioning the writings, "on the past writings below" added to the "Base your prediction"
  sentence, and the `writings_relied_on` field. Any gap between rungs 3 and 4N should come from the
  writings.
- **4N to 4B:** the two differ only in the block between `</materials>` and `<justice_writings>`
  (who the justice is, and "do not try to work out who Justice A is") and in the question line. The
  writings are the same text in both.
- **Shared opening:** everything up to `</materials>` is word for word the same in 4N, 4B and 4S, so
  all 22 rung 4 prompts for a case start identically and that start can be reused from a cache.
- **4S swap:** `v2_named.txt` filled with one justice's name and another's writings. Pairs: Thomas
  and Sotomayor, Gorsuch and Alito, both directions.

## Filling in `{writings_list}` and `{writings}` (D-036)

- Labels: `Opinion 1 (2019, dissent)`, `Opinion 2 (2022, opinion of the Court)`, ... numbered in
  the order shown (most similar first, after the fixed mix is met).
- Each excerpt in `{writings}` starts with `=== Opinion 1 (2019, dissent) ===`, as the case materials
  do.
- Before use, the text is cleaned: case names in labels and headings removed, the author line
  ("JUSTICE X, concurring") removed, every justice's name replaced with "[a justice]".
- Recorded with each prediction: which opinions went in (with their real case names, kept outside
  the prompt), similarity scores, and how much of each was cut.

## Steelman case against v2

- **"Do not try to work out who Justice A is" may not work.** A model can't choose to forget what it
  recognizes. The author probe measures how often it can tell; the instruction only keeps it from
  making identification the task.
- **Removing case names takes away real information from 4N.** A named justice's opinion in a
  well-known case carries meaning the bare text doesn't. We accept that so 4N and 4B differ only by
  the name. 4N may therefore score a little below what a "best possible" rung 4 would.
- **Replacing all justices' names can garble the text.** "[a justice]'s dissent misreads the
  statute" loses who is arguing with whom. Some excerpts will read oddly.
- **The note on separate opinions may overcorrect.** Telling the model that disagreement is rarer
  than it looks could push it toward predicting unanimity, which is one of the things the coalition
  test measures. It is the same in every rung 4 condition, so comparisons between them are fair,
  but rung 3 doesn't have it.
- **The swap tells the model something false** (that these are the named justice's writings). That
  is the test, but it's an artificial setup a reviewer may question.
- **The concerns about v1 still hold:** the model has probably read these opinions already, topic
  matching by word overlap is crude, Justice Jackson's pool is smaller, older opinions may be out of
  date, cutting from the start of an opinion keeps background and can lose the reasoning, and long
  prompts can bury the case.
