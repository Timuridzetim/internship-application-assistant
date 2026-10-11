# Internship Application Assistant

A working, local Python + SQLite tracker for internship applications. Save a vacancy, check eligibility, prepare materials, submit manually, and keep a dated next action until the outcome is known.

**MVP status:** CLI implemented. No packages, API keys, Docker, or accounts are needed. Python 3.10+ is required. Vacancy discovery, Telegram, FastAPI, ranking, and AI drafting are future work.

## Minimal scenario

One applicant manages a summer internship shortlist. Every vacancy has a source URL, company, role, location, optional deadline, status, notes, and a dated next action. The same exact URL cannot be added twice. Different URLs for the same job still require manual checking.

Success means you can answer: **Where did I apply, what happens next, and what needs attention today?**

## Start

```sh
git clone https://github.com/Timuridzetim/internship-application-assistant.git
cd internship-application-assistant
python tracker.py init
```

On systems where Python is named `python3`, use that instead. On Windows, `py` also works. Run commands from the repository root. Data persists in `data/applications.sqlite3`; an optional `--db PATH` goes before the subcommand.

## End-to-end workflow

The company and vacancy below are fictional. Replace dates with your actual deadlines and review dates.

1. Find a vacancy on a company careers page or university portal. Open the original listing and record its URL.
2. Save it with a concrete eligibility check as the next action:

```sh
python tracker.py add --company "Example Robotics" --role "Computer Vision Intern" --location "Munich" --url "https://example.com/jobs/cv-intern" --deadline 2026-11-15 --next-action "Check year-one eligibility and work authorization" --next-date 2026-10-12 --notes "Summer 2027; duration and language requirements not verified"
```

The tool prints an ID. The examples below assume a new database and ID `1`; use your actual ID.

3. Check academic year, required skills, internship dates, language, relocation, pay, and work authorization. Record unknowns explicitly; residence in one country does not establish eligibility elsewhere. If suitable, prepare a tailored CV and relevant project links:

```sh
python tracker.py update 1 --status preparing --next-action "Tailor CV and select CV project links" --next-date 2026-10-14 --notes "Eligibility checked against original listing; CV: materials/example-robotics/cv.pdf"
```

4. Review your materials and submit on the employer website yourself. Only after successful submission, mark it applied and schedule a follow-up appropriate to the employer's guidance:

```sh
python tracker.py update 1 --status applied --next-action "Check portal and consider follow-up" --next-date 2026-10-28
```

The first transition to `applied` records the computer's current local date in `applied_at`. No submission is performed by this tool.

5. Review the shortlist and today's tasks:

```sh
python tracker.py list
python tracker.py list --status applied
python tracker.py due
python tracker.py due --on 2026-10-28
```

`due` includes overdue/today next actions for active applications, plus overdue/today application deadlines for `saved` and `preparing` roles. Applied roles retain their original deadline, but it no longer triggers an application reminder. Dates use YYYY-MM-DD and the computer's local date. There are no background notifications.

6. When invited, record the interview task. After an outcome, update the status:

```sh
python tracker.py update 1 --status interview --next-action "Prepare Python and ML interview" --next-date 2026-11-02
python tracker.py update 1 --status offer --notes "Offer received; review terms manually"
python tracker.py export exports/applications.csv
```

All statuses: `saved`, `preparing`, `applied`, `interview`, `offer`, `rejected`, `withdrawn`. Transitions are editable to correct mistakes. `offer`, `rejected`, and `withdrawn` leave the daily queue; schedule offer evaluation outside this MVP. Notes updates replace previous notes. There is no full event history or deletion command.

## Project structure

| Path | Purpose |
| --- | --- |
| `tracker.py` | CLI, validation, SQLite storage, daily queue, CSV export |
| `tests/test_tracker.py` | End-to-end workflow and failure checks |
| `.gitignore` | Excludes personal data and application materials |
| `data/applications.sqlite3` | Local database, created automatically |
| `materials/<company>/` | Optional local CV and cover-letter versions |
| `exports/` | Local CSV snapshots |
| `LICENSE` | MIT license |

Keep personal applications, contact details, CVs, and exports out of the public repository. Back up the SQLite file while the CLI is closed; CSV is a readable snapshot, and CSV import is not implemented.

## Verify

```sh
python -m unittest discover -s tests -v
```

Tests use temporary databases and do not modify your tracker.

## Next increments

1. Add event history, editing of vacancy fields, and CSV import.
2. Add rule-based eligibility and priority filters with explicit unknowns.
3. Add permitted feeds/APIs and deduplication by employer job ID.
4. Add a Telegram digest, then a FastAPI interface if needed.
5. Optionally draft summaries and materials from verified profile facts, with manual review and submission.

These increments are planned, not implemented. The MVP intentionally starts with a useful application tracker.

## License

[MIT](LICENSE).
