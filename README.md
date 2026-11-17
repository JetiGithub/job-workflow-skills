# Job Workflow Skills / 求职工作流 Skills

**Grok Bot users:** start with [GROK_BOT_SETUP.md](GROK_BOT_SETUP.md). These workflows have not yet been tested inside Grok Bot.

**Grok Bot 用户：**请先阅读 [GROK_BOT_SETUP.md](GROK_BOT_SETUP.md)。这些工作流程尚未在 Grok Bot 内测试。

A human-led job search toolkit with two agent skills, a local SQLite queue, optional public Greenhouse board discovery, offline filtering and reports, a cover-letter outline, and application packets based on candidate-approved facts. Early preview; review all outputs. It does not automatically fill forms or submit applications.

这是一个由用户主导的求职工具包，包含两个 Skill、本地 SQLite 队列、可选的公开 Greenhouse 职位搜索、离线筛选和报告、求职信提纲，以及基于候选人确认事实的申请材料包。目前为早期预览版，请核对所有输出；它不会自动填写表单或提交申请。

## Setup / 设置

Python 3.9+; no third-party packages. Copy `examples/config.example.json` to `config.local.json`, set role and location keywords, resume path, work authorization preference and mode (`review`, `draft`, or `submit`). The keywords and mode are used as described below. Resume path and work authorization preference are stored for a host agent; this CLI does not read a resume or decide eligibility. Keep this file private.

需要 Python 3.9 或更高版本，无需第三方依赖。将 `examples/config.example.json` 复制为 `config.local.json`，填写职位与地点关键词、简历路径、工作授权偏好及模式（`review`、`draft` 或 `submit`）。关键词和模式的用途见下文。简历路径和工作授权偏好供宿主助手使用；命令行工具不会读取简历或判断资格。请将此文件保密。

```sh
cp examples/config.example.json config.local.json
python3 workflow.py scout-json examples/jobs.json
python3 jobflow.py list
python3 jobflow.py status 1 needs_verification
python3 jobflow.py status 1 preparing
# Set mode to draft in config.local.json before this step.
# 执行前请在 config.local.json 中将 mode 设为 draft。
python3 workflow.py draft 1
# Copy and edit the fictional example privately before using it.
# 使用前请私下复制并修改虚构示例。
cp examples/candidate.example.json private/candidate.json
python3 application.py 1 --profile private/candidate.json
python3 jobflow.py history 1
python3 -m unittest discover -s tests -v
```

The local import accepts an array of objects with `company`, `title`, `location`, and `url`. Filtering is case-insensitive substring matching against title and location; empty lists match all. Missing location is allowed but a location filter excludes it. Matches enter the queue as `discovered`; verify each official posting independently. Each run writes a new dated report under `private/reports/`, including counts and a queue snapshot; reruns do not overwrite prior reports. Reports and the queue may contain personal information and should remain private.

本地导入接受对象数组，字段为 `company`、`title`、`location` 和 `url`。职位和地点筛选采用不区分大小写的子字符串匹配；空列表匹配全部。可以缺少地点，但设置地点筛选后此类岗位会被排除。匹配岗位以 `discovered` 状态进入队列；请独立核验官方职位页面。每次运行都会在 `private/reports/` 下生成新的带日期报告，包含统计和队列快照，不会覆盖旧报告。报告和队列可能含个人信息，应保持私有。

To search a known public Greenhouse board (network access required), provide its board token and company name:

要搜索已知的公开 Greenhouse 招聘板块，请提供其 board token 和公司名称（需要网络）：

```sh
python3 workflow.py scout-greenhouse BOARD_TOKEN --company 'Company name'
```

A single posting can be checked with `python3 workflow.py verify-greenhouse ID BOARD_TOKEN POSTING_ID`. This compares its returned URL to the queued URL and reports the title; it does not change status, confirm eligibility, or guarantee that the position is open. Errors and URL mismatches need manual review.

可以使用 `python3 workflow.py verify-greenhouse ID BOARD_TOKEN POSTING_ID` 核对单个岗位。该命令比较返回链接与队列链接并显示职位名称；它不会改变状态、确认资格或保证职位仍在招聘。错误和链接不一致需要人工复核。

