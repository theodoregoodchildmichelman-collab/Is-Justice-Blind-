# Rung 1 baselines

Development terms OT2018-OT2025: 475 argued cases, 4243 justice votes. Each term is predicted only from earlier terms.

## Headline accuracy

| Model | Case outcome | Case (split decisions only) | Justice votes | Votes (split decisions only) |
|---|---|---|---|---|
| B0 always petitioner | 67.2% | 66.9% | 61.4% | 57.1% |
| B1 ideology only | 50.3% | 55.0% | 60.8% | 70.6% |
| B2 ideology by issue | 48.4% | 53.2% | 59.1% | 68.5% |

Split decisions: 278 of 475 cases were not unanimous.

## Vote accuracy by justice (current Court)

| Justice | Votes | B0 always petitioner | B1 ideology only | B2 ideology by issue |
|---|---|---|---|---|
| JGRoberts | 475 | 66.7% | 54.1% | 53.1% |
| CThomas | 475 | 58.5% | 61.9% | 61.9% |
| SAAlito | 471 | 60.1% | 63.7% | 62.6% |
| SSotomayor | 474 | 56.8% | 67.5% | 66.9% |
| EKagan | 474 | 58.0% | 65.6% | 65.6% |
| NMGorsuch | 472 | 64.0% | 54.0% | 48.5% |
| BMKavanaugh | 466 | 66.3% | 56.2% | 53.2% |
| ACBarrett | 339 | 64.3% | 55.2% | 54.3% |
| KBJackson | 231 | 58.9% | 70.6% | 68.4% |

## Case accuracy by term

| Term | Cases | B0 always petitioner | B1 ideology only | B2 ideology by issue |
|---|---|---|---|---|
| OT2018 | 68 | 57.4% | 48.5% | 44.1% |
| OT2019 | 56 | 60.7% | 50.0% | 41.1% |
| OT2020 | 56 | 75.0% | 57.1% | 58.9% |
| OT2021 | 62 | 75.8% | 54.8% | 51.6% |
| OT2022 | 57 | 61.4% | 47.4% | 49.1% |
| OT2023 | 59 | 72.9% | 52.5% | 54.2% |
| OT2024 | 60 | 70.0% | 46.7% | 43.3% |
| OT2025 | 57 | 64.9% | 45.6% | 45.6% |
