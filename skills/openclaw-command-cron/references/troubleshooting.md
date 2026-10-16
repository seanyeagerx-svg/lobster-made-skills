# 按症状排查

本机权威参考：OpenClaw docs `cli/cron.md`、`automation/cron-jobs/delivery.md`。

1. **意外通知**：读回 delivery、run diagnostics 和脚本自身的发送调用。`none` 关闭 runner fallback，不代表阻止脚本直发或 agent message 工具；command stdout 走配置的 announce/webhook/none，并非必然绕过 none 经 heartbeat 外发。完成标准：通知来源与目标已定位，修复后一次运行没有意外发送。
2. **备份不完整**：检查是否有嵌套 Git 仓库、gitlink 或无首个 commit 的内嵌仓；核对备份范围，按范围修复打包/忽略规则并核验远端文件与恢复结果。完成标准：要求的文件实际可恢复，未把 push 成功或 job skipped 当备份成功。
3. **owner 未解析**：用完整 CLI 列表与真实 id 核对 job 的 agent；明确应归属谁后用 `automations edit <job-id> --agent <id>` 修复。只有系统默认 owner 确需改变时才处理 `agents.defaults.systemAgent.agentId`。完成标准：effectiveAgentId 正确且运行不再因 owner 跳过。
4. **动作监控循环触发**：核对上次动作、冷却期和计数状态；成功动作后重置触发计数并进入适合业务的冷却期。完成标准：连续触发测试不重复执行同一动作，恢复条件仍能正常触发。
5. **消息/计划修改**：先 get 全文再更新完整 message，保留所需约束；按当前 CLI 文档选择 flags/位置参数。完成标准：读回 message 和下一次运行时间与意图相同。
6. **running 误判与删后无记录**：agentTurn 运行含引导和投递，耗时没有统一正常阈值——running 状态先查 `automations runs <job-id>` 的 completionStatus 与投递记录，确认完成后再动 job；不同版本的历史保留行为须查当前文档，删除前保存需要的执行与投递证据。从未查记录就断言「未投递/没发出来」= 无实证断言，禁止。完成标准：下结论前有 runs 记录或接收方证据支撑；删除发生在记录核实之后。
