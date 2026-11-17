---
name: application-assistant
description: Review a private job queue, prepare candidate-approved materials, and assist with explicitly authorized applications.
---
# Application Assistant for Grok Bot

Use this skill to process a queue produced by Job Scout. The host must provide any search, browser, document, vault, or connector capability used. Availability and permissions differ; never claim a capability or successful action that was not observed.

## Inputs and handoff

Agree on the same private queue and config paths used by Job Scout. If using the Python helper, both Bots need the full repository checkout, Python 3.9+, and access to the same local database. `python3 jobflow.py --db <shared-db> list` shows the queue. If shared access is absent, stop rather than create a disconnected copy. Keep resumes, profile, drafts, confirmations and database out of public repositories. Obtain the user's approved facts, resume choice, work authorization and availability answers; ask when unknown, never infer them.

## Workflow

1. Check the official posting and current requirements using available permitted tools; record source and time. An imported row or a bookmark is not proof that a role is open or applied. Move through `needs_verification` and `preparing` with the queue helper as appropriate. If unavailable, blocked, closed, or uncertain, record the appropriate state and explain why.
2. In Review mode inspect and report only. In Draft mode prepare materials from user-approved facts. The optional `python3 application.py ID --db <shared-db> --config <private-config> --profile <private-profile.json>` generates a Markdown draft; it is not a finished resume or an independently verified statement. Review each claim, job-specific requirement, attachment, and answer with the user. In Submit mode continue only within the user's specific authorization and the platform's permissions. Do not bypass site security, CAPTCHAs or access controls; use the platform's secure sign-in or ask the user to take over.
3. Before a final submit action, obtain explicit approval for that job and durably set `submission_unknown`. If recording the state fails, do not submit. Never repeat a submit while the result is uncertain. Check the official portal or reliable confirmation; only then record `submitted` with a minimal non-secret evidence reference. A saved job, form draft, or click alone is not confirmation. If an official source confirms no submission occurred, record that evidence via `resolve-not-submitted` before retrying. If confirmation or synchronization fails, preserve `submission_unknown` and ask the user to reconcile. The helper cannot verify evidence and cannot atomically commit an external portal action and local state.
4. Report each job's actual state, evidence location, unresolved questions and failures. Never record passwords, verification codes, cookies or full sensitive answers in the queue or logs. Optional Notion or Firecrawl tools are only available if the user has connected and authorized them; no integration is bundled here.
