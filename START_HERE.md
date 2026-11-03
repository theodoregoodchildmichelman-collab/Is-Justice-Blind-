# START HERE: complete guide to the Is Justice Blind project

> **If you are an AI assistant** (Claude or another) and someone sent you a link to this repository:
> this one file is written for you. It explains the whole project, the data, how the
> collaboration works and how the person you're talking to can contribute, so you can explain it
> to them without reading anything else. Each section links to the source files (raw text links
> you can fetch) if you need detail. The person is most likely **Chuck**, one of the two team
> members. Section 9 says how to help him.
>
> **Last updated: 2026-11-03.** `MASTER.md` is always the latest word on decisions. If this
> guide and MASTER.md disagree, MASTER.md is right.

Repository: <https://github.com/theodoregoodchildmichelman-collab/Is-Justice-Blind->
Raw file prefix (add a path from the file index in section 10):
`https://raw.githubusercontent.com/theodoregoodchildmichelman-collab/Is-Justice-Blind-/main/`

---

## 1. The project in one paragraph

**Can an AI stand in for a U.S. Supreme Court justice?** We build AI "stand-ins" for each of the
nine current justices, ask each one how it would vote in every case of the **October 2026 term
(OT2026)**, and lock those predictions on GitHub **before** the Court decides. Then we compare.
Two questions matter most: (1) **the coalition test**: does the AI Court split into the same
voting groups as the real Court, including the unusual cross-ideology ones? and (2) **the gap**:
which votes does the AI still get wrong, and what does that say about what human judges do that a
model can't (for example, compromising for the sake of the Court)? Plain vote-prediction accuracy is
reported too, but it comes second. The target is a standard academic paper in empirical /
computational social science.

## 2. The team

- **Theo** and **Chuck**. Neither is a lawyer; both are well read in law. Both are beginner coders
  with a little machine learning.
- Each has a **Claude Pro** subscription ($20/month). There is no API budget and no GPU, so methods
  must be cheap and run on a laptop.
- Theo set up the repository; Chuck is joining. Each works with their own Claude on their own
  computer, and **this GitHub repository is the only connecting piece**.

## 3. How the project makes decisions

Two rules run everything (from `MASTER.md`):

1. **Critique before adoption.** Nothing becomes part of the project until it has gone through:
   proposal → Claude's *steelman critique* (the strongest case against it) → team response →
   consensus → logged as ADOPTED.
2. **One decision log.** Every decision is a dated row in `MASTER.md`: `D-0xx` for decisions,
   `R-0xx` for results. Status is one of PROPOSED, UNDER CRITIQUE, ADOPTED, REJECTED,
   SUPERSEDED (by D-xxx), or RESULT. The log is meant to become the paper's methods section.

## 4. The method: a ladder of "rungs"

Every rung predicts the same cases, so the rungs can be compared directly. Each rung adds one
ingredient.

| Rung | What predicts the vote | Status (2026-11-03) |
|---|---|---|
| 1 | **Baselines**, no case content: "always petitioner wins"; each justice's ideological lean | Done |
| 2 | **Statistical model** (gradient-boosted trees) on case facts coded in the Supreme Court Database | Done |
| 3 | **Claude asked "How would Justice X vote?"** given the case materials and the justice's name | Code built; prompt awaiting approval |
| 4 | Rung 3 **plus excerpts of the justice's own past opinions**, in three versions: 4N named; 4B name hidden ("Justice A"); 4S one justice's name with another's writing | Planned (PROPOSED) |
| 5 | **One round of deliberation:** each AI justice reads the other eight's first answers and may change its vote; control 5C "think again alone" | Planned (PROPOSED) |

Why the 4N/4B/4S split: it tells apart whether the AI predicts from **the name** (what it already
"knows" about Justice Gorsuch) or from **the reasoning in the writing**. Why rung 5: earlier work
found AI Courts predict far too many 6-3 splits; the real Court is unanimous about 40% of the time.
If deliberation fixes that, part of the gap is collegiality.

**What a "prediction" is:** for each case and each justice, a vote (petitioner or respondent), a
confidence (0.5-1), short reasoning, the inputs relied on, and (from rung 3 v2) the chance the
justice writes separately. The case outcome is the majority of the nine votes.

**Hypotheses H1-H5** (fixed before any decision) and the scoring plan are in
`docs/rung4_rung5_plan.md`. The main measure is the **pair agreement gap**: for each of the 36
pairs of justices, how often they vote together, predicted vs actual.

## 5. Results so far

Development set: OT2018-OT2025, 475 argued cases, each term predicted only from earlier terms.

