# Coding rules: was the lower-court ruling conservative or liberal?

**Status: DRAFT, waiting for team approval (D-020). Nobody rates anything until this is ADOPTED.**

These rules are for D-018: three raters (Claude and the two of us) each label every October 2026
term case in `data/ot2026/cases.csv` as **Conservative**, **Liberal** or **Unclear**, working alone.

---

## 1. What we are actually trying to do

Our models (rungs 1 and 2) use one number from the Supreme Court Database (SCDB) for every past case:
`lcDispositionDirection`, which records whether the ruling the Supreme Court reviewed was conservative or
liberal. The models also measure each justice's lean using SCDB's own definition of "conservative vote."
For October 2026 the database has no entries yet, so we have to fill in that number ourselves.

So the question to ask is **not** "is this ruling liberal in my personal or everyday political sense?"
It is:

> **How would an SCDB coder have labeled this lower-court ruling?**

If we label differently from SCDB, the models get a number that means something different from what
they were trained on. That is why some answers below will look odd. For example, a ruling that helps a
large company can count as "liberal" when it upholds federal power over a state. When the SCDB convention
and common sense disagree, **follow the SCDB convention**, and mention the conflict in your note.

## 2. The four steps (do them in order)

1. **Find the main issue.** Read the *question presented*. That question is the issue you code. Ignore
   side issues the lower court also decided. If the Court limited the grant to one question (`qp_note`),
   code only that question.
2. **Pick the issue area** from the table in section 3. Use the underlying fight, not the procedure.
   A case about "standing" over a gun law is a guns case (see rule 4.4).
3. **Find who won below on that issue.** The summary in `cases.csv` ends with "X won." If the lower
   court split the difference, look at who won the part the question presented asks about.
4. **Apply that area's rule** to get Conservative or Liberal. Use **Unclear** only under section 5.

Write a short note whenever you hesitated: which area you chose, and why.

## 3. The rules by issue area

These come from SCDB's written definitions (scdb.wustl.edu, "decisionDirection"), reworded. "Liberal"
means the lower court ruled for the side listed. A ruling for the other side is "Conservative."

