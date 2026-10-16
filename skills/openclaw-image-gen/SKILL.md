---
name: openclaw-image-gen
description: "通过 OpenClaw provider 生成图片素材或生成后无输出时用：选择可用模型、生成文件并强制读回和视觉核验。"
---

# OpenClaw 图片生成

先核对当前 CLI 帮助和 provider 能力。只有用户已授权本次生成及相应额度/费用时才提交，不为验证安装而自动发起计费生成。

1. **选择 provider/model**：运行 `openclaw infer image providers --json`，检查 configured 与生成能力；从当前结果选择模型。`capability` 是 `infer` 的别名，参阅本机 docs `cli/infer.md`。完成标准：所选 provider/model 有配置依据，尺寸/质量参数受支持。
2. **执行一次生成**：选一个本次独有的输出路径，运行 `openclaw infer image generate --model <provider/model> --output <绝对路径> --prompt "<text>" --json`；按模型能力追加 `--size`/`--quality`。完成标准：进程结束且已保留退出状态和 JSON 的 ok、provider、model、attempts、输出路径；静默结束仅记「结果待核验」。
3. **强制读回产物**：检查 JSON 报告的实际路径（扩展名可能按返回 MIME 改变），确认文件属于本次调用、非空且可解码为图片。旧文件会在写入失败后保留，因此旧路径存在不算成功；不设 PNG 必须数百 KB 的阈值。完成标准：退出/结果状态与新产物一致且解码成功；缺文件、旧文件或冲突状态均记失败/未确认，先据诊断修复再决定是否重试。
4. **视觉检查与交付**：用当前可用图像查看工具打开步骤 3 的文件，检查主题、文字、水印与伪影；只有通过后才接入项目或发送。完成标准：已实际看图并交付相同文件；生成成功与接收端送达分别说明。批量前确认数量和所用鉴权/计费路线，依据当前 provider 信息说明成本，沿用步骤 2–4 核验每张图。
