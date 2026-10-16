---
name: gateway-tailscale-access
description: "浏览器接入 WebChat/Control UI、核查改端口建议、或 ts.net 不通时用：检查托管路由并交付带验证状态的 URL。"
---

# Gateway 浏览器接入核查

默认只读核查。不得因加载本技能就修改 VPN、出口节点、系统代理、DNS 或路由；涉及终止进程、重启或更改接入方式时，必须已有针对该动作的明确授权。不得把私网接入问题自动改为公网 Funnel。

1. **确认接入模式**：读取当前环境获准访问的配置，核对 `gateway.tailscale.mode`、`gateway.bind` 与 Control UI basePath；查本机 OpenClaw docs 的 `gateway/tailscale.md` 和 `gateway/stable-https-url.md`。完成标准：已区分托管 serve/funnel、外部代理和直接 tailnet 绑定。
2. **核对端口与路由**：运行 `tailscale serve status --json`，检查 `Foreground` 中 hostname、path、目标监听器。文档中的 OpenClaw 托管 Serve 使用 HTTPS **443**，转发到专用临时 loopback 端口；普通 Gateway 本地端口默认 18789。文档列出的 443/8443/10000 是 **Funnel 的 TLS 端口限制**，不是把托管 Serve 改为 8443 的配置依据。完成标准：记录实际 claim 与配置的对应关系，改端口建议有当前文档和路由证据支持。
3. **定位缺失或冲突**：将 JSON 路由与本次 Gateway 启动日志对照。若为孤立 foreground claim，按 `gateway/tailscale.md` 的 “Recover an orphaned foreground claim” 核对进程归属；仅在确认属于待恢复 Gateway 且获授权后终止该进程，验证 claim 消失再重启。背景 root handler 与 foreground claim 的清理方式不同；保留其他应用拥有的路由。完成标准：claim 正常，或具体缺证/冲突及其所有者已明确。
4. **端到端验证**：从目标 tailnet 设备访问状态输出中的 HTTPS URL（含实际 basePath），确认 Control UI 加载及 WebSocket 登录；本机探测只作定位证据。Serve 身份认证需专用监听器、有效 Tailscale 头及 `allowTailscale`，Funnel 需 password。完成标准：交付实际 URL 和目标端验证结果；缺目标端证据时标记「可访问性未验证」。
