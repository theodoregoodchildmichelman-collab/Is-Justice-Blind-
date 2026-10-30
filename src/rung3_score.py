"""Score rung 3 on decided OT2026 cases, next to the baselines, as decisions come in.

Same metrics as results/rung2_model.md: case accuracy, vote accuracy, both also on split
(non-unanimous) decisions only, and vote accuracy per justice. Rung 3 also gets a calibration
score, and a coalition table for D-013 (how often each pair of justices votes together,
predicted vs actual).

Inputs:
  data/ot2026/outcomes.csv       one row per decided case: docket, decided (YYYY-MM-DD),
                                 petitioner_won (1 or 0), source (link to the opinion)
  data/ot2026/outcome_votes.csv  one row per justice per decided case: docket, justice
                                 (SCDB code, e.g. EKagan), vote (petitioner, respondent, or
                                 recused), opinions_joined (e.g. "majority; concurrence:Thomas"),
                                 wrote (the opinion they wrote, if any, e.g. "dissent")
  predictions/rung3/<docket>.json
  data/ot2026/direction_scores.csv for B1 (skipped until all three ratings are in)
  predictions/<model>/ot2026_votes.csv for any other model (columns docket, justice, vote),
                                 e.g. R2 once it has been run on OT2026

A rung 3 prediction counts only if it is committed to git, unchanged since, and its commit
date is before the decision date. Anything else is listed as excluded, with the reason.

Case outcome rule (as in rungs 1-2): the side most of the 9 predicted votes favor; a tie
goes to the respondent. Vote accuracy skips justices who did not take part.

Run:  .venv/bin/python src/rung3_score.py
      .venv/bin/python src/rung3_score.py --contaminated   # past-case pipeline tests, never accuracy
Writes: results/rung3_ot2026.md (the --contaminated run only prints)
"""

import argparse
import json
import subprocess
from itertools import combinations

import numpy as np
import pandas as pd

from rung1_baselines import CURRENT_COURT, pct, vote_from_lean
from scdb import ROOT, load_votes

