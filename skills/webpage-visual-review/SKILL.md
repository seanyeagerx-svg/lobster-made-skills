---
name: webpage-visual-review
description: "网页截图自查、UI 视觉验收或字体疑似未生效时用：获取可见渲染证据，核对字体与截图局限。"
---

# 网页渲染截图自查

1. **确认页面与环境**：确定 URL、viewport 和待检查区域，核对可用 Chromium/浏览器工具及图像读取路径权限。完成标准：页面在目标环境可访问且截图输出目录可写、可由图像工具读取。
2. **截图并读回**：优先用当前环境提供的浏览器与截图工具；本机仅在允许 CLI 浏览器且已安装 `chromium-browser` 时可运行 `chromium-browser --headless=new --disable-gpu --disable-dev-shm-usage --screenshot=<绝对路径> --window-size=1440,900 --virtual-time-budget=8000 --hide-scrollbars <URL>`；按实际 sandbox 环境处理启动问题。完成标准：本次截图非空、可解码且对应目标页面。
3. **核对动态内容**：对后续屏空白、reveal、IntersectionObserver 或懒加载，滚动目标区域并等待渲染后重新截图，与实际浏览器对照；优先分屏，图像工具超限时用已安装的 `convert <in> -resize 1100x -quality 82 <out>.jpg` 提供缩略图，同时保留原图细节。完成标准：已区分真实缺陷与未触发渲染，证据不足者标为未确认。
4. **检查字体分支**：有字体要求或观感异常时，运行 `fc-list :lang=zh family`、`fc-match "<CSS字体名>"` 检查系统字体；结合页面实际加载的 webfont 与 computed style。需要 A/B 时保持文字、布局、viewport、裁剪区域一致，只改字体；像素差只证明渲染有差别，不以固定 RMSE 阈值证明命中特定字体。完成标准：有字体加载/实际渲染证据，或明确缺字体和待修项；安装/别名变更限定在授权环境。
5. **看图并报告**：用当前图像查看工具打开截图，按区域指出布局、对比、文本和字体问题；将截图事实与用户的审美选择分开。完成标准：报告引用本次截图，提出的问题有可见证据，待用户判断和未覆盖设备均明确。
