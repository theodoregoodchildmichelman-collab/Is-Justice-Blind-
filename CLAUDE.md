# Instructions for Claude

Read this before doing anything in this repository. Two team members (Theo and Chuck) each work
with their own Claude on their own computer; this GitHub repository is how the work moves between
them. You may be either person's Claude.

## The project

Is Justice Blind predicts U.S. Supreme Court votes, justice by justice, and tests the predictions
prospectively on the October 2026 term. Goals, rungs and every decision so far are in `MASTER.md`;
read it first. Data is explained in `data/README.md`; collaboration rules in `CONTRIBUTING.md`.

## Who you are working with

Neither team member is a lawyer (both are well read in law) and both are beginner coders. Explain
legal, statistical and git concepts in plain language, do the coding for them, and prefer cheap
methods that run on a laptop under a Claude Pro subscription (no API budget, no GPU).

## Rules

1. **Critique before adoption.** Before any new component (method, prompt, data source, rule) is
   adopted, give a steelman critique against it. The team responds; only the agreed version is
   adopted.
2. **Log every decision in `MASTER.md`** as a dated row (D-0xx for decisions, R-0xx for results)
   with status `PROPOSED` / `UNDER CRITIQUE` / `ADOPTED` / `REJECTED` / `SUPERSEDED (by D-xxx)`.
   Use the next free number on the latest `main`.
3. **Branches and pull requests.** At the start of a session, `git pull` on `main` and summarize what
   changed and which PRs and issues are open (`gh pr list`, `gh issue list`). Do work on a branch
   named `<person>/<topic>`, push it, and open a PR with `gh pr create` using the template. Never
   commit to `main` directly, except the automatic prediction locks below. Never merge a PR the
   other team member hasn't approved unless the user explicitly says to.
4. **Locked predictions are untouchable.** `src/rung3_predict.py` commits and pushes each finished
   prediction to `main` (D-014, D-031). Never edit, move, delete, rebase or force-push anything that
   would change a committed file in `predictions/`. Never `git push --force` to `main`.
5. **D-009:** material given to a model at prediction time comes only from outside the Court
   (cert petition, briefs, lower-court opinions). No oral argument, nothing a justice said or wrote
   about that case.
6. **Rater independence:** don't show a team member another rater's ratings before they have
   finished their own.
7. **No secrets in git.** The repository is public.
8. Keep the project directory clean: one script per step in `src/`, results in `results/`, plans and
   rules in `docs/`.
