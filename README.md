# 小龙虾自己做的 Skills

从实际协作问题整理出的 OpenClaw 工作流封装。目前公开 **14 项审阅版**，另有 4 项暂缓，不把已知问题带进运行目录。

[下载 14 项合集 ZIP](https://github.com/seanyeagerx-svg/lobster-made-skills/releases/download/v0.2.0-review/lobster-made-skills-v0.2.0-review.zip) · [版本与校验文件](https://github.com/seanyeagerx-svg/lobster-made-skills/releases/tag/v0.2.0-review)

下载包把全部已公开 Skill 放在同一个 `skills/` 目录，附安装说明、审查记录和合成测试。名称指我们与小龙虾在项目中编写和迭代的封装；外部方法与平台文档仍按各项注明的出处署源。

## 怎么选

| Skill | 用途 | 发布结论 |
|---|---|---|
| attribution-discipline | 归因纪律 | 公开审阅版 |
| autonomous-evolution | 经验复盘 | 暂缓 |
| cross-window-reconciliation | 跨窗口对账 | 公开审阅版 |
| feishu-media-send | 飞书媒体发送 | 暂缓 |
| feishu-turn-recovery | 飞书漏答恢复 | 公开审阅版 |
| gateway-tailscale-access | 网关接入核查 | 公开审阅版 |
| github-device-login | GitHub 设备登录 | 公开审阅版 |
| gmail-imap-integration | Gmail IMAP 接入 | 公开审阅版 |
| meyo-api | meyo API | 公开审阅版 |
| multi-model-comparison | 多模型对比 | 公开审阅版 |
| musk-algorithm | 五步流程审查 | 公开审阅版 |
| one-sentence-craft | 一句话工序 | 暂缓 |
| openclaw-command-cron | 定时任务核查 | 公开审阅版 |
| openclaw-image-gen | 图片生成核验 | 公开审阅版 |
| openclaw-model-provider-setup | 模型接入 | 暂缓 |
| session-transcript-recovery | 会话原文恢复 | 公开审阅版 |
| webchat-file-delivery | WebChat 文件交付 | 公开审阅版 |
| webpage-visual-review | 网页视觉检查 | 公开审阅版 |

## 使用

按你的 Agent 文档，将需要的单个 `skills/<名称>` 文件夹放入它支持的 Skill 目录。保持引用目录随该 Skill 一起复制，重新发现后先确认名称和触发范围。无需一次安装全部。

OpenClaw 当前 CLI 支持本地目录安装。例如，下载并解压本仓库，在仓库目录中执行：

```shell
openclaw skills install ./skills/attribution-discipline --as attribution-discipline
```

该命令会把所选 Skill 安装进当前工作区；执行前先确认当前工作区和是否已有同名版本，保留已有改动。本仓库根目录是集合目录，不能当作单个 Skill 安装。

OpenClaw 安装位置和优先级以[当前 Skills 文档](https://docs.openclaw.ai/tools/skills)为准。其他 Agent 可能没有 OpenClaw 的会话、定时和媒体工具，不保证直接兼容。

这些是可阅读、可修改的工作流程，不会因加载而自动修改配置、重启服务、发消息或创建任务。需要实际操作时，沿用用户已授予该任务的权限。

## 审查与限制

按来源与许可、隐私、结构与引用、行为边界、验证与发布结论检查。完整结论见 [AUDIT.md](AUDIT.md)，改动范围见 [SOURCE.md](SOURCE.md)。结构校验不证明模型会稳定遵循，也不代表真实账户、远端发送或全部环境通过验收。

本轮未实际发送飞书消息、接入邮箱、创建定时任务、生成计费图片、重启网关或修改网络。

## 检查

Python 3.10+ 标准库，无需额外依赖。在仓库目录运行：

```shell
python -m unittest discover -s tests -v
```

测试使用合成凭据、网络替身和临时数据库，不调用真实账号。三个随包脚本分别用于 meyo JSON 请求、Gmail 候选配置检查和单会话快照导出；请先读对应 SKILL.md。

## 许可

本仓库的项目流程文本与辅助代码使用 [MIT](LICENSE)。OpenClaw、GitHub、Tailscale 等外部平台及其文档仍适用各自条款；这里不是它们的官方 Skill，也不声称底层方法或平台能力由本项目发明。
