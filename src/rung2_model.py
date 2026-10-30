"""Rung 2: a statistical model trained on coded case facts, no case text.

For each justice-vote it predicts "votes for the petitioner?" from:
  - case facts the database codes and that are known before decision (issue, parties,
    which lower court, how it ruled, whether there was a dissent below, why cert was granted)
  - the justice's track record before this term (their lean, how often they side with petitioners)
  - the Court's recent reversal rate
The case outcome is the majority of the predicted votes, as in rung 1.

Model: gradient-boosted decision trees (many small decision trees, each one fixing the
mistakes of the ones before). For term T it is trained only on terms before T.

Two versions, per D-017:
  own  the justice's lean is their past conservative-vote share in the database
  mq   the lean is their Martin-Quinn score from the previous term
       (runs only if data/raw/mq/justices.csv exists)

Run:  .venv/bin/python src/rung2_model.py
Writes: results/rung2_model.md
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder

from rung1_baselines import CURRENT_COURT, EVAL_TERMS, case_predictions, pct, predict_term, vote_from_lean
from scdb import ROOT, load_votes

MQ_FILE = ROOT / "data/raw/mq/justices.csv"

CASE_CATEGORIES = ["issueArea", "issue", "petitioner", "respondent", "caseSource", "caseOrigin",
                   "lcDisposition", "certReason", "jurisdiction", "adminAction", "justiceName"]
CASE_NUMBERS = ["term", "lc_conserv", "lcDisagreement", "threeJudgeFdc", "court_pet_rate_5yr"]
JUSTICE_NUMBERS = ["lean", "lean_vote", "pet_rate", "terms_served"]
RECENT_TERMS = 5


def add_history(votes: pd.DataFrame) -> pd.DataFrame:
    """Add each justice's record from all terms strictly before the current one."""
    per_term = votes.groupby(["justiceName", "term"]).agg(
        cons=("voted_conserv", "sum"), coded=("voted_conserv", "count"),
        pet=("voted_petitioner", "sum"), n=("voted_petitioner", "size")).reset_index()
    per_term = per_term.sort_values(["justiceName", "term"])
    g = per_term.groupby("justiceName")
    # cumsum includes the current term, so subtract it back out to keep only the past.
    for col in ["cons", "coded", "pet", "n"]:
        per_term[f"past_{col}"] = g[col].cumsum() - per_term[col]
    per_term["lean"] = per_term.past_cons / per_term.past_coded.replace(0, np.nan)
    per_term["pet_rate"] = per_term.past_pet / per_term.past_n.replace(0, np.nan)
    per_term["terms_served"] = g.cumcount()
    votes = votes.merge(per_term[["justiceName", "term", "lean", "pet_rate", "terms_served"]],
                        on=["justiceName", "term"], how="left")

    # Share of cases the petitioner won over the previous five terms.
    case_rate = votes.groupby("term").agg(won=("petitioner_won", "sum"), n=("petitioner_won", "size"))
    rolled = case_rate.rolling(RECENT_TERMS, min_periods=1).sum().shift(1)
    votes["court_pet_rate_5yr"] = votes.term.map(rolled.won / rolled.n)
    return votes


def add_mq(votes: pd.DataFrame) -> pd.DataFrame:
    """Martin-Quinn score from the previous term (positive = conservative), rescaled to 0-1."""
    mq = pd.read_csv(MQ_FILE)[["term", "justiceName", "post_mn"]]
    mq["term"] += 1  # a score from term T-1 is what we know going into term T
    votes = votes.merge(mq.rename(columns={"post_mn": "mq"}), on=["justiceName", "term"], how="left")
    votes["lean_mq"] = 1 / (1 + np.exp(-votes.mq))
    return votes


def make_model() -> object:
    encode = ColumnTransformer(
        [("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan,
                                encoded_missing_value=np.nan, min_frequency=30), CASE_CATEGORIES)],
        remainder="passthrough")
    n_num = len(CASE_NUMBERS) + len(JUSTICE_NUMBERS)
    trees = HistGradientBoostingClassifier(
        categorical_features=[True] * len(CASE_CATEGORIES) + [False] * n_num,
        learning_rate=0.05, max_iter=300, random_state=0)
    return make_pipeline(encode, trees)


def predict_rolling(votes: pd.DataFrame, lean_col: str) -> pd.Series:
    """Predicted vote for every row in EVAL_TERMS, each term trained on earlier terms only."""
    X = votes[CASE_CATEGORIES + CASE_NUMBERS].copy()
    X["lean"] = votes[lean_col]
    X["lean_vote"] = vote_from_lean((votes[lean_col] > 0.5).astype(int), votes.lc_conserv)
    X["lean_vote"] = X.lean_vote.where(votes[lean_col].notna())
    X["pet_rate"], X["terms_served"] = votes.pet_rate, votes.terms_served
    y = votes.voted_petitioner

    out = pd.Series(np.nan, index=votes.index)
    for term in EVAL_TERMS:
        train, test = votes.term < term, votes.term == term
        model = make_model().fit(X[train], y[train])
        out[test] = model.predict(X[test])
    return out


def main() -> None:
    votes = add_history(load_votes())
    has_mq = MQ_FILE.exists()
    if has_mq:
        votes = add_mq(votes)

    preds = pd.concat([predict_term(votes, t) for t in EVAL_TERMS])
    preds["pred_r2"] = predict_rolling(votes, "lean").loc[preds.index].astype(int)
    models = ["b0", "b1", "r2"]
    names = {"b0": "B0 always petitioner", "b1": "B1 ideology only", "r2": "R2 model (own-vote lean)"}
    if has_mq:
        preds["pred_r2mq"] = predict_rolling(votes, "lean_mq").loc[preds.index].astype(int)
        models.append("r2mq")
        names["r2mq"] = "R2 model (Martin-Quinn lean)"

    cases = case_predictions(preds, models)
    split = cases[~cases.unanimous]
    split_votes = preds[preds.caseId.isin(split.index)]

    out = ["# Rung 2: statistical model on coded case facts", "",
           f"Development terms OT{EVAL_TERMS[0]}-OT{EVAL_TERMS[-1]}: {len(cases)} cases, {len(preds)} votes. "
           "Each term is predicted by a model trained only on earlier terms (back to 1946).", ""]
    if not has_mq:
        out += ["Martin-Quinn comparison not run: `data/raw/mq/justices.csv` was not found.", ""]
    else:
        out += ["Caveat: Martin-Quinn scores are estimated from the full vote history, so even the "
                "previous-term score has seen some later votes. That gives the MQ version a small head start.", ""]

    out += ["## Headline accuracy", "",
            "| Model | Case outcome | Case (split only) | Justice votes | Votes (split only) |",
            "|---|---|---|---|---|"]
    for m in models:
        out.append(f"| {names[m]} | {pct(cases[f'pred_{m}'] == cases.petitioner_won)} "
                   f"| {pct(split[f'pred_{m}'] == split.petitioner_won)} "
                   f"| {pct(preds[f'pred_{m}'] == preds.voted_petitioner)} "
                   f"| {pct(split_votes[f'pred_{m}'] == split_votes.voted_petitioner)} |")

    out += ["", "## Vote accuracy by justice (current Court)", "",
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

    path = ROOT / "results/rung2_model.md"
    path.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
