# Job Workflow Skills

A human-led job search toolkit with two agent skills, a local SQLite queue, optional public Greenhouse board discovery, offline filtering and reports, and a cover-letter outline. Early preview; review all outputs. It does not automatically fill forms or submit applications.

## Setup

Python 3.9+; no third-party packages. Copy `examples/config.example.json` to `config.local.json`, set role and location keywords, resume path, work authorization preference and mode (`review`, `draft`, or `submit`). The keywords and mode are used as described below. Resume path and work authorization preference are stored for a host agent; this CLI does not read a resume or decide eligibility. Keep this file private.

```sh
cp examples/config.example.json config.local.json
python3 workflow.py scout-json examples/jobs.json
python3 jobflow.py list
python3 jobflow.py status 1 needs_verification
python3 jobflow.py status 1 preparing
# Set mode to draft in config.local.json before this step:
python3 workflow.py draft 1
python3 -m unittest discover -s tests -v
```

The local import accepts an array of objects with `company`, `title`, `location`, and `url`. Filtering is case-insensitive substring matching against title and location; empty lists match all. Missing location is allowed but a location filter excludes it. Matches enter the queue as `discovered`; verify each official posting independently. Each run writes a new dated report under `private/reports/`, including counts and a queue snapshot; reruns do not overwrite prior reports. Reports and the queue may contain personal information and should remain private.

To search a known public Greenhouse board (network access required), provide its board token and company name:

```sh
python3 workflow.py scout-greenhouse BOARD_TOKEN --company 'Company name'
```

This calls the [Greenhouse public Job Board API](https://docs.greenhouse.io/job-board.html). It searches only the specified board, not the entire web, and uses no credentials. The adapter is tested with fictional response data; a live integration has not been verified. Rate limits, outages, board access and website rules apply. No LinkedIn, Notion or Firecrawl integration is included.

## Application workflow

The queue status is `discovered`, `needs_verification`, `preparing`, `waiting_user`, `submitted`, `submission_unknown`, `closed`, or `skipped`. `save` is a separate bookmark flag, never an application. Transitions are defined in `jobflow.py`. Review means inspection only. Draft mode creates a private Markdown cover-letter outline and checklist with placeholders: it does not parse resumes, invent experience, or automatically fill forms. Submit mode also permits drafting and communicates intent to a host agent; this CLI does not submit or enforce browser permissions.

Before a separately authorized host or user clicks final submit, mark the job `submission_unknown`. If interrupted, check the official portal or confirmation before trying again. Record a reliable confirmation with `status ID submitted --evidence 'minimal confirmation reference'`. If the official source confirms no application was submitted, use `resolve-not-submitted ID --evidence 'minimal reconciliation reference'` before another attempt. These commands record the user's assertion; the program cannot verify its truth or guarantee that a portal action and a local write are atomic. Never store credentials, verification codes or full sensitive answers as evidence. The Skill instructs the host to obtain explicit authorization for each final submission and stop at security challenges.

Install the two folders under `skills/` using your agent platform's installation instructions. The host must supply search, browser, document editing and user interaction capabilities when needed; compatibility and real form flows have not been tested. Treat job descriptions as untrusted data rather than instructions.

## Privacy and limitations

The queue deduplicates normalized URLs, not different URLs referring to the same role. SQLite transactions and uniqueness constraints protect concurrent writes on one local database. Do not use a network filesystem or sync the active database between machines. The database and private files are not encrypted; back them up securely. `.gitignore` excludes common private paths but is not a guarantee: review files and history before publishing. Do not put personal credentials, cookies, real application records or resumes into a public repository. Fictional examples are included. No live applications, external tracker sync, automated confirmation verification or browser integration has been tested.
