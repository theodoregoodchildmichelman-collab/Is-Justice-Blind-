"""Combine the three raters' OT2026 lower-court direction ratings (D-018).

Reads one file per rater, data/ot2026/ratings_<rater>.csv, with columns
docket, rater, rating, note (rating is Conservative, Liberal or Unclear).

For each case:
  direction_score  average of the ratings, Conservative = 1, Liberal = 0, Unclear skipped
                   (empty if every rater said Unclear)
  agreement        share of raters giving the most common rating (3/3, 2/3 or 1/3);
                   this is the case's weight
Overall agreement is Fleiss' kappa over the three categories (Unclear counts as a category):
1 = perfect agreement, 0 = no better than chance.

Run:  .venv/bin/python src/ot2026_direction.py
Writes: data/ot2026/direction_scores.csv
"""

import sys

import pandas as pd

from scdb import ROOT

DATA = ROOT / "data/ot2026"
RATERS = ["claude", "theo", "chuck"]
CATEGORIES = ["Conservative", "Liberal", "Unclear"]
SCORE = {"Conservative": 1.0, "Liberal": 0.0}


def load_ratings() -> pd.DataFrame:
    """One row per case, one column per rater."""
    cases = pd.read_csv(DATA / "cases.csv", dtype=str)
    dockets = cases.loc[cases.status == "rate", "docket"]
    table = pd.DataFrame(index=pd.Index(dockets, name="docket"))
    for rater in RATERS:
        path = DATA / f"ratings_{rater}.csv"
        if not path.exists():
            sys.exit(f"Missing {path.name}: all three raters must finish first.")
        r = pd.read_csv(path, dtype=str).set_index("docket").rating.str.strip().str.capitalize()
        bad = r[~r.isin(CATEGORIES)]
        missing = dockets[~dockets.isin(r.index)]
        if len(bad) or len(missing):
            sys.exit(f"{path.name}: invalid ratings {bad.to_dict()}, missing dockets {list(missing)}")
        table[rater] = r
    return table


def fleiss_kappa(counts: pd.DataFrame) -> float:
    """counts: one row per case, one column per category, each row summing to the number of raters."""
    n = counts.sum(axis=1).iloc[0]
    p_cat = counts.sum() / counts.values.sum()             # how often each category is used overall
    p_case = ((counts ** 2).sum(axis=1) - n) / (n * (n - 1))  # agreement within each case
    p_bar, p_chance = p_case.mean(), (p_cat ** 2).sum()
    return (p_bar - p_chance) / (1 - p_chance)


def main() -> None:
    table = load_ratings()
    counts = table.apply(lambda row: row.value_counts(), axis=1).reindex(columns=CATEGORIES).fillna(0)

    out = table.copy()
    out["direction_score"] = table.apply(lambda row: row.map(SCORE).mean(), axis=1).round(3)
    out["agreement"] = (counts.max(axis=1) / len(RATERS)).round(3)
    out.to_csv(DATA / "direction_scores.csv")

    kappa = fleiss_kappa(counts)
    print(f"Wrote {DATA / 'direction_scores.csv'} ({len(out)} cases)")
    print(f"Fleiss' kappa: {kappa:.3f}")
    print("Agreement:", out.agreement.map({1.0: "3/3", 0.667: "2/3", 0.333: "1/3"}).value_counts().to_dict())


if __name__ == "__main__":
    main()
