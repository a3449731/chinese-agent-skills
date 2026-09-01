---
name: agent-browser
description: 浏览器自动化操作指南（Qoder/Cursor 版）——导航网页、填写表单、点击按钮、截图、提取数据、测试 Web 应用，或自动化任何浏览器任务。触发词包括"打开网站"、"填写表单"、"点击按钮"、"截图"、"从页面抓取数据"、"测试这个 Web 应用"、"登录网站"、"自动化浏览器操作"。主路径：Qoder 的 Browser 子代理（Agent 工具）与 Cursor 浏览器预览；可选高级路径：agent-browser CLI（面向 Electron 桌面应用、Slack 自动化等专项场景）。
---

# 浏览器自动化（Qoder/Cursor 版）

面向 AI 助手的浏览器自动化操作指南。根据任务和环境选择执行路径：日常网页交互优先用 Qoder 的 **Browser 子代理**；在 Cursor 里用其**浏览器预览**能力；特殊场景（Electron 桌面应用、Slack、云端浏览器）再用 **agent-browser CLI**。

## 主路径（推荐）：Qoder Browser 子代理

通过 **Agent 工具**派发一个 Browser 子代理来执行浏览器任务。这是 Qoder 内置的浏览器自动化能力，无需安装任何东西。

**任务描述怎么写：**
- 明确目标：要访问的 URL、要完成的操作（导航、点击、输入、滚动、截图）
- 定义成功条件：什么结果算完成（例如"表单提交后出现成功提示"）
- 需要视觉验证时，要求子代理截图并返回截图路径
- 需要参考界面时，把截图路径传给子代理作为输入

**适用场景：**
- 导航页面、填写表单、点击按钮、滚动浏览
- 截图、提取页面数据
- Web 应用的功能测试与探索性测试
- QA、bug 狩猎、评审应用质量

**注意事项：**
- 任务描述要具体；模糊的描述会让子代理走弯路
- 涉及登录/敏感操作时，明确告知子代理如何处理凭据

## 备选路径：Cursor 浏览器预览

Cursor 提供内置的浏览器预览能力（浏览器预览面板 / 移动预览），适合在开发过程中预览和交互 Web 应用：

- 在编辑器内打开预览面板，实时查看页面
- 直接与页面交互（点击、输入）验证功能
- 配合 DevTools 检查网络请求与元素
- 适合边开发边验证的前端工作流

如果交互需求超出预览面板的能力（复杂多步操作、需要程序化验证），改用 Qoder 的 Browser 子代理。

## 可选高级路径：agent-browser CLI

原版 agent-browser 是一个面向 AI agent 的快速浏览器自动化 CLI：通过 CDP 驱动 Chrome/Chromium，带无障碍树快照和紧凑的 `@eN` 元素引用。Qoder/Cursor 内置能力覆盖日常需求时无需安装；以下场景再考虑它。

**安装：** `npm i -g agent-browser && agent-browser install`

**能力：**
- 快速的原生 Rust CLI，不是 Node.js 包装器
- 通过 CDP 驱动 Chrome/Chromium，不依赖 Playwright 或 Puppeteer
- 带元素引用的无障碍树快照，交互可靠
- 会话、认证保管库、状态持久化、视频录制

**专项场景（加载对应工作流内容）：**
```bash
agent-browser skills get core            # 从这里开始——工作流、常见模式、故障排查
agent-browser skills get electron        # Electron 桌面应用（VS Code、Slack、Discord、Figma、……）
agent-browser skills get slack           # Slack 工作区自动化（未读、消息、会话搜索）
agent-browser skills get dogfood         # 探索性测试 / QA / bug 狩猎
agent-browser skills get vercel-sandbox  # Vercel Sandbox microVM 中的 agent-browser
agent-browser skills get agentcore       # AWS Bedrock AgentCore 云浏览器
```
运行 `agent-browser skills list` 查看已安装版本上可用的全部内容。

**可观测性仪表盘：** 仪表盘独立于浏览器会话运行在 4848 端口，也可以通过代理或转发 URL（如 `https://dashboard.agent-browser.localhost`）打开。AI 助手应停留在仪表盘源上：会话标签、状态和流式流量在内部代理，无需暴露会话端口。

## 决策：用哪条路径

| 场景 | 路径 |
|---|---|
| 日常网页导航 / 填表 / 点击 / 截图 / 取数 | Qoder Browser 子代理（推荐） |
| 开发中预览和交互自己的 Web 应用 | Cursor 浏览器预览 |
| Electron 桌面应用、Slack、云浏览器等专项 | agent-browser CLI |
| 需要视频录制、认证保管库、长会话状态 | agent-browser CLI |