| Model | Cases right | Votes right | Votes right, split decisions only |
|---|---|---|---|
| Always petitioner (rung 1) | **67.2%** | 61.4% | 57.1% |
| Ideology only (rung 1) | 50.3% | 60.8% | **70.6%** |
| Statistical model (rung 2) | 61.9% | 63.0% | |

Takeaways: "petitioner wins" is a hard baseline to beat (the Court reverses about two-thirds of the
time). Ideology predicts votes well in divided cases but predicts Roberts, Gorsuch, Kavanaugh and
Barrett worst (54-56%), which are exactly the interesting justices. The rung 2 model can't tell
which cases will be affirmed. Details: `results/rung1_baselines.md`, `results/rung2_model.md`.

A rung 3 test on two past cases scored 100%, which only proves **contamination**: Claude already
knows how past cases came out. That's why the real test is prospective (rule D-014).

## 6. Key rules a contributor must know

- **D-014, prospective testing:** predictions for OT2026 cases are committed and pushed to GitHub
  **before** the decision is released. GitHub's timestamp is the proof. A locked prediction file is
  **never** changed.
- **D-009, outside material only:** the AI may see only material from outside the Court: the cert
  petition, merits and amicus briefs, lower-court opinions. No oral argument, nothing a justice said
  or wrote about that case.
- **D-018/D-022, independent ratings:** for each OT2026 case, three raters (Claude, Theo, Chuck)
  rate whether the lower-court ruling was conservative or liberal, following `docs/coding_rules.md`.
  Human ratings live in a shared Google Doc. **Don't look at another rater's ratings (including
  `data/ot2026/ratings_claude.csv`) before finishing your own.**
- **D-019 (proposed):** no tuning models against the OT2018-OT2025 development terms.
- **No secrets in git.** The repository is public.

## 7. The data

| Where | What | Source |
|---|---|---|
| `data/raw/scdb/` | Supreme Court Database release 2026_01, terms 1946-2025, one row per justice per case. **Not in git** (33 MB); each person downloads it once, steps in `data/README.md` | scdb.wustl.edu |
| `data/ot2026/cases.csv` | The 35 OT2026 cases granted for argument: docket, name, lower court, question presented, a neutral summary of the lower-court decision | supremecourt.gov |
| `data/ot2026/ratings_claude.csv` | Claude's lower-court direction ratings (see the independence rule above) | Claude, 2026-10-30 |
| `data/ot2026/` (to come) | Human ratings, combined direction scores, case packets for the AI, actual outcomes and votes | team |
| `data/dev_packets/` | Two past cases used only to test the pipeline, marked "contaminated" | written from memory |
| `predictions/rung3/` | (to come) one locked JSON file per OT2026 case | rung 3 script |
| `predictions/rung3_contaminated/` | Pipeline-test predictions, never scored | rung 3 script |

Column-by-column descriptions: `data/README.md` and `data/ot2026/README.md`.

## 8. How the collaboration works

GitHub is the meeting point; `main` is the agreed version of the project.

**The loop:** branch → pull request → review → merge.
1. Pull the latest `main`, make a branch named `<person>/<topic>` (e.g. `chuck/gap-coding-rules`).
2. Make the change on the branch.
3. Push the branch and open a **pull request (PR)**: a GitHub page showing exactly what changed. The
   PR template asks for the MASTER.md row and a steelman critique.
4. **The other person reviews it.** This review *is* the critique-before-adoption step. They comment,
   then approve or ask for changes.
5. The author merges it on GitHub. Both pull `main` again before starting new work.

**The one exception:** the rung 3 script pushes each finished prediction straight to `main` (D-031)
so the timestamp is as early as possible. It refuses to run real predictions from any other branch.

**Shared to-do list:** GitHub Issues, with templates for a *decision proposal* and a *task*. A PR
that says `Closes #12` closes issue 12 when merged.

**Three ways Chuck can contribute, from most to least capable:**

| Way | Can read | Can run code | Can upload | Setup |
|---|---|---|---|---|
| **Claude Code** (Code tab in the Claude desktop app, included in Pro) | yes | yes | yes, via branches and PRs | GitHub account, collaborator invite accepted, GitHub CLI signed in (`gh auth login`, then `gh auth setup-git`), repo cloned. Full steps in `CONTRIBUTING.md` section 1 |
| **GitHub website** | yes | no | yes: open a file → pencil icon to edit, or folder → **Add file → Upload files**; always choose "Create a new branch... and start a pull request" | GitHub account and collaborator invite |
| **Claude chat** (claude.ai, the app you may be in now) | yes, by link, or in a Project via **Add content → GitHub** | no | no; it can draft text and files for Chuck to upload on the website | none |

