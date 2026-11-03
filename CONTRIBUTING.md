# Working together on Is Justice Blind

This repository on GitHub is the meeting point. Each of us works on our own computer with our own
Claude, and everything we share goes through here. Nobody needs to know git well: Claude does the
typing, this page explains what is going on.

## 1. One-time setup

1. **GitHub account.** Sign up free at <https://github.com/signup> and send Theo your username.
   Theo adds you as a collaborator; accept the invitation from the email GitHub sends you (or at
   <https://github.com/notifications>). Until you accept, you can read everything but not upload.
2. **Claude Code.** In the Claude desktop app, open the **Code** tab (included with Claude Pro).
   This is the Claude that can open the project folder, run the code and send changes to GitHub.
3. **GitHub sign-in for your computer.** Install the GitHub command-line tool from
   <https://cli.github.com> (macOS installer), then in a terminal run:
   ```bash
   gh auth login
   ```
   Choose GitHub.com → HTTPS → "Login with a web browser". Then run `gh auth setup-git`. After
   this, Claude can push and open pull requests for you without asking for passwords.
4. **Get the project.** In the Code tab, ask Claude:
   > Clone https://github.com/theodoregoodchildmichelman-collab/Is-Justice-Blind-.git into my
   > Documents folder, set up the Python environment from requirements.txt, and walk me through
   > downloading the Supreme Court Database as described in data/README.md.

   Then open that folder as your project in the Code tab. Claude reads `CLAUDE.md` automatically
   and learns the project's rules.
5. **Read in this order:** `README.md` → `MASTER.md` (every decision so far) → `data/README.md`
   → `docs/rung4_rung5_plan.md`. Or ask Claude: "Give me a tour of this project."

**No Claude Code?** You can still take part from the GitHub website: open any file and press the
pencil icon to edit, or use **Add file → Upload files** on a folder page. When GitHub asks, choose
**"Create a new branch for this commit and start a pull request"**, never "Commit directly to main".
A normal claude.ai chat can also read the repository (in a Project, **Add content → GitHub**) to
answer questions about it, but it cannot upload.

## 2. The everyday loop: branch → pull request → review → merge

`main` is the agreed version of the project. Nobody edits it directly (one exception, below).
Instead:

1. **Start fresh.** Ask Claude: *"Pull the latest main and start a branch for <what you're doing>."*
   Branch names look like `chuck/gap-coding-rules` or `theo/rung4-code`.
2. **Work.** Ask Claude to make the change. Claude commits as it goes.
3. **Share.** Ask Claude: *"Push this branch and open a pull request."* A pull request (PR) is a
   page on GitHub that shows exactly what changed and lets the other person comment.
4. **Review = our critique step.** The other person reads the PR (on GitHub, or by asking their
   Claude *"review pull request #N and give me a steelman critique"*), leaves comments, and either
   approves or asks for changes. This is the "critique → team response → consensus" step from
   MASTER.md's process rule, written down where both of us can see it.
5. **Merge.** Once approved, the author presses **Merge pull request** on GitHub and deletes the
   branch. Then both of us ask Claude to *"pull the latest main"* before starting anything new.

Small fixes (typos, a broken link) still go through a PR, but the review can be a quick thumbs-up.

**The one exception: locked predictions.** `src/rung3_predict.py` commits each finished prediction
and pushes it straight to `main` the moment it is done (D-031), because GitHub's timestamp is our
proof that the prediction came before the decision. The script refuses to run real predictions
from any branch other than `main`. Never edit, move or delete a file in `predictions/` once it is
committed.

## 3. Rules that keep the project clean

- **Every decision goes in `MASTER.md`.** Add a row with the next free number (D-0xx), the date and
  time, and status `PROPOSED`; it becomes `ADOPTED` only when the PR that adopts it is merged.
  Put the number in the PR title, e.g. *"D-038: gap coding rules"*. If we both grab the same number,
  whoever merges second renumbers theirs.
- **Results get an R-0xx row** in the same table.
- **D-009:** case materials given to the AI come only from outside the Court. No oral argument, no
  justice's words about that case.
- **Independence:** don't open another rater's ratings (e.g. `data/ot2026/ratings_claude.csv`)
  before finishing your own.
- **Never commit** passwords, API keys, `.env` files or the raw database (`data/raw/` is ignored
  for you).
- **One topic per PR.** Easier to review, easier to undo.

## 4. Keeping track of who's doing what

- **Issues** (the Issues tab on GitHub) are our shared to-do list. Open one for any task, question
  or proposal; there are templates for a *decision proposal* and a *task*. Assign it to whoever
  takes it.
- Link a PR to its issue by writing `Closes #12` in the PR description; merging closes the issue.
- Ask Claude at the start of a session: *"Pull main and tell me what changed since I last worked,
  plus any open PRs and issues."*

## 5. When something goes wrong

- **"Merge conflict":** both of us changed the same lines. Ask Claude: *"Resolve the merge conflict
  on this PR and explain each choice."* Check its explanation before accepting.
- **"Push rejected":** someone merged first. Ask Claude to pull main into your branch and try again.
- **Unsure?** Open an issue or message the other person before doing anything to `main`.
