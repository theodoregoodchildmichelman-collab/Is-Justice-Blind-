# October 2026 term data

## cases.csv

One row per docket the Court granted for argument in OT2026, as of 2026-10-30 (35 rows). Shared with
the rung 3 session, so the columns stay fixed.

| column | meaning |
|---|---|
| `docket` | Supreme Court docket number |
| `case_name` | short case name |
| `status` | `rate` = gets a direction rating; `dismissed` = left the docket before argument (no rating) |
| `consolidated_with` | docket argued together with this one (each docket is still rated separately, since each has its own lower court) |
| `lower_court` | court whose decision is under review |
| `lower_court_docket` | that court's docket number(s) |
| `lower_court_date` | date of that decision (YYYY-MM-DD) |
| `lower_court_link` | PDF containing that decision (usually the cert petition's appendix on supremecourt.gov) |
| `lower_court_summary` | neutral 3-5 sentence summary of what it held and who won, written from the lower-court opinion |
| `question_presented` | the question the Court agreed to decide (the Court's limited or added questions where it wrote its own) |
| `qp_note` | how the grant was limited or changed, if at all |
| `qp_source` | the Court's official question-presented PDF |

**Sources:** the Court's Granted & Noted List (as of 2026-10-13), plus the order lists of 2026-10-19 (two
new grants) and 2026-10-20/21/27 (no new grants); docket pages and QP PDFs on supremecourt.gov. The
summaries come only from the lower-court opinions (and, where an opinion was very short, the petition
appendix). Per D-009, nothing comes from oral argument or anything a justice said.

**Original-jurisdiction cases:** none were granted for argument this term (none appear on the Court's
list), so none are listed.

**Not rated:** 25-886 *Genalo v. Black* (dismissed under Rule 46 on 2026-09-11).

**Updating:** if the Court grants more cases for this term, add rows at the bottom. Don't rename or
reorder columns.