DATA = ROOT / "data/ot2026"
RUNG3 = ROOT / "predictions/rung3"
RUNG3_DEV = ROOT / "predictions/rung3_contaminated"
NAMES = {"b0": "B0 always petitioner", "b1": "B1 ideology only", "rung3": "Rung 3 general AI"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def commit_date(path) -> str | None:
    """Date the file was first committed, or None if it is not committed or has been changed."""
    rel = str(path.relative_to(ROOT))
    first = git("log", "--diff-filter=A", "--format=%cI", "--", rel).splitlines()
    if not first or git("status", "--porcelain", "--", rel) or len(git("log", "--format=%H", "--", rel).splitlines()) > 1:
        return None
    return first[-1][:10]


def load_rung3(outcomes: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Rung 3 votes for decided cases, plus a list of excluded cases and why."""
    rows, excluded = [], []
    for docket, decided in outcomes.decided.items():
        path = RUNG3 / f"{docket}.json"
        if not path.exists():
            excluded.append(f"{docket}: no rung 3 prediction")
            continue
        committed = commit_date(path)
        if committed is None:
            excluded.append(f"{docket}: prediction not committed, or changed after commit")
            continue
        if committed >= decided:
            excluded.append(f"{docket}: committed {committed}, not before decision on {decided}")
            continue
        rec = json.loads(path.read_text())
        for justice, a in rec["justices"].items():
            rows.append({"docket": docket, "justice": justice, "vote": int(a["vote"] == "petitioner"),
                         "confidence": a["confidence"]})
    return pd.DataFrame(rows, columns=["docket", "justice", "vote", "confidence"]), excluded


def b1_votes(dockets: list[str]) -> pd.DataFrame | None:
    """Ideology only: each justice's lean from all past votes, read off our lower-court rating."""
    path = DATA / "direction_scores.csv"
    if not path.exists():
        return None
    scores = pd.read_csv(path, dtype={"docket": str}).set_index("docket").direction_score
    past = load_votes()
    lean = (past.groupby("justiceName").voted_conserv.mean() > 0.5).astype(int)
    rows = []
    for docket in dockets:
        lc = scores.get(docket, np.nan)
        lc = (lc > 0.5) * 1.0 if pd.notna(lc) else np.nan  # an exact 0.5 tie counts as liberal
        for j in CURRENT_COURT:
            v = vote_from_lean(pd.Series([lean[j]]), pd.Series([lc])).iloc[0]
            rows.append({"docket": docket, "justice": j, "vote": int(v)})
    return pd.DataFrame(rows)


def other_models() -> dict[str, pd.DataFrame]:
    out = {}
    for path in sorted((ROOT / "predictions").glob("*/ot2026_votes.csv")):
        df = pd.read_csv(path, dtype={"docket": str})
        df["vote"] = (df.vote == "petitioner").astype(int)
        out[path.parent.name] = df
    return out


def case_calls(preds: pd.DataFrame) -> pd.Series:
    """Predicted winner per case from all predicted votes: 1 = petitioner. A tie affirms."""
    return (preds.groupby("docket").vote.mean() > 0.5).astype(int)


def pairwise_agreement(votes: pd.DataFrame) -> pd.Series:
    """Share of cases where each pair of justices voted the same way."""
    wide = votes.pivot(index="docket", columns="justice", values="vote")
    out = {}
    for a, b in combinations(CURRENT_COURT, 2):
        both = wide[[a, b]].dropna()
        out[f"{a}-{b}"] = (both[a] == both[b]).mean() if len(both) else np.nan
    return pd.Series(out)


def score(models: dict[str, pd.DataFrame], actual_votes: pd.DataFrame, winners: pd.Series,
          title: str, notes: list[str]) -> list[str]:
    actual_votes = actual_votes[actual_votes.vote.isin(["petitioner", "respondent"])].copy()
    actual_votes["actual"] = (actual_votes.vote == "petitioner").astype(int)
    unanimous = actual_votes.groupby("docket").actual.agg(lambda s: s.nunique() == 1)

    # Compare every model on the same cases: those every model predicted.
    common = set(winners.index)
    for preds in models.values():
        common &= set(preds.docket)
    common = sorted(common)
    split = [d for d in common if not unanimous[d]]

    out = [f"# {title}", "", *notes, "",
           f"Cases scored: {len(common)} ({len(split)} split decisions).", ""]
    if not common:
        return out + ["Nothing to score yet."]

    out += ["## Headline accuracy", "",
            "| Model | Case outcome | Case (split only) | Justice votes | Votes (split only) |",
            "|---|---|---|---|---|"]
    joined = {}
    for m, preds in models.items():
        calls = case_calls(preds)
        v = preds.merge(actual_votes[["docket", "justice", "actual"]], on=["docket", "justice"])
        v = v[v.docket.isin(common)]
        joined[m] = v
        out.append(f"| {NAMES.get(m, m)} | {pct(calls[common] == winners[common])} "
                   f"| {pct(calls[split] == winners[split]) if split else '-'} "
                   f"| {pct(v.vote == v.actual)} "
                   f"| {pct(v[v.docket.isin(split)].vote == v[v.docket.isin(split)].actual) if split else '-'} |")

    out += ["", "## Vote accuracy by justice", "",
            "| Justice | Votes | " + " | ".join(NAMES.get(m, m) for m in models) + " |",
            "|---|---|" + "---|" * len(models)]
    for j in CURRENT_COURT:
        cells = [pct(v[v.justice == j].vote == v[v.justice == j].actual) for v in joined.values()]
        n = len(next(iter(joined.values())).query("justice == @j"))
        out.append(f"| {j} | {n} | " + " | ".join(cells) + " |")

    if "rung3" in joined:
        v = joined["rung3"]
        p_pet = np.where(v.vote == 1, v.confidence, 1 - v.confidence)
        brier = np.mean((p_pet - v.actual) ** 2)
        out += ["", "## Rung 3 calibration", "",
                f"Brier score {brier:.3f} (0 is perfect; always saying 50/50 scores 0.250).", "",
                "| Stated confidence | Votes | Share correct |", "|---|---|---|"]
        bins = pd.cut(v.confidence, [0.5, 0.6, 0.7, 0.8, 0.9, 1.0], include_lowest=True)
        for b, g in v.groupby(bins, observed=True):
            out.append(f"| {b} | {len(g)} | {pct(g.vote == g.actual)} |")

        # D-013: do the predicted coalitions look like the real ones?
        actual_pairs = pairwise_agreement(actual_votes[actual_votes.docket.isin(common)]
                                          .assign(vote=lambda d: d.actual))
        pred_pairs = pairwise_agreement(models["rung3"][models["rung3"].docket.isin(common)])
        gap = (pred_pairs - actual_pairs).abs()
        out += ["", "## Coalitions (D-013)", "",
                f"How often each pair of justices votes together. Average gap between predicted and "
                f"actual: {100 * gap.mean():.1f} points. Largest gaps:", "",
                "| Pair | Predicted together | Actually together |", "|---|---|---|"]
        for pair in gap.sort_values(ascending=False).index[:10]:
            out.append(f"| {pair} | {100 * pred_pairs[pair]:.0f}% | {100 * actual_pairs[pair]:.0f}% |")
    return out


def main_ot2026() -> None:
    outcomes = pd.read_csv(DATA / "outcomes.csv", dtype={"docket": str}).set_index("docket")
    actual = pd.read_csv(DATA / "outcome_votes.csv", dtype=str)
    rung3, excluded = load_rung3(outcomes)
    dockets = list(outcomes.index)

    models = {"b0": pd.DataFrame([{"docket": d, "justice": j, "vote": 1}
                                  for d in dockets for j in CURRENT_COURT])}
    notes = []
    b1 = b1_votes(dockets)
    if b1 is None:
        notes.append("B1 not scored: `data/ot2026/direction_scores.csv` does not exist yet.")
    else:
        models["b1"] = b1
    models.update(other_models())
    if "r2" not in models:
        notes.append("R2 not scored: no `predictions/r2/ot2026_votes.csv` yet.")
    models["rung3"] = rung3
    if excluded:
        notes += ["", "Excluded from rung 3:", *[f"- {e}" for e in excluded]]

    out = score(models, actual, outcomes.petitioner_won.astype(int), "Rung 3 on the October 2026 term", notes)
    out += ["", "## Opinions joined (for D-013)", "", "| Docket | Justice | Vote | Opinions joined | Wrote |",
            "|---|---|---|---|---|"]
    for r in actual.fillna("").itertuples():
        out.append(f"| {r.docket} | {r.justice} | {r.vote} | {r.opinions_joined} | {r.wrote} |")
    path = ROOT / "results/rung3_ot2026.md"
    path.write_text("\n".join(out) + "\n")
    print("\n".join(out))


def main_contaminated() -> None:
    """Score past-case pipeline tests against SCDB. Prints only; these are never accuracy numbers."""
    votes = load_votes()
    rows, actual, winners = [], [], {}
    for path in sorted(RUNG3_DEV.glob("*.json")):
        rec = json.loads(path.read_text())
        manifest = json.loads((ROOT / "data/dev_packets" / rec["docket"] / "manifest.json").read_text())
        cv = votes[votes.caseId == manifest["scdb_case_id"]]
        winners[rec["docket"]] = int(cv.petitioner_won.iloc[0])
        for r in cv.itertuples():
            actual.append({"docket": rec["docket"], "justice": r.justiceName,
                           "vote": "petitioner" if r.voted_petitioner else "respondent"})
        for j, a in rec["justices"].items():
            rows.append({"docket": rec["docket"], "justice": j, "vote": int(a["vote"] == "petitioner"),
                         "confidence": a["confidence"]})
    models = {"rung3": pd.DataFrame(rows)}
    out = score(models, pd.DataFrame(actual), pd.Series(winners),
                "CONTAMINATED pipeline test (not accuracy)",
                ["Past cases Claude has probably seen decided. This checks that the code runs; "
                 "the numbers mean nothing about how well rung 3 predicts."])
    print("\n".join(out))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--contaminated", action="store_true")
    if p.parse_args().contaminated:
        main_contaminated()
    else:
        main_ot2026()
