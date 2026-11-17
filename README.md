# Job Workflow Skills

Two portable skill instructions and a small offline job queue for a human-led job search. This is an early preview. It does not search the web, fill forms, generate resumes or letters, submit applications, or connect to Notion or Firecrawl. Those actions require separate host capabilities or future integrations and have not been tested here.

## Requirements and setup

Python 3.9+ with the standard library. Clone this repository and run from its directory:

```sh
python3 jobflow.py add examples/jobs.json
python3 jobflow.py list
python3 jobflow.py status 1 needs_verification
python3 jobflow.py status 1 preparing
python3 jobflow.py status 1 submission_unknown
# Only after seeing a reliable confirmation, replace the example text:
python3 jobflow.py status 1 submitted --evidence 'Official confirmation observed'
python3 -m unittest discover -s tests -v
```

Copy `examples/config.example.json` to `config.local.json` and edit it privately. It records role, location, resume path, work authorization preference, and desired mode for a human or host agent to read; the CLI does **not** load or enforce it. Do not commit real configuration, resumes or queue databases. Install the two folders under `skills/` using the target agent platform's own skill installation instructions; compatibility with any particular platform has not been tested.

## Modes and workflow

- **Review:** review job information and queue entries. The CLI only stores user-supplied records; verification is manual or host-assisted.
- **Draft:** a host agent may prepare materials, subject to its own capabilities. No draft generator is included.
- **Submit:** a policy for a separately authorized host agent, not a feature implemented by the CLI. The user must authorize each final submission. No submit button is automated here.

The queue status is one of `discovered`, `needs_verification`, `preparing`, `waiting_user`, `submitted`, `submission_unknown`, `closed`, or `skipped`. Run `python3 jobflow.py status --help` for syntax. `save` sets a separate bookmark flag and never changes application status. The allowed transitions are defined in `jobflow.py`. Before a final submission, transition from `preparing` or `waiting_user` to `submission_unknown`. If the operation is interrupted or confirmation cannot be checked, leave it there and inspect the official portal before any retry. Only use `submitted` when a reliable confirmation has been observed; the CLI requires a nonempty evidence description, but cannot verify its truth. It records the status and evidence in one local database transaction. Avoid storing personal details or credentials in evidence.

Records are deduplicated by a normalized URL; tracking parameters beginning `utm_` and URL fragments are removed. Different URLs for the same role will not be merged automatically; review possible duplicates manually. SQLite transactions and a unique constraint protect concurrent writes to the same local database. Do not place the database on a network filesystem or sync it concurrently across machines. Database creation, browser submission and an external tracker cannot form one transaction; a crash or lost confirmation can still require manual reconciliation. SQLite does not encrypt the database. Keep it in a private location and back it up securely.

## Privacy and limitations

`private/`, local configuration, PDFs and databases are ignored by Git, but ignore rules are not a privacy guarantee. Review every file and Git history before publication. Do not place passwords, API keys, cookies, verification codes, or private form answers in the queue. The examples are fictional. No integrations or live website flows have been tested. Notion and Firecrawl are possible future optional integrations, not included features. This project does not bypass website controls.
