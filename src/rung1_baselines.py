"""Rung 1: baselines that use no case content at all.

  B0  Always petitioner: every justice votes for the petitioner ("always reverse").
  B1  Ideology only: each justice votes their overall lean (conservative or liberal),
      read off the direction of the lower-court ruling being reviewed.
  B2  Ideology by issue: same as B1, but the lean is measured separately per issue area.

Every prediction for term T uses only votes from terms before T, so nothing leaks.
Run:  .venv/bin/python src/rung1_baselines.py
Writes: results/rung1_baselines.md
"""

import pandas as pd

from scdb import ROOT, load_votes

EVAL_TERMS = range(2018, 2026)  # OT2018-OT2025: development terms, not the headline test
CURRENT_COURT = ["JGRoberts", "CThomas", "SAAlito", "SSotomayor", "EKagan",
                 "NMGorsuch", "BMKavanaugh", "ACBarrett", "KBJackson"]
MIN_ISSUE_VOTES = 10  # below this, B2 falls back to the justice's overall lean

# Used only for a justice's first term, when they have no past votes to measure.
# 1 = appointed by a Republican president, 0 = by a Democrat.
APPOINTED_BY_REPUBLICAN = {
    "JGRoberts": 1, "CThomas": 1, "SAAlito": 1, "NMGorsuch": 1, "BMKavanaugh": 1,
    "ACBarrett": 1, "SSotomayor": 0, "EKagan": 0, "KBJackson": 0,
    "RBGinsburg": 0, "SGBreyer": 0, "AMKennedy": 1,
}


def vote_from_lean(lean_conserv: pd.Series, lc_conserv: pd.Series) -> pd.Series:
    """Turn a lean into a vote for or against the petitioner.

    A conservative justice wants to reverse a liberal lower court (vote petitioner)
    and affirm a conservative one (vote respondent); a liberal justice the opposite.
    If the lower court's direction is unknown, fall back to voting petitioner.
    """
    votes_petitioner = (lean_conserv == 1) != (lc_conserv == 1)
    return votes_petitioner.where(lc_conserv.notna(), True).astype(int)


def predict_term(votes: pd.DataFrame, term: int) -> pd.DataFrame:
    past = votes[(votes.term < term) & votes.voted_conserv.notna()]
    now = votes[votes.term == term].copy()

    overall = past.groupby("justiceName").voted_conserv.mean()
    by_issue = past.groupby(["justiceName", "issueArea"]).voted_conserv.agg(["mean", "size"])

    prior = now.justiceName.map(APPOINTED_BY_REPUBLICAN).astype(float)
    lean_rate = now.justiceName.map(overall).fillna(prior)
    now["lean_b1"] = (lean_rate > 0.5).astype(int)

    key = pd.MultiIndex.from_arrays([now.justiceName, now.issueArea])
    issue_stats = by_issue.reindex(key)
    issue_rate = pd.Series(issue_stats["mean"].values, index=now.index)
    enough = pd.Series(issue_stats["size"].values, index=now.index) >= MIN_ISSUE_VOTES
    now["lean_b2"] = (issue_rate.where(enough, lean_rate) > 0.5).astype(int)

    now["pred_b0"] = 1
    now["pred_b1"] = vote_from_lean(now.lean_b1, now.lc_conserv)
    now["pred_b2"] = vote_from_lean(now.lean_b2, now.lc_conserv)
    return now


def case_predictions(preds: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    """A case goes to the petitioner if a strict majority of predicted votes do (a tie affirms)."""
    g = preds.groupby("caseId")
    cases = g.agg(term=("term", "first"), petitioner_won=("petitioner_won", "first"),
                  unanimous=("minVotes", lambda s: s.iloc[0] == 0))
    for m in models:
        share = g[f"pred_{m}"].mean()
        cases[f"pred_{m}"] = (share > 0.5).astype(int)
    return cases


def pct(x: pd.Series) -> str:
    return f"{100 * x.mean():.1f}%"


def main() -> None:
    votes = load_votes()
    preds = pd.concat([predict_term(votes, t) for t in EVAL_TERMS])
    models = ["b0", "b1", "b2"]
    names = {"b0": "B0 always petitioner", "b1": "B1 ideology only", "b2": "B2 ideology by issue"}
    cases = case_predictions(preds, models)
    split = cases[~cases.unanimous]
    split_votes = preds[preds.caseId.isin(split.index)]

    out = ["# Rung 1 baselines",
           "",
           f"Development terms OT{EVAL_TERMS[0]}-OT{EVAL_TERMS[-1]}: {len(cases)} argued cases, "
           f"{len(preds)} justice votes. Each term is predicted only from earlier terms.",
           "",
           "## Headline accuracy",
           "",
           "| Model | Case outcome | Case (split decisions only) | Justice votes | Votes (split decisions only) |",
           "|---|---|---|---|---|"]
    for m in models:
        out.append(f"| {names[m]} | {pct(cases[f'pred_{m}'] == cases.petitioner_won)} "
                   f"| {pct(split[f'pred_{m}'] == split.petitioner_won)} "
                   f"| {pct(preds[f'pred_{m}'] == preds.voted_petitioner)} "
                   f"| {pct(split_votes[f'pred_{m}'] == split_votes.voted_petitioner)} |")
    out += ["", f"Split decisions: {len(split)} of {len(cases)} cases were not unanimous.", ""]

    out += ["## Vote accuracy by justice (current Court)", "",
            "| Justice | Votes | " + " | ".join(names[m] for m in models) + " |",
            "|---|---|" + "---|" * len(models)]
    for name in CURRENT_COURT:
        jv = preds[preds.justiceName == name]
        out.append(f"| {name} | {len(jv)} | "
                   + " | ".join(pct(jv[f"pred_{m}"] == jv.voted_petitioner) for m in models) + " |")

    out += ["", "## Case accuracy by term", "",
            "| Term | Cases | " + " | ".join(names[m] for m in models) + " |",
            "|---|---|" + "---|" * len(models)]
    for term, tc in cases.groupby("term"):
        out.append(f"| OT{term} | {len(tc)} | "
                   + " | ".join(pct(tc[f"pred_{m}"] == tc.petitioner_won) for m in models) + " |")

    path = ROOT / "results/rung1_baselines.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
