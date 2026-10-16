# 18 项审查记录

审查日期：2026-10-16。范围是本项目技能工坊中留存完整备份的 18 项历史集合及其后续同名版本。检查源码与本地引用，并抽核当前官方文档；没有把其他安装的插件技能或视频制作 SOP 混入本集合。

| Skill | 用途 | 发布结论 |
|---|---|---|
| attribution-discipline | 归因纪律 | 公开审阅版 |
| autonomous-evolution | 经验复盘 | 暂缓 |
| cross-window-reconciliation | 跨窗口对账 | 公开审阅版 |
| feishu-media-send | 飞书媒体发送 | 暂缓 |
| feishu-turn-recovery | 飞书漏答恢复 | 公开审阅版 |
| gateway-tailscale-access | 网关接入核查 | 公开审阅版 |
| github-device-login | GitHub 设备登录 | 公开审阅版 |
| gmail-imap-integration | Gmail IMAP 接入 | 暂缓 |
| meyo-api | meyo API | 暂缓 |
| multi-model-comparison | 多模型对比 | 公开审阅版 |
| musk-algorithm | 五步流程审查 | 暂缓 |
| one-sentence-craft | 一句话工序 | 暂缓 |
| openclaw-command-cron | 定时任务核查 | 公开审阅版 |
| openclaw-image-gen | 图片生成核验 | 公开审阅版 |
| openclaw-model-provider-setup | 模型接入 | 暂缓 |
| session-transcript-recovery | 会话原文恢复 | 暂缓 |
| webchat-file-delivery | WebChat 文件交付 | 公开审阅版 |
| webpage-visual-review | 网页视觉检查 | 公开审阅版 |

## 逐项说明

### attribution-discipline

正文夹有私人称呼与历史案例；公开副本已换成通用例子。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### autonomous-evolution

依赖集合外的 fake-success-guard；检查器按固定记忆布局和关键词评分，不能证明能力进化。先补依赖和独立验证。

状态：本仓库不包含其运行文件。

### cross-window-reconciliation

触发范围偏宽，且依赖本轮暂缓的恢复技能；公开副本仅检查本任务获准访问的相关会话，不默认写记录或扩大恢复范围。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### feishu-media-send

图片/视频脚本直接依赖字符串 appId/appSecret 配置；视频脚本会原样打印部分 HTTP 错误体，未覆盖 SecretRef、多账号及未知结果重试的受控测试。暂缓脚本分发。

状态：本仓库不包含其运行文件。

### feishu-turn-recovery

单独一句“在吗”不足以触发跨历史调查；公开副本要求已有漏答迹象，且只在已授权回复的会话内处理。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### gateway-tailscale-access

修复入口涉及私网路由；公开副本默认只读核查，删除具体私人地址，保留路由归属和单独授权边界。官方端口与 foreground claim 文档已核对。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### github-device-login

把 gh helper 当作唯一正确值，会误改已有 Git Credential Manager；公开副本改为验证现有 helper，保留其他账号配置。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### gmail-imap-integration

当前写法依赖特定 OpenClaw IMAP 插件、隔离 reader 和凭证存储机制；字段与当前官方文档大体一致，但这份流程未完成可复现的隔离/拒收/路由回归验证，暂不作为通用接入包发布。

状态：本仓库不包含其运行文件。

### meyo-api

正文调用 scripts/meyo_api.py，但目录没有该脚本；端点摘录还需核对官方文档复用范围。当前不具备可复现安装条件。

状态：本仓库不包含其运行文件。

### multi-model-comparison

流程和引用完整；公开副本补充跨模型共享资料必须遵循本次授权，不把模型一致当事实验证。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### musk-algorithm

五步方法属于外部方法；现有封装未提供可核查的方法来源和改写范围，不按我们原创的方法或独立原创 Skill 发布。

状态：本仓库不包含其运行文件。

### one-sentence-craft

现版绑定私人偏好文件；索引注明新增“锋利校准”来自外部 Agent，正文未同步来源。先完成来源、授权/改写范围和事实表述核对，不能仅退回旧版掩盖问题。

状态：本仓库不包含其运行文件。

### openclaw-command-cron

主命令/别名描述与版本有关；固定运行耗时及删除必毁历史不宜泛化。公开副本改为按本机帮助和持久 run 证据判断，并明确运行会产生副作用。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### openclaw-image-gen

命令与官方 infer 文档一致；公开副本注明版本检查和计费授权，保留文件解码与实际看图两层验证。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### openclaw-model-provider-setup

含 nohup+sleep 延迟重启示例；不能保证脱离网关控制组，也不适宜作为通用自恢复流程。cost=0 不能独立证明订阅路线，模型自报身份同样不是路由证据。

状态：本仓库不包含其运行文件。

### session-transcript-recovery

包含块设备明文取证分支，可能读取大量无关数据；需要将正常历史恢复与底层取证拆分，并补最小读取范围与实际 schema 验证。

状态：本仓库不包含其运行文件。

### webchat-file-delivery

旧的单次私人收件案例不能推广为所有客户端能力；公开副本去掉私人案例，仅要求按本次客户端/附件验证送达。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

### webpage-visual-review

结构完整，无缺失引用；公开副本优先使用当前可用浏览器，保留截图、实际看图与字体证据边界，不把 CLI 作为强制环境。

状态：仅公开经过整理的审阅副本，未修改原运行版本。

## 官方参考

- [OpenClaw 定时任务 CLI](https://docs.openclaw.ai/cli/cron)
- [OpenClaw 推理 CLI](https://docs.openclaw.ai/cli/infer)
- [OpenClaw Tailscale 接入](https://docs.openclaw.ai/gateway/tailscale)
- [Tailscale Funnel 范围](https://tailscale.com/docs/features/tailscale-funnel)
- [OpenClaw IMAP](https://docs.openclaw.ai/automation/imap)

校验结果见 [VALIDATION.md](VALIDATION.md)。文档与 CLI 可能变化，使用前应核对当前安装版本。