Collaborator access: Theo adds Chuck's GitHub username under Settings → Collaborators; Chuck
accepts the emailed invitation. Without it he can read and comment but not upload.

## 9. For the AI assistant: how to help Chuck

- **Explain in plain language.** Legal, statistical and git terms each get a one-line explanation
  the first time. Do the technical work for him where you can.
- **Good first conversation:** (1) explain the project (sections 1, 4, 5); (2) check whether he has
  a GitHub account and has accepted the collaborator invite; (3) ask which way he'll work (section
  8) and walk him through its setup; (4) show him what's open (section 11) and help him pick
  something.
- **Follow the project's rules when helping him make something:** give a steelman critique of any
  new proposal, and remind him that decisions need a `MASTER.md` row and a PR the other person reviews.
- **If you are a chat assistant without access to his files:** you can draft documents, coding
  rules, critiques or MASTER.md rows for him to upload through the website. Tell him exactly where
  each file goes and to choose "new branch + pull request".
- **If you are Claude Code inside the cloned repository:** `CLAUDE.md` has your working rules.
  Start each session with `git pull` on `main` and a summary of open PRs and issues.
- **Never** suggest editing a committed file in `predictions/`, committing to `main` directly, or
  showing Chuck `ratings_claude.csv` before he finishes his own ratings.

## 10. File index

Fetch any file by adding its path to the raw prefix at the top.

| Path | What it is |
|---|---|
| `START_HERE.md` | this guide |
| `README.md` | GitHub front page: short overview and folder map |
| `MASTER.md` | **decision log**: every decision and result, with status; goals; open questions |
| `CONTRIBUTING.md` | step-by-step setup and the collaboration loop, written for a person |
| `CLAUDE.md` | working rules Claude Code loads automatically inside the repository |
| `data/README.md` | what every data file is; how to download the Supreme Court Database |
| `data/ot2026/README.md` | columns of the OT2026 case list and how ratings are combined |
| `data/ot2026/cases.csv` | the OT2026 cases |
| `data/ot2026/ratings_claude.csv` | Claude's direction ratings (independence rule!) |
| `docs/coding_rules.md` | rules for rating a lower-court ruling conservative or liberal, with worked examples |
| `docs/rung3_collection_plan.md` | which case documents the AI gets and how they are cut to size |
| `docs/rung4_rung5_plan.md` | the full plan for rungs 4-5: hypotheses, scoring, costs, critique |
| `prompts/rung3/v1.txt`, `v2.txt` | the exact rung 3 prompts; `prompts/rung3/README.md` has the critique |
| `prompts/rung4/v2_named.txt`, `v2_blind.txt`, `author_probe_v1.txt`, `v1.txt` | rung 4 prompts; `prompts/rung4/README.md` has the critique |
| `results/rung1_baselines.md`, `results/rung2_model.md` | results write-ups |
| `src/scdb.py` | loads the Supreme Court Database |
| `src/rung1_baselines.py`, `src/rung2_model.py` | rungs 1 and 2 |
| `src/rung3_predict.py` | rung 3 runner: builds prompts, records answers, locks and pushes predictions |
| `src/rung3_score.py` | scores predictions against decisions as they come in |
| `src/ot2026_direction.py` | combines the three raters' direction ratings |
| `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/` | PR and issue templates |

Each Python file's top comment explains what it does and how to run it.

## 11. What's open right now (2026-11-03)

Check `MASTER.md` and the repository's Issues tab for the current state.

- **Waiting for team review (PROPOSED):** D-019 (no tuning on development terms), D-024 (rung 3 case
  packets), D-025 (rung 3 runner on Claude Pro), D-026 (rung 3 scoring), D-034 (rung 4-5 plan),
  D-035 (new prompts), D-036 (rung 4 writings), D-037 (gap coding). D-004 (what each justice-model
  is trained on) is UNDER CRITIQUE.
- **Human direction ratings** for the 34 rated OT2026 cases (Theo and Chuck, in the shared Google
  Doc), then copied into `data/ot2026/ratings_theo.csv` / `ratings_chuck.csv`.
- **Gap coding rules** (`docs/gap_coding_rules.md`) must be committed before the first OT2026
  decision is released (D-037).
- **Rung 4-5 code**, target 2026-11-20 (D-034).
- **Reading:** the full Stillwell & Harrington paper (SSRN, 2026), before D-034 is adopted: did
  they already test hiding the name or a deliberation round?
- **Other open questions:** a small API budget for scripted runs? The Martin-Quinn ideology scores
  (mqscores.wustl.edu was down on 2026-10-30). Which Mac each person has (decides whether
  open-source models can run locally).