This calls the [Greenhouse public Job Board API](https://docs.greenhouse.io/job-board.html). It searches only the specified board, not the entire web, and uses no credentials. The adapter is tested with fictional response data; a live integration has not been verified. Rate limits, outages, board access and website rules apply. No LinkedIn, Notion or Firecrawl integration is included.

该命令调用 [Greenhouse 公开职位 API](https://docs.greenhouse.io/job-board.html)，只搜索指定板块，无需凭据。适配器仅使用虚构响应测试，尚未验证实时连接；仍受频率限制、服务故障、板块访问权限和网站规则约束。项目未包含 LinkedIn、Notion 或 Firecrawl 集成。

## Application workflow / 申请流程

The queue status is `discovered`, `needs_verification`, `preparing`, `waiting_user`, `submitted`, `submission_unknown`, `closed`, or `skipped`. `save` is a separate bookmark flag, never an application. Transitions are defined in `jobflow.py`. Review means inspection only. Draft mode can create a private Markdown outline, or an application packet containing a resume-content section and cover-letter draft from a candidate-approved JSON profile. Claims are copied from that profile; the tool does not parse an existing resume, tailor claims to a job description, guarantee document formatting, invent experience, or automatically fill forms. The candidate must edit and verify every statement. The packet is Markdown, not a finished PDF or DOCX resume. Submit mode also permits drafting and communicates intent to a host agent; this CLI does not submit or enforce browser permissions.

队列状态包括 `discovered`（已发现）、`needs_verification`（待核验）、`preparing`（准备中）、`waiting_user`（等待用户）、`submitted`（已提交）、`submission_unknown`（提交结果未知）、`closed`（已关闭）和 `skipped`（跳过）。`save` 是独立的收藏标记，不代表申请。状态转换定义在 `jobflow.py` 中。Review 仅供检查；Draft 可根据候选人确认的 JSON 资料生成私有 Markdown 提纲或包含简历内容和求职信草稿的材料包。事实直接来自资料；工具不会解析现有简历、按职位改写事实、保证排版、编造经历或自动填表。用户须编辑并核对每一项陈述。材料包是 Markdown，不是完成的 PDF 或 DOCX 简历。Submit 模式也允许草拟，并向宿主助手表明意图；命令行工具不会提交申请或强制浏览器权限。

Before a separately authorized host or user clicks final submit, mark the job `submission_unknown`. If interrupted, check the official portal or confirmation before trying again. Record a reliable confirmation with `status ID submitted --evidence 'minimal confirmation reference'`. If the official source confirms no application was submitted, use `resolve-not-submitted ID --evidence 'minimal reconciliation reference'` before another attempt. These commands record the user's assertion; the program cannot verify its truth or guarantee that a portal action and a local write are atomic. Never store credentials, verification codes or full sensitive answers as evidence. The Skill instructs the host to obtain explicit authorization for each final submission and stop at security challenges.

获得单独授权的宿主或用户点击最终提交前，应先将岗位标记为 `submission_unknown`。若过程被中断，重试前须检查官方门户或确认信息。可靠确认后，使用 `status ID submitted --evidence 'minimal confirmation reference'` 记录；若官方来源确认未提交，则在重试前使用 `resolve-not-submitted ID --evidence 'minimal reconciliation reference'`。这些命令记录用户提供的信息，程序无法核实其真实性，也无法保证网站操作和本地写入是一个原子事务。不要将凭据、验证码或完整敏感回答作为证据保存。Skill 要求宿主在每次最终提交前取得明确授权，并在遇到安全验证时停止。

Install the two folders under `skills/` using your agent platform's installation instructions. The host must supply search, browser, document editing and user interaction capabilities when needed; compatibility and real form flows have not been tested. Treat job descriptions as untrusted data rather than instructions.

按照所用助手平台的安装说明安装 `skills/` 下的两个文件夹。需要时，搜索、浏览器、文档编辑和用户交互能力由宿主提供；平台兼容性和真实表单流程尚未测试。职位描述应作为不可信数据处理，不应当作指令执行。

## Privacy and limitations / 隐私与限制

The queue deduplicates normalized URLs, not different URLs referring to the same role. SQLite transactions and uniqueness constraints protect concurrent writes on one local database. Do not use a network filesystem or sync the active database between machines. The database and private files are not encrypted; back them up securely. `.gitignore` excludes common private paths but is not a guarantee: review files and history before publishing. Do not put personal credentials, cookies, real application records or resumes into a public repository. Fictional examples are included. No live applications, external tracker sync, automated confirmation verification or browser integration has been tested.

队列按规范化链接去重，不能自动识别指向同一岗位的不同链接。SQLite 事务和唯一约束保护同一本地数据库的并发写入；不要使用网络文件系统，也不要在多台机器间同步正在使用的数据库。数据库和私有文件未加密，应安全备份。`.gitignore` 排除常见私有路径，但不能保证隐私；发布前请审查文件和历史。不要将个人凭据、Cookie、真实申请记录或简历放入公开仓库。示例均为虚构；真实申请、外部追踪同步、自动确认核验及浏览器集成均未测试。
