---
name: github-device-login
description: "GitHub gh 登录、重认证或 git 推拉缺凭证时用：PTY 驱动设备授权并核验账号和 credential helper。"
---

# GitHub 设备流认证

1. **查现状**：运行 `gh auth status`，核对目标 GitHub hostname/账号；推拉缺凭证时再查 `git config --global --get-regexp credential`。git 提交身份用 `git config user.name`、`git config user.email` 查看有效值，按任务需要处理。完成标准：认证故障、credential helper 和提交身份问题已区分。
2. **发起设备流**：需要登录时，在 PTY 运行 `gh auth login --hostname github.com --git-protocol https --web`，按实际提示选择 Git 凭证集成；出现 code 和 Press Enter 提示后按 Enter 进入等待。完成标准：进程显示本次 one-time code 和授权 URL，处于等待批准状态。
3. **交付授权码**：将本次 code 与进程给出的设备登录 URL 交给用户的私密会话；按进程实际过期提示重新发起。完成标准：已提交正确代码且用户可完成授权；在批准前保持「等待授权」。
4. **核验登录**：批准后检查进程退出结果，运行 `gh auth status`、`gh api user` 确认目标账号；需要 HTTPS Git 集成时核对当前有效 credential helper 能为目标仓库提供凭证；Git Credential Manager 等已有配置同样有效，不为使用 gh 而覆盖它或其他账号配置。仅在需要提交且身份缺失时使用用户确认的姓名/邮箱，优先仓库范围配置。完成标准：账号 API 调用成功、所需 helper 已生效；任何提交身份变更均读回一致。
