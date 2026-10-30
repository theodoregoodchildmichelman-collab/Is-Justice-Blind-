# Rung 3: what we collect per case (PROPOSED, D-024)

Rung 3 asks a general AI model "How would Justice X vote?" using only material from outside the
Court (D-009). This plan says where that material comes from, how long it gets, and what gets cut.

## Where it comes from

Everything comes from the case's docket page on supremecourt.gov
(`https://www.supremecourt.gov/docket/docketfiles/html/public/<docket>.html`), which links a PDF of
every filing. Free, public, and the same source for every case.

| Input | What it is | Typical length |
|---|---|---|
| Question presented | The question the Court agreed to decide (already in `cases.csv`) | under 1k tokens |
| Lower-court decision | The opinion under review, from the cert petition's appendix | 5k-30k tokens; 60k+ with dissents |
| Cert petition + brief in opposition | Why the losing side wants review, and the reply | 10k-15k tokens each |
| Merits briefs | Petitioner's brief, respondent's brief, petitioner's reply | ~17k, ~17k, ~8k tokens |
| Solicitor General's brief | The federal government's view, when it is not a party | ~12k tokens |
| Other amicus briefs | Outside groups; often 10-50 per case | ~12k tokens each |

(A token is about 3/4 of a word. Word limits from the Court's Rule 33 set most of these lengths.)
The full record for one case runs from about 100k to over 700k tokens: too long to send nine times.

**Excluded** (D-009): oral argument transcripts and audio, anything filed after argument, news
coverage, and anything a justice said or wrote about the case. Whoever collects the material opens
only the docket page and its PDFs, never news or argument coverage. If the docket page shows a
decision, we do not predict that case.

## How long it gets: a fixed 60k-token packet

Each case gets the same budget, split into fixed slots. Unused space in one slot is not handed to
another, so packets stay comparable across cases.

| Order | Slot | Cap (tokens) | If the document is longer |
|---|---|---|---|
| 1 | Question presented | full | never cut |
| 2 | Lower-court decision | 15k | keep the majority opinion from the start; dissents below get up to 2k each, from their opening |
| 3 | Petitioner's merits brief | 12k | keep the Summary of Argument whole, then the Argument from the start until the cap |
| 4 | Respondent's merits brief | 12k | same |
| 5 | Petitioner's reply brief | 5k | same |
| 6 | Solicitor General's brief (if not a party) | 4k | Summary of Argument only |
| 7 | Other amicus briefs | 8k | a one-line list of every amicus and the side it supports; then Summary of Argument sections, split evenly between the two sides, taken in docket filing order |
| 8 | Cert petition + brief in opposition | 4k | "Reasons for granting" sections only; cut first because the merits briefs replace them |

Every cut is marked in the text as `[... cut ...]`, and the packet's `manifest.json` records each
input's source link, original length, kept length, and whether it was cut.

**Why cut this way:** the parties' own briefs carry the case; the Summary of Argument is the
lawyers' own short version, so keeping it whole loses the least. Amici are numerous and repetitive,
so we keep the full list (which signals who cares about the case) and a balanced sample of their
arguments. Choosing amici by filing order, not by our judgment of quality, keeps us from picking.

## When we predict

- **Earliest:** once the respondent's merits brief and the reply brief are filed (usually a week or
  two before argument).
- **Latest:** before the decision. Cases argued in October can be decided from late November, so
  they go first; we work through cases in argument order.
- **Fallback:** if a decision may come before a full packet is ready, predict from the minimal
  packet (question presented + lower-court summary, `--minimal`) and label it. Never skip a case
  to wait for more material.

## How the files are stored

- Downloaded PDFs: `data/raw/briefs/<docket>/` (not in git; they are large and public anyway).
  PDFs are untrusted files, so text is pulled out with a script that only reads them.
- Packet: `data/ot2026/packets/<docket>/manifest.json` plus one `.txt` per input, committed to git
  before the prediction, so anyone can see exactly what the model saw.

## Cost on a Pro subscription

9 prompts x 60k tokens is about 540k tokens of input per case, roughly 19 million for 35 cases.
Because the justice's name comes after the materials, prompts 2-9 for a case start with the same
text as prompt 1, and that shared start can be reused from a cache, which costs much less. Even so,
expect usage limits to cap us at a few cases per session window. Running all 35 may take several
days of batches; the code saves after every justice, so a run can stop and resume.

## Needs a decision

- New dependency: `pypdf` (a standard library for pulling text out of PDFs).
- Downloading the PDFs from supremecourt.gov (about 30-60 files per case).
