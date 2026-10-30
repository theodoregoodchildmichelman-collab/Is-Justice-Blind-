# Rung 2: statistical model on coded case facts

Development terms OT2018-OT2025: 475 cases, 4243 votes. Each term is predicted by a model trained only on earlier terms (back to 1946).

Martin-Quinn comparison not run: `data/raw/mq/justices.csv` was not found.

## Headline accuracy

| Model | Case outcome | Case (split only) | Justice votes | Votes (split only) |
|---|---|---|---|---|
| B0 always petitioner | 67.2% | 66.9% | 61.4% | 57.1% |
| B1 ideology only | 50.3% | 55.0% | 60.8% | 70.6% |
| R2 model (own-vote lean) | 61.9% | 61.9% | 63.0% | 65.1% |

## Vote accuracy by justice (current Court)

| Justice | Votes | B0 always petitioner | B1 ideology only | R2 model (own-vote lean) |
|---|---|---|---|---|
| JGRoberts | 475 | 66.7% | 54.1% | 63.2% |
| CThomas | 475 | 58.5% | 61.9% | 63.2% |
| SAAlito | 471 | 60.1% | 63.7% | 62.8% |
| SSotomayor | 474 | 56.8% | 67.5% | 66.2% |
| EKagan | 474 | 58.0% | 65.6% | 63.3% |
| NMGorsuch | 472 | 64.0% | 54.0% | 58.9% |
| BMKavanaugh | 466 | 66.3% | 56.2% | 62.4% |
| ACBarrett | 339 | 64.3% | 55.2% | 59.9% |
| KBJackson | 231 | 58.9% | 70.6% | 66.7% |

## Case accuracy by term

| Term | Cases | B0 always petitioner | B1 ideology only | R2 model (own-vote lean) |
|---|---|---|---|---|
| OT2018 | 68 | 57.4% | 48.5% | 54.4% |
| OT2019 | 56 | 60.7% | 50.0% | 51.8% |
| OT2020 | 56 | 75.0% | 57.1% | 76.8% |
| OT2021 | 62 | 75.8% | 54.8% | 71.0% |
| OT2022 | 57 | 61.4% | 47.4% | 50.9% |
| OT2023 | 59 | 72.9% | 52.5% | 54.2% |
| OT2024 | 60 | 70.0% | 46.7% | 71.7% |
| OT2025 | 57 | 64.9% | 45.6% | 64.9% |
