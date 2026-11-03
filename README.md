# Is Justice Blind?

Can an AI stand in for a U.S. Supreme Court justice? This project builds models that predict how
each of the nine justices will vote, tests them **prospectively** on the October 2026 term
(predictions are locked on GitHub before each decision comes out), and studies **the gap**: what
the real justices do that the models cannot.

Two people, no lawyers, beginner coders, one Claude Pro subscription each. The aim is a standard
academic paper.

**New here? Read [CONTRIBUTING.md](CONTRIBUTING.md) first.** It explains how to get set up and how
the two of us pass work back and forth through this repository.

## Where things stand

The full history of every decision is in **[MASTER.md](MASTER.md)**, the project's single decision
log. Short version:

| Rung | What it is | Status |
|---|---|---|
| 1 | Baselines: "always petitioner", ideology only | Done: [results/rung1_baselines.md](results/rung1_baselines.md) |
| 2 | Statistical model on coded case facts | Done: [results/rung2_model.md](results/rung2_model.md) |
| 3 | Ask Claude "how would Justice X vote?" | Pipeline built; prompt awaiting approval |
| 4 | Same, plus the justice's own past writing (named / name hidden / name swapped) | Planned: [docs/rung4_rung5_plan.md](docs/rung4_rung5_plan.md) |
| 5 | One round of deliberation among the nine model-justices | Planned (same doc) |

The two headline analyses (D-032): the **coalition test** (do the nine models form the same voting
blocs as the real Court?) and **the gap**.

## Map of the repository

```
MASTER.md            decision log: every decision, dated, with its status (start here)
CONTRIBUTING.md      how to set up and how we work together
CLAUDE.md            instructions any Claude session reads automatically when it opens this folder
data/                all data; see data/README.md for what every file means
  raw/               downloaded Supreme Court Database (NOT in git, too big; download steps in data/README.md)
  ot2026/            this term's cases, direction ratings, and (later) outcomes
  dev_packets/       sample case packets used to test the rung 3 pipeline
docs/                plans and written rules (coding rules, collection plan, rung 4-5 plan)
prompts/             the exact prompts sent to the AI, one folder per rung, with critiques in each README
predictions/         locked predictions; NEVER edit a committed file here
results/             write-ups of each rung's results
src/                 Python code, one script per step (each file's top comment says how to run it)
requirements.txt     Python packages
```

## Quick start (for running code)

```bash
git clone https://github.com/theodoregoodchildmichelman-collab/Is-Justice-Blind-.git
cd Is-Justice-Blind-
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then download the Supreme Court Database as described in [data/README.md](data/README.md), and run,
for example, `.venv/bin/python src/rung1_baselines.py`.
