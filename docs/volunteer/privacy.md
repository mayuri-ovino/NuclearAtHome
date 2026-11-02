# Privacy policy: Nuclear@Home

Status: DRAFT for human review. Not legal advice. Every item marked **TODO-DECIDE** must be filled in
by the project team before this page is published. Items marked **TODO-VERIFY** describe BOINC
behaviour that we have not yet checked against the BOINC version we run.

Terms used here:
- **BOINC** is the free software that runs volunteer computing projects. It keeps your account and
  your computers' records. Our project runs on a BOINC server.
- **Stats export** is a setting in your BOINC account. It lets the project publish your points and rank.
- **Show computers** is a setting in your BOINC account. It lets the project show your computers'
  hardware and recent work on our website.

## 1. Who runs this project

- Data controller (the organisation that decides how your data is used): Mayuri Ovino (individual), United States
- Contact address for privacy questions: nuclearathome@gmail.com
- Where the servers are hosted (country, and the cloud provider): United States (provider TODO-DECIDE)
- This policy applies to every volunteer, wherever they live. Volunteers in the EU, UK and similar places also have the rights in section 11.

## 2. The short version

- The Nuclear@Home program on your computer collects nothing beyond what BOINC collects by default.
- Your account and your computers' records live in BOINC.
- Our science database keeps a copy of some of those records, so the science can be checked and
  published. Section 4 lists exactly what is copied.
- Public pages show your points and your computers only if you agree in your BOINC account.
- We do not use cookies or trackers on the Nuclear@Home website pages.
- We do not sell or share your data for money.

## 3. What BOINC keeps by default

BOINC keeps these records for every project it runs. We do not add to them.

**Your account**
- Username, email address, password (stored as a hashed form, not the password itself; **TODO-VERIFY**
  which hash BOINC uses), country, an optional web address, your team, and your privacy settings.

**Your computers (called "hosts" in BOINC)**
- Processor (CPU) model, graphics card (GPU) model, operating system name, number of CPU cores,
  and memory size, as BOINC reports them (**TODO-VERIFY** the full list of fields BOINC stores by default).
- Speed benchmarks that BOINC runs on your computer.
- The computer's network name, if BOINC stores it (**TODO-VERIFY**).
- The internet address (IP address) your computer connects from when it contacts the BOINC server.
  BOINC needs this to send and receive work. (**TODO-VERIFY** which BOINC field holds it and how
  long BOINC keeps it.)

**Your work**
- Which work units your computers were sent, when they were sent, when they came back, whether the
  server accepted them, and the points they earned.

**Results you upload**
- Each finished work unit uploads its output files. These files describe a simulated block of
  tungsten atoms: counts of damaged spots, an energy log, progress, snapshots of atom positions, and
  the final arrangement of atoms. They hold no personal information.
- **TODO-VERIFY** that the uploaded file list in the job setup matches this description.

## 4. What our science database keeps

Our science database (PostgreSQL) stores a copy of some of the BOINC records, plus the science
results. Our code does **not** copy these items:
- Computer network names.
- IP addresses.
- Email addresses.
- Passwords or password hashes.

Our code **does** copy these items:

| Item | What it is | Kept as |
|---|---|---|
| Computer summary | CPU model, GPU model, operating system name, number of CPU cores | Per computer, rebuilt from BOINC every hour |
| Recent tasks per computer | Work unit name, app type (CPU or GPU), status, sent and returned times | Last 14 days, rebuilt from BOINC every hour |
| Validated results | Work unit name, energy and temperature of the simulation, points, your user number, computer number, team number, sent and reported times | Kept to the second in the database |
| Cascade statistics | Counts of damaged spots and cluster sizes, snapshot file name | Kept with the result |
| Time per frame samples | Time your computer took per 1% of a work unit, with the time of the sample | Kept with the computer number |
| Daily totals | Points, valid and invalid results, and rank per computer, user and team | Rebuilt each day |
| Badges | Badge names you earned | Kept per user number |
| Privacy copy | Your two BOINC choices (show computers, stats export) | Copied from BOINC each day |

Note: the database keeps your user number and computer number on results even if you turn off
stats export or show computers. Those two settings control what the public website shows. They do
not delete rows from the science database.

## 5. What the public can see

The public website and its data interface (API) show the following.

