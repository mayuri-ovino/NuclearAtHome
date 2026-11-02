# Consent texts for Nuclear@Home (BOINC consent system)

Status: DRAFT for human review. The wording is a proposal. The project team must approve it.
Items marked **TODO-VERIFY** are BOINC details we have not checked against the BOINC version we
run. Do not publish this page until they are checked.

Terms used here:
- **Consent record**: a row in BOINC's database that says a user agreed (or did not agree) to one
  thing, and when.
- **Consent type**: one kind of consent, identified by a short code (its "shortname").

## 1. How BOINC stores consent

These table and column names are used by our code (`stats/jobs.py`), so they are checked against the repo:

- `consent_type` table: `id`, `shortname` (the short code, for example `STATSEXPORT`).
- `consent` table: `userid`, `consent_type_id`, `consent_flag` (1 = yes, 0 = no), `consent_time`.

Our daily stats job reads the most recent row for each user. If a user has no row, the job treats
the answer as **no**. A newer row with `consent_flag` = 0 withdraws earlier consent.

## 2. Consent types for Nuclear@Home

| Shortname | Purpose | Checkbox text (proposed) | Required to join? |
|---|---|---|---|
| `ENROLL` **TODO-VERIFY** that BOINC uses this shortname for sign-up terms | Agreement to the project terms and privacy policy at sign-up | "I have read the Nuclear@Home privacy policy and I agree to the project terms." | **TODO-DECIDE** |
| `STATSEXPORT` | Publish points, rank and badges in the public stats, and include the user in the daily BOINC stats export | "Show my points, rank and badges on the Nuclear@Home public stats pages, and include me in the daily BOINC stats export. I can turn this off at any time." | No. Default: **off** (TODO-DECIDE to confirm) |
| Show computers (not a consent type in our code) | Show your computers' hardware and recent work on the public site | "Show my computers' hardware and recent work on the Nuclear@Home website. I can turn this off at any time." | No. Default: **off** (TODO-DECIDE to confirm) |

Notes on the table:
- "Show computers" is a BOINC account setting, not a consent record in our code. Our database
  reads it from the user's `show_hosts` column (`stats/jobs.py`). **TODO-VERIFY** where BOINC shows
  this setting to users, and whether it can also be asked at sign-up.
- Each checkbox text should stay short. Do not add tick-by-default boxes.
- A user who does not tick a box is still allowed to join and use BOINC normally. **TODO-DECIDE:**
  confirm this matches the project's policy.

## 3. How to turn these on in BOINC

These steps describe the BOINC server administration pages. Confirm each step on the BOINC version
installed on our server before relying on it.

1. **Project configuration.** In the project's `config.xml`, the BOINC documentation names an option
   `enable_privacy_by_default`. **TODO-VERIFY** the exact element name, its effect, and whether it
   should be on for the public alpha.
2. **Consent types.** Log in as the project administrator. Open the consent-type management page
   (**TODO-VERIFY** the path, which we believe is `html/ops/manage_consent_types.php` in the BOINC web
   code). Add each consent type from section 2 with its shortname and checkbox text.
3. **Default state.** Set `STATSEXPORT` and the "show computers" choice to **not agreed** by default.
   **TODO-VERIFY** how BOINC sets a default for a consent type.
4. **Sign-up page.** Check that the sign-up form shows the consent checkboxes. **TODO-VERIFY** how
   BOINC shows them (required or optional, and where).
5. **Withdrawal.** Check how a user withdraws consent in BOINC (**TODO-VERIFY**). Our code reads the
   latest row, so a withdrawal written by BOINC takes effect at the next daily job.
6. **Test with a test account.** Create a test account, tick and untick each box, and check the
   `consent` rows and the public pages. Confirm that the stats page hides the user until consent is
   given.

## 4. What the consent covers and does not cover

Consent covers only the items in section 2. It does not cover:
- Our science database keeping your user, computer and result numbers (described in the privacy
  policy, section 4). This is a use of data for the science, and its legal basis is legitimate
  interest (privacy policy, section 10).
- BOINC's own handling of your account, which is set by BOINC and by the privacy policy.

## 5. Records to keep

- Keep the `consent` rows. They show when each answer was given.
- If a consent type's text changes, record the date of the change and the old text, so each old
  answer can be matched to the text the user saw. The history is kept in git, in this file's history.

## 6. Open items for the human

- **TODO-DECIDE:** approve each checkbox text in section 2.
- **TODO-DECIDE:** whether `ENROLL` is required at sign-up.
- **TODO-DECIDE:** default states (both proposed as off).
- **TODO-VERIFY:** every BOINC mechanism marked above.
