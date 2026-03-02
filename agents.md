# DocAdvisor Agent 指令规范

## 1. 项目背景与目标
- **当前状态**：本项目是一个基于 Python 的 ReAct + RAG 架构的文档助手，目前使用 Tkinter 作为 GUI。
- **目标任务**：将前端迁移至 Next.js (App Router) 技术栈，打造具有"现代审美"和"丝滑交互"的 Web 界面。
- **核心逻辑**：保持 `src/engine` 中的核心推理逻辑不变，前端通过 API（建议使用 FastAPI 包装）与后端通信。

## 2. 技术栈约束 (Tech Stack)
- **Framework**: Next.js 14+ (App Router).
- **Language**: TypeScript (必须启用严格模式).
- **Styling**: Tailwind CSS (遵循响应式设计).
- **Components**: 优先使用 shadcn/ui 组件库，保持设计语言一致性。
- **Icons**: 使用 Lucide React 图标库。
- **State Management**: 使用 React Context 或 Zustand 处理轻量状态。

## 3. 开发准则 (Coding Standards)
- **视觉风格**：追求极简主义、深色模式友好、大量的留白与平滑的过渡动画（可使用 Framer Motion）。
- **组件化**：将聊天窗口、推理过程展示（Thought Trace）、检索结果预览拆分为独立组件。
- **交互规范**：
  - 推理过程需要支持"流式展示"（Streaming）。
  - 检索到的文档片段需支持点击高亮或侧边栏预览。
  - 模型配置界面需采用模态框（Dialog）形式。

## 4. 任务执行与 Definition of Done (DoD)
- **环境搭建**：Agent 在修改代码前，需先在云端执行 `pnpm install` 验证依赖环境。
- **前后端解耦**：所有对 Python 逻辑的调用必须通过定义的 API 接口，严禁直接在前端代码中注入 Python 执行脚本。
- **提交规范**：完成功能后，请先运行 `pnpm build` 确保没有类型错误，然后提交 Pull Request。
- **README 更新**：修改完成后，自动更新根目录 README 中的"快速开始"部分，加入 Web 端启动指令。

## 5. 禁止行为
- 禁止使用 `pages/` 路由模式。
- 禁止引入未经说明的第三方 UI 库。
- 禁止删除原有的 `scripts/tkinter_app.py`，需保持向后兼容。
