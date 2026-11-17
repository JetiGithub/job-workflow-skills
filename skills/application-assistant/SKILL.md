---
name: application-assistant
description: Review a private job queue, prepare approved materials, and assist with authorized applications. 复核私有岗位队列、准备经确认的材料并协助获授权的申请。
---
# Application Assistant for Grok Bot / Grok Bot 申请助手

Use this skill to process a queue produced by Job Scout. The host must provide any search, browser, document, vault, or connector capability used. Availability and permissions differ; never claim a capability or successful action that was not observed.

使用此 Skill 处理 Job Scout 生成的队列。所需搜索、浏览器、文档、凭据保险库或连接器能力由宿主提供，实际权限与可用性因环境而异；未观察到的能力或成功操作不得声称存在。

## Inputs and handoff / 输入与交接

Agree on the same private queue and config paths used by Job Scout. If using the Python helper, both Bots need the full repository checkout, Python 3.9+, and access to the same local database. `python3 jobflow.py --db <shared-db> list` shows the queue. If shared access is absent, stop rather than create a disconnected copy. Keep resumes, profile, drafts, confirmations and database out of public repositories. Obtain the user's approved facts, resume choice, work authorization and availability answers; ask when unknown, never infer them.

与 Job Scout 约定同一私有队列和配置路径。如使用 Python 辅助工具，两个 Bot 需要完整仓库副本、Python 3.9+ 和同一本地数据库的访问权限。使用 `python3 jobflow.py --db <shared-db> list` 查看队列；无法共享时应停止，不要创建互不相通的副本。简历、资料、草稿、确认信息和数据库不得放入公开仓库。获取用户确认的事实、简历选择、工作授权和可用时间；不明确时询问，不得推断。

## Workflow / 工作流程

1. Check the official posting and current requirements using available permitted tools; record source and time. An imported row or a bookmark is not proof that a role is open or applied. Move through `needs_verification` and `preparing` with the queue helper as appropriate. If unavailable, blocked, closed, or uncertain, record the appropriate state and explain why.

1. 使用可用且允许的工具核验官方职位及当前要求，记录来源和时间。导入记录或收藏不代表职位仍开放或已经申请。适当使用队列辅助工具推进至 `needs_verification` 和 `preparing`；如职位不可用、受阻、关闭或状态不明，应记录相应状态并说明原因。
2. In Review mode inspect and report only. In Draft mode prepare materials from user-approved facts. The optional `python3 application.py ID --db <shared-db> --config <private-config> --profile <private-profile.json>` generates a Markdown draft; it is not a finished resume or an independently verified statement. Review each claim, job-specific requirement, attachment, and answer with the user. In Submit mode continue only within the user's specific authorization and the platform's permissions. Do not bypass site security, CAPTCHAs or access controls; use the platform's secure sign-in or ask the user to take over.

2. Review 模式仅检查和报告。Draft 模式根据用户确认的事实准备材料；可选命令 `python3 application.py ID --db <shared-db> --config <private-config> --profile <private-profile.json>` 生成 Markdown 草稿，它不是完成的简历，也不独立核实陈述。与用户核对每项事实、职位要求、附件和回答。Submit 模式仅在用户具体授权和平台权限范围内继续。不要绕过网站安全措施、验证码或访问控制；使用平台安全登录或请用户接手。
3. Before a final submit action, obtain explicit approval for that job and durably set `submission_unknown`. If recording the state fails, do not submit. Never repeat a submit while the result is uncertain. Check the official portal or reliable confirmation; only then record `submitted` with a minimal non-secret evidence reference. A saved job, form draft, or click alone is not confirmation. If an official source confirms no submission occurred, record that evidence via `resolve-not-submitted` before retrying. If confirmation or synchronization fails, preserve `submission_unknown` and ask the user to reconcile. The helper cannot verify evidence and cannot atomically commit an external portal action and local state.

3. 最终提交前，取得该岗位的明确批准，并持久记录 `submission_unknown`；若记录失败，不得提交。结果不确定时绝不重复提交。检查官方门户或可靠确认信息后，才可使用最少的非敏感证据标记 `submitted`；收藏、表单草稿或单次点击都不是提交确认。若官方来源确认未提交，重试前须通过 `resolve-not-submitted` 记录证据。若确认或同步失败，保留 `submission_unknown` 并请用户核对。辅助工具无法验证证据，也无法将外部网站操作与本地状态写入合为原子事务。
4. Report each job's actual state, evidence location, unresolved questions and failures. Never record passwords, verification codes, cookies or full sensitive answers in the queue or logs. Optional Notion or Firecrawl tools are only available if the user has connected and authorized them; no integration is bundled here.

4. 报告每个岗位的实际状态、证据位置、未解决问题和失败情况。不得在队列或日志中保存密码、验证码、Cookie 或完整敏感回答。Notion 或 Firecrawl 仅在用户已连接并授权且工具可用时使用；本项目未附带这些集成。
