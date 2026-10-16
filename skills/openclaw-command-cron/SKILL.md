---
name: openclaw-command-cron
description: "创建或修改定时命令、设置提醒投递、排查运行结果时用：配置 OpenClaw automation 并分别核验执行与送达。"
---

# OpenClaw 命令与提醒定时任务

创建、修改和手动运行均须已获相应任务授权；运行会实际执行命令或模型任务。先读配置再操作，示例不是让 agent 自动创建测试任务的授权。

1. **确认任务与所有者**：区分确定性 command 和 agentTurn 提醒，确认时区、计划、实际脚本、agent 与投递目标；修改前用 `openclaw automations list --json`、`get <job-id>` 读取完整对象。先核对本机 `openclaw automations --help` 和 `cli/cron.md`；`automations` 与 `cron` 的别名表述随版本而异。完成标准：已有明确 payload、owner、计划和投递要求，更新使用真实 id。
2. **创建或修改**：命令类使用 `openclaw automations create "<cron表达式>" --name "<名称>" --command-argv '["/abs/path.sh"]' --command-cwd <dir> --timeout-seconds <预算> --tz <时区> --no-deliver`。需要提醒时按 `cli/cron.md` 的 agentTurn 示例配置 agent、message、session 和明确 announce 路由；保留现有任务无关字段。完成标准：读回 payload、owner、时区与 nextRunAtMs 均符合要求。
3. **验证投递策略**：孤立任务默认 announce；`channel:last` 未解析到目标时可 fail-closed，检查 `automations show <job-id>` 的 route preview。内部任务使用 `edit <job-id> --no-deliver`；提醒保留 announce 并填写已确认 channel/to。`--best-effort-deliver` 仅用于允许投递失败的任务，不用来掩盖必达提醒。完成标准：`get` 的 delivery 与意图一致，`show` 路由可解析或明确为内部任务。
4. **运行并分开验收**：在授权范围内用 `openclaw automations run <job-id> --wait --wait-timeout 10m` 触发一次，随后 `runs <job-id> --json` 核对执行结果、命令退出状态、摘要和实际产物。执行 status=ok 仍可能 completionStatus=failed；逐项检查 delivery diagnostics。完成标准：执行成功且实际副作用符合任务；必达提醒还有目标端送达证据，内部任务没有意外通知。agentTurn 运行含引导与投递，耗时受任务和环境影响；running ≠ failed，完成与否以 `runs <job-id>` 记录为准，确认完成前不删改 job。
5. **处理分支故障**：查 [排查步骤](references/troubleshooting.md) 中对应的备份、动作监控、owner 或静默分支。完成标准：修复后重跑步骤 4，或报告具体未解决原因及证据。
