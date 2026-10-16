# 18 项审查记录

审查日期：2026-10-16。第一轮公开10项；第二轮补查来源并修复4项，目前公开14项，另4项暂缓。检查次序：来源与许可 → 隐私 → 结构/引用 → 行为边界 → 受控验证与发布结论。

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

## 第二轮新增4项

- **gmail-imap-integration**：补查项目新建记录后，修复触发范围，增加只读候选配置检查器和负对照测试。限制独立reader、窄白名单、SecretRef、认证门槛与关闭投递，比较基线防止误改原渠道/Agent。未做真实邮箱接入验收。
- **meyo-api**：找回本项目封装与技能创建提案记录，补写缺失JSON客户端；固定官方HTTPS目的地，禁止重定向和自动写入重试，校验请求头并过滤已知凭据字段。官方接口正文改为外链，不复制官方Skill。未做真实账号调用验收。
- **musk-algorithm**：找到本项目技能创建提案和多轮用户打磨记录；方法署源Everyday Astronaut公开采访，公开的是我们的协作封装。移除固定删除配额、无条件强制审查与无限追加验证，区分评估和实施授权。
- **session-transcript-recovery**：补查项目新建记录后，将公开范围限定为授权历史和已有SQLite快照，移除块设备/删除取证分支，新增只读单会话导出器、范围限制、拒绝覆盖和合成数据库测试。未宣称完整恢复或兼容所有schema。

## 逐项说明

### attribution-discipline

正文夹有私人称呼与历史案例；公开副本已换成通用例子。

状态：只公开整理后的审阅副本，原运行文件未改。

### autonomous-evolution

补查早期安装记录，确认来自外部五支柱框架。后续迭代不改变来源，本轮不复制、不改成我们的原创发布。

状态：不包含其运行文件。

### cross-window-reconciliation

触发范围偏宽，且旧版依赖专用恢复技能；公开副本仅检查本任务获准访问的相关会话，不默认写记录或扩大恢复范围。第二轮发布的恢复技能也仅限明确授权的历史和已有快照。

状态：只公开整理后的审阅副本，原运行文件未改。

### feishu-media-send

已有使用、事故处理和迭代记录，但未补足原始创建/来源证据。按本轮来源门槛暂缓，既有脚本兼容与错误输出问题仍需后续处理。

状态：不包含其运行文件。

### feishu-turn-recovery

单独一句“在吗”不足以触发跨历史调查；公开副本要求已有漏答迹象，且只在已授权回复的会话内处理。

状态：只公开整理后的审阅副本，原运行文件未改。

### gateway-tailscale-access

修复入口涉及私网路由；公开副本默认只读核查，删除具体私人地址，保留路由归属和单独授权边界。官方端口与 foreground claim 文档已核对。

状态：只公开整理后的审阅副本，原运行文件未改。

### github-device-login

把 gh helper 当作唯一正确值，会误改已有 Git Credential Manager；公开副本改为验证现有 helper，保留其他账号配置。

状态：只公开整理后的审阅副本，原运行文件未改。

### gmail-imap-integration

补查项目新建记录后，修复触发范围，增加只读候选配置检查器和负对照测试。限制独立reader、窄白名单、SecretRef、认证门槛与关闭投递，比较基线防止误改原渠道/Agent。未做真实邮箱接入验收。

状态：只公开整理后的审阅副本，原运行文件未改。

### meyo-api

找回本项目封装与技能创建提案记录，补写缺失JSON客户端；固定官方HTTPS目的地，禁止重定向和自动写入重试，校验请求头并过滤已知凭据字段。官方接口正文改为外链，不复制官方Skill。未做真实账号调用验收。

状态：只公开整理后的审阅副本，原运行文件未改。

### multi-model-comparison

流程和引用完整；公开副本补充跨模型共享资料必须遵循本次授权，不把模型一致当事实验证。

状态：只公开整理后的审阅副本，原运行文件未改。

### musk-algorithm

找到本项目技能创建提案和多轮用户打磨记录；方法署源Everyday Astronaut公开采访，公开的是我们的协作封装。移除固定删除配额、无条件强制审查与无限追加验证，区分评估和实施授权。

状态：只公开整理后的审阅副本，原运行文件未改。

### one-sentence-craft

找到项目内更新记录，但现版新增校准段另有外部来源；来源与改写授权尚未闭合。保持整项暂缓，不靠删除署名或回退旧版包装成来源清楚。

状态：不包含其运行文件。

### openclaw-command-cron

主命令/别名描述与版本有关；固定运行耗时及删除必毁历史不宜泛化。公开副本改为按本机帮助和持久 run 证据判断，并明确运行会产生副作用。

状态：只公开整理后的审阅副本，原运行文件未改。

### openclaw-image-gen

命令与官方 infer 文档一致；公开副本注明版本检查和计费授权，保留文件解码与实际看图两层验证。

状态：只公开整理后的审阅副本，原运行文件未改。

### openclaw-model-provider-setup

只追到使用与后续迭代，未补足创建来源。继续暂缓；旧版延迟重启和费用/路由判定问题仍未作为可用流程发布。

状态：不包含其运行文件。

### session-transcript-recovery

补查项目新建记录后，将公开范围限定为授权历史和已有SQLite快照，移除块设备/删除取证分支，新增只读单会话导出器、范围限制、拒绝覆盖和合成数据库测试。未宣称完整恢复或兼容所有schema。

状态：只公开整理后的审阅副本，原运行文件未改。

### webchat-file-delivery

旧的单次私人收件案例不能推广为所有客户端能力；公开副本去掉私人案例，仅要求按本次客户端/附件验证送达。

状态：只公开整理后的审阅副本，原运行文件未改。

### webpage-visual-review

结构完整，无缺失引用；公开副本优先使用当前可用浏览器，保留截图、实际看图与字体证据边界，不把 CLI 作为强制环境。

状态：只公开整理后的审阅副本，原运行文件未改。

## 官方参考

- [OpenClaw IMAP](https://docs.openclaw.ai/automation/imap)
- [OpenClaw 定时任务 CLI](https://docs.openclaw.ai/cli/cron)
- [OpenClaw 推理 CLI](https://docs.openclaw.ai/cli/infer)
- [OpenClaw Tailscale 接入](https://docs.openclaw.ai/gateway/tailscale)
- [meyo 官方主文档](https://www.meyo.life/skill.md)
- [五步方法原始采访](https://everydayastronaut.com/starbase-tour-and-interview-with-elon-musk/)

验证结果和边界见 [VALIDATION.md](VALIDATION.md)。不把历史自评、模型自报或受控测试当作真实账号验收。
