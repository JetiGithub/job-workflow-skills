# Using these workflows with Grok Bot / 在 Grok Bot 中使用这些工作流程

This repository is an early preview of two instructions intended for Grok Bot, plus optional Python helpers. It has **not been installed or end-to-end tested in Grok Bot**. The exact available tools, files, approvals and connectors depend on the user's account and Bot.

本仓库是面向 Grok Bot 的两个工作流程说明及可选 Python 辅助工具的早期预览版，**尚未在 Grok Bot 内安装或完成端到端测试**。实际可用的工具、文件、审批和连接取决于用户账号及 Bot。

1. Review `skills/job-scout/SKILL.md` and `skills/application-assistant/SKILL.md`. In Grok Bot, ask the relevant Bot to read the desired instructions and save them as a private skill. The official [Skills and routines guide](https://docs.x.ai/grok-bot/skills-routines-and-automations) describes saving skills and enabling private skills. It does not establish that a GitHub URL automatically installs these scripts; this project does not claim one-click installation.

1. 阅读 `skills/job-scout/SKILL.md` 和 `skills/application-assistant/SKILL.md`。在 Grok Bot 中，请对应 Bot 读取所需说明并将其保存为私有 Skill。[官方指南](https://docs.x.ai/grok-bot/skills-routines-and-automations)介绍了保存和启用私有 Skill；它未说明 GitHub 链接会自动安装这些脚本，本项目也不声称支持一键安装。
2. If using the Python helpers, make a copy of the full repository accessible to both Bot execution environments. Verify Python 3.9+ and the shared private database path on a suitable local filesystem. A copied skill text by itself does not provide these files. If Bots cannot access the same database, use an explicitly approved private handoff instead and do not run the helper against separate copies as if synchronized.

2. 如需 Python 辅助工具，请让两个 Bot 的执行环境都能访问完整仓库副本。检查 Python 3.9+，并确认适合的本地文件系统上的同一个私有数据库路径。复制 Skill 文本本身不会提供脚本文件。若两个 Bot 无法访问同一数据库，应使用经用户明确同意的私有交接方式，不要把各自独立的数据库副本当作已同步。
3. Create private configuration and candidate profile files from the fictional examples. Give the Bots only the access needed. Do not place resumes, credentials, real job records or configuration in the public repository. Use the platform's secure sign-in for credentials.

3. 根据虚构示例创建私有配置和候选人资料，只授予 Bot 必要权限。不要将简历、凭据、真实岗位记录或配置放入公开仓库；凭据使用平台安全登录方式。
4. Test the queue and report with `examples/jobs.json`, then check the handoff in the second Bot. Test Review and Draft modes before any schedule or real application. The repository's tests cover local Python behavior, not actual Grok Bot installation, browser interactions, external connections or submission.

4. 使用 `examples/jobs.json` 测试队列和报告，再检查第二个 Bot 能否接收交接。在安排定时任务或真实申请前，先测试 Review 和 Draft 模式。仓库测试覆盖本地 Python 行为，并不验证真实 Grok Bot 安装、浏览器交互、外部连接或提交。
5. Ask Grok Bot to set up a routine only after a successful manual test and only if desired. Confirm schedule, time zone, owner, sources, storage and failure behavior. A routine or skill does not override the requirement for explicit authorization of each final application submission.

5. 仅在手动测试成功且用户希望定时运行时，请 Grok Bot 创建 routine。确认时间、时区、所属 Bot、来源、存储和失败处理。Routine 或 Skill 不会取代每次最终提交申请前的明确授权要求。

For local helper commands and current limitations see the [README](README.md). Optional connectors, browser access and document generation are host capabilities and are not bundled integrations.

本地辅助命令和当前限制见 [README](README.md)。可选连接器、浏览器访问和文档生成属于宿主能力，并非本项目附带的集成。