| Page or data | What is shown | Who controls it |
|---|---|---|
| Project summary | Active computers in the last 7 days, work units per day, totals | Totals only. No user or computer names or numbers. |
| Science bins | Average damage per energy and temperature bin, with error ranges | No user or computer details. |
| Latest cascades | Work unit name, energy, temperature, damage count, points, day | No user or computer details. |
| A user's stats | Rank, points, speed per day, badges, looked up by user number | Shown only if you agreed to stats export in BOINC. |
| A team's stats | Rank, points, speed per day, looked up by team number | Shown without a consent check, but only once at least two volunteers have contributed to the team, so a total never shows one person's points. |
| A computer's stats | Hardware summary, estimated and actual speed, valid and invalid counts for 30 days, recent tasks, time per frame by day | Shown only if the computer's owner has "show computers" turned on in BOINC. |
| 3D cascade files | The simulated atom positions for one work unit | No user or computer details. |

Details for the computer page:
- Task times are shown as dates only, not as the exact time.
- The public website never shows IP addresses, email addresses or host names.

User numbers, team numbers and computer numbers are public numbers that BOINC assigns. Anyone who
knows a number can look up that user's, team's or computer's public page, if the page is allowed.

## 6. Daily BOINC stats export

BOINC creates a standard XML stats file once a day. The project's code does not write this file.
BOINC's own export tool does.

**TODO-VERIFY:** that BOINC's export includes only users who agreed to stats export, and which
fields it includes (for example, whether it includes user names).

## 7. Cookies, trackers and third parties

- The Nuclear@Home website pages (overview, machines, work units, stats, campaigns, join, news and
  the 3D viewer) set no cookies. They load no advertising or analytics code.
- The 3D viewer loads its own copy of the Three.js graphics library from our server, not from another
  company's site.
- BOINC's own account pages, such as the login page, may set a cookie that keeps you signed in.
  **TODO-VERIFY** the cookie names BOINC sets.
- Our web server writes access logs, which can include IP addresses. They are kept for 7 days,
  only to stop abuse and fix faults, then deleted.

## 8. How long we keep data

| Data | How long | Notes |
|---|---|---|
| BOINC account | Until you delete it | You can delete your account in BOINC (**TODO-VERIFY** the exact page). |
| Science database rows | Kept for the science | See section 9 for what changes when an account is deleted. |
| Web server logs | 7 days | See section 7. |
| Server backups | 14 days | Nightly off-site backups; each is deleted after 14 days. |
| BOINC's internal records of results and tasks | **TODO-VERIFY** BOINC's default purge time | |

## 9. What happens when you delete your account

Our daily stats job does the following for users who no longer exist in BOINC:
- Sets your user, computer and team numbers on your past results to 0. The results and their
  science statistics stay in the database, but they no longer link to you.
- Deletes your computers' time-per-frame samples and daily totals.
- Deletes your per-user daily totals and badges.

The hourly job drops computers that BOINC no longer lists.

The change happens when the daily job runs, not at the moment you delete your account.
This takes at most 30 days, including backups being replaced.

## 10. Legal basis

| Use | Legal basis |
|---|---|
| Your account, sending work, checking results and awarding points | Contract: needed to provide the service you signed up for |
| Keeping results and their numbers in the science database | Legitimate interest: open, checkable science |
| Public stats and showing your computers | Consent: you can withdraw it at any time |
| Web server logs and security checks | Legitimate interest: keeping the project safe and working |

Where we ask for consent, the wording is in `gdpr_consent.md`. Consent is recorded in BOINC with the
time you gave it.

## 11. Your rights

If data protection law applies to you, you have these rights.

- **Access.** You can see your account in BOINC. **TODO-VERIFY** which BOINC pages show your stored data.
- **Correction.** You can change your account details in BOINC.
- **Erasure.** You can delete your BOINC account. See section 9 for what happens. **TODO-VERIFY**
  whether BOINC deletes or only detaches your computers' records.
- **Portability.** You can ask for a copy of your data in a common format. **TODO-VERIFY** BOINC's
  data export option and what it includes.
- **Objection.** You can object to a use of your data. Email nuclearathome@gmail.com.
- **Withdraw consent.** Turn off stats export or show computers in your BOINC account. Our code
  reads the most recent choice, so the change takes effect at the next daily job.
- **Complaint.** You can complain to a data protection authority. If you live in the EU or UK, you
  can complain to the data protection authority where you live.

## 12. Children

Anyone aged 13 or over can join. Children under 13 need a parent or guardian, who sets up the
account for them. If you believe a child under 13 gave us personal data without a parent's consent,
email nuclearathome@gmail.com and we will delete it.

## 13. Security

- The public API is read-only. It never shows IP addresses, email addresses or canary status
  (the hidden reference runs that we use to check the software).
- The database role used by the public API cannot read the hidden reference-run tables.
- **TODO-VERIFY** that the live site serves HTTPS only.

## 14. Changes to this policy

Changes are announced on the project's News page and on Discord before they take effect.

Last updated: **TODO-DECIDE** (date)
