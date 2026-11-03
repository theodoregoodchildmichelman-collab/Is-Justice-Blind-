# Data

Everything the project reads or writes, folder by folder. Rule D-009 applies to all of it: material
used at prediction time comes only from outside the Court (cert petition, briefs, lower-court
opinions), never oral argument or anything a justice said about the case.

## raw/ (not in git)

The Supreme Court Database (SCDB), release **2026_01** (terms 1946-2025). It is 33 MB, so it is kept
out of git (see `.gitignore`); each person downloads it once.

1. Go to <http://scdb.wustl.edu/data.php>.
2. Under "Modern Database", download the **Case Centered Data, Citation** and the **Justice Centered
   Data, Citation** files in **CSV** format.
3. Unzip both into `data/raw/scdb/`, so you have:
   - `data/raw/scdb/SCDB_2026_01_caseCentered_Citation.csv`
   - `data/raw/scdb/SCDB_2026_01_justiceCentered_Citation.csv`

Codebook (what every column means): <http://scdb.wustl.edu/documentation.php>.
`src/scdb.py` loads the justice-centered file and adds clean 0/1 columns; its top comment lists them.

Martin-Quinn ideology scores, when we get them, go in `data/raw/mq/` (see open questions in MASTER.md).

## ot2026/

This term's cases, the prospective test set (D-014). Full column list in
[ot2026/README.md](ot2026/README.md).

| File | What it is |
|---|---|
| `cases.csv` | every docket granted for argument, with lower court, question presented and a neutral summary |
| `ratings_claude.csv` | Claude's rating of each lower-court ruling as Conservative / Liberal / Unclear (D-018). **Do not open until you have finished your own ratings.** |
| `ratings_theo.csv`, `ratings_chuck.csv` | (to come) human ratings, copied from the shared Google Doc |
| `direction_scores.csv` | (to come) the three ratings combined by `src/ot2026_direction.py` |
| `outcomes.csv`, `outcome_votes.csv` | (to come) each decision and each justice's vote, entered as decisions come out (D-026) |
| `packets/<docket>/` | (to come) the case materials fed to the AI for rungs 3-5 (docs/rung3_collection_plan.md) |

## dev_packets/

Two past cases (*Williams v. Reed*, *Medical Marijuana v. Horn*) used only to test that the rung 3
pipeline works. Written from memory and marked `"contaminated": true`: Claude already knows how they
came out, so they never count as accuracy.

## Elsewhere

- `predictions/rung3/<docket>.json`: one locked prediction per case (all nine justices' votes,
  confidence and reasoning). A committed file is never changed.
- `predictions/rung3_contaminated/`: pipeline tests on past cases, never scored.
- `results/`: write-ups produced by the scripts in `src/`.