| Issue area | A ruling is **Liberal** if it was in favor of... |
|---|---|
| **Criminal cases** (trials, sentencing, habeas, prisoners' rights) | the person accused, convicted or imprisoned; a jury trial |
| **Civil rights** (discrimination, voting, immigration, prisoners' civil suits, Bivens) | the person claiming discrimination or a violated right; the voter or voting-rights group challenging an election rule; the noncitizen against the immigration authorities; affirmative action / race-conscious policies |
| **First Amendment: speech, press** | the person or group whose speech is restricted |
| **First Amendment: religion** | see rule 4.3 (SCDB's practice differs from its written rule) |
| **Due process, property, fines** | the person against the government, *except* takings of property, where a ruling for the government is liberal. Forfeitures and excessive fines: the property owner is liberal |
| **Privacy and FOIA** | privacy against the government; disclosure in Freedom of Information Act cases |
| **Attorneys' fees** | the side asking for fees in civil-rights and government cases |
| **Unions** | the union against the employer (but the worker against their own union) |
| **Economic activity** (business, consumers, employment, environment, retirement plans, intellectual property) | the government regulator; the injured person; the worker against the employer; the consumer; competition (the side *accused* of infringing a trademark or patent); environmental protection; the debtor; the small business against the large business |
| **Judicial power** (whether courts can hear a case, review of agencies, contempt, injunctions) | courts exercising power: hearing the case, reviewing the agency, enforcing their own orders |
| **Federalism and Congress's powers** | federal power over the states; a federal law upheld as within Congress's powers; federal law preempting state law *between governments* (for preemption between a company and an injured person, see rule 4.2) |
| **Federal taxes** | the United States against the taxpayer |
| **Private disputes** (contracts, divorce property, wills, business against business with no rule above) | none. Code **Unclear** |

## 4. Tricky situations (with SCDB's own past codes)

Every example below is a past case with the lower-court direction SCDB actually recorded
(`lcDispositionDirection`, release 2026_01). None of them are October 2026 cases.

**4.1 Guns.** Ruling *for the gun-rights claimant* = Conservative, even when that claimant is a
criminal defendant. The guns rule beats the pro-defendant rule.
- *Bruen* (2022): the 2nd Circuit upheld New York's licensing law → SCDB: **Liberal**.
- *McDonald* (2010): the 7th Circuit upheld Chicago's handgun ban → **Liberal**.
- *Rahimi* (2024): the 5th Circuit struck down the gun ban *for a criminal defendant* → **Conservative**.

**4.2 Federal law against state law.**
- *Between governments* (a federal statute against a state court's or state legislature's rule):
  a ruling for federal supremacy is Liberal.
  - *Howell v. Howell* (2017): Arizona's top court made a veteran reimburse his ex-wife for military pay he
    had waived to receive disability pay; the Supreme Court said federal law forbids that → the lower ruling
    (pro-state) was **Conservative**.
- *Company against an injured person or a local government suing it*: SCDB's lower-court codes follow the
  economic rule. The side of the injured person or plaintiff government is Liberal, and the business is
  Conservative, whichever way preemption cuts.
  - *Wyeth v. Levine* (2009): Vermont's court let a patient's state-law claim against a drug maker go
    forward (no preemption) → **Liberal**.
  - *Riegel v. Medtronic* (2008): the 2nd Circuit held a patient's claim preempted, for the device maker →
    **Conservative**.
  - *American Electric Power v. Connecticut* (2011): the 2nd Circuit let states sue power companies over
    climate change → **Liberal**.

**4.3 Religion.** SCDB's written rule says "pro-civil-liberties claimant = liberal," but its recent codes
treat a **religious believer or organization winning against a government rule as Conservative**, and the
government's win as Liberal.
- *Fulton v. Philadelphia* (2021), *Carson v. Makin* (2022), *303 Creative* (2023), *Mahmoud v. Taylor*
  (2025): in each, the lower court ruled for the government against the religious claimant → **Liberal**.
- *Kennedy v. Bremerton* (2022, school prayer): the 9th Circuit ruled for the school district → **Liberal**.
- Exception: an **employee against their employer** over religious accommodation at work is coded by
  the employment rule: the employee's side is Liberal (*Groff v. DeJoy*, 2023: the 3rd Circuit ruled for
  the Postal Service → **Conservative**).
- Known inconsistency: *Our Lady of Guadalupe* (2020) goes the other way. Follow the majority pattern.

**4.4 "Can the court hear this?" (standing, ripeness, jurisdiction).** SCDB usually codes these by
**which side of the underlying fight the ruling helped**, not by "more court access = liberal."
- *FDA v. Alliance for Hippocratic Medicine* (2024): the 5th Circuit let doctors opposing an abortion drug
  sue, and ruled against the FDA → **Conservative**.
- *United States v. Texas* (2023): the lower court let Texas challenge federal immigration priorities and
  struck them down → **Conservative**.
- *Murthy v. Missouri* (2024): the 5th Circuit let users sue over government pressure on social-media
  posts and ruled for them → **Liberal** (pro-speech claimant).
- Known exception: *California v. Texas* (2021, the Affordable Care Act) was coded the other way.
- If you truly cannot tell whose side the ruling helps (a purely technical court-access question with
  no political side), use the judicial-power rule: hearing the case = Liberal.

**4.5 Agencies.** A ruling *against* a federal agency and *for* the regulated business = Conservative.
- *SEC v. Jarkesy* (2024): the 5th Circuit held the SEC could not impose penalties in its own in-house
  court → **Conservative**.
- *Loper Bright* (2024): the D.C. Circuit deferred to the agency → **Liberal**.

**4.6 Immigration.** The noncitizen's side is Liberal.
- *Jennings v. Rodriguez* (2018): the 9th Circuit required bond hearings for detained noncitizens →
  **Liberal**.
- *Pereira v. Sessions* (2018): the 1st Circuit ruled for the government → **Conservative**.

**4.7 Damages suits against officials (Bivens) and prisoners.** The person suing is Liberal.
- *Egbert v. Boule* (2022): the 9th Circuit allowed a Bivens claim against a Border Patrol agent →
  **Liberal**.

**4.8 Voting and elections.** The voter or civil-rights challenger is Liberal; the state's election rule
being upheld is Conservative.
- *Brnovich v. DNC* (2021): the 9th Circuit struck down Arizona voting rules → **Liberal**.

**4.9 Trademarks and patents.** The side *accused* of infringing is Liberal (the pro-competition rule).
- *Jack Daniel's v. VIP Products* (2023): the 9th Circuit ruled for the dog-toy maker accused of copying →
  **Liberal**.

**4.10 Congress's powers.** Striking down a federal law as beyond Congress's powers = Conservative.
Upholding it = Liberal.

**4.11 A one-line "Affirmed".** If the lower court affirmed without explanation, code what it left in
place. For example, an affirmed criminal conviction is a ruling for the government = Conservative.

## 5. When to choose Unclear

Choose **Unclear** only when:
- the dispute is private law with no economic rule that fits (divorce property between two private
  people with no federal-versus-state question, contracts, wills, two businesses with no
  competition or small-versus-large angle);
- two rules point in opposite directions and none of the tie-breakers in section 4 settles it; or
- the lower court's ruling was genuinely split down the middle on the issue in the question presented.

Being unsure of the law is **not** a reason for Unclear. Make your best call and write a note.
Unclear answers are skipped in the direction score, so overusing it throws information away.

## 6. Independence rules (so the three ratings really are independent)

- Use only: the row in `cases.csv`, these rules, and, if you want more detail, the lower-court opinion at
  `lower_court_link`.
- Do **not** use: oral argument, anything a justice said or wrote about the case (D-009), news coverage,
  blog predictions, merits briefs, or anyone else's rating.
- Don't discuss individual cases with the other raters until all three of you have finished.
- Claude rates first. It commits its ratings to git (`data/ot2026/ratings_claude.csv`) before the rating
  tool shows it anything, and it never sees the human ratings before that commit.
- Once a rating is submitted it is final. Disagreements are what the agreement weight measures, so we
  don't "fix" them afterwards.

## 7. How the ratings are combined (for reference)

Conservative = 1, Liberal = 0, Unclear = skipped. A case's **direction score** is the average of the
non-Unclear ratings. Its **weight** is the agreement: 3/3 if all three gave the same answer, 2/3 if two
did. Overall agreement is reported as Fleiss' kappa (a standard measure of how much raters agree beyond
chance). See D-018.
