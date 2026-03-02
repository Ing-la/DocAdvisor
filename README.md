# DocAdvisor 🚀

> 基于 ReAct + RAG 的 **Web 文档顾问系统**（FastAPI + Next.js）

## ✨ 当前版本定位

本项目已完成从本地 GUI/CLI 到 Web 架构迁移，当前仅保留：

- Python 推理引擎（`src/engine`）
- FastAPI API 层（`src/api`）
- Next.js 前端（`frontend/`）

## 🧱 架构

- **Backend API**: FastAPI (`src/api/server.py`)
- **Engine**: ReAct + RAG (`src/engine`, `src/tools`)
- **Frontend**: Next.js 14 + Tailwind + shadcn/ui 风格组件 (`frontend/`)
- **Streaming**: SSE `POST /api/v1/chat/stream`

## 🚀 快速开始

### 1) 启动后端

```bash
pip install -r requirements.txt
python scripts/api_server.py
```

默认地址：`http://localhost:8000`

### 2) 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

默认地址：`http://localhost:3000`

## 🔌 API 概览

- `GET /api/v1/health`
- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`
- `GET /api/v1/config`
- `PUT /api/v1/config`
- `GET /api/v1/retrieval/latest?session_id=...`
- `POST /api/v1/chat`
- `POST /api/v1/chat/stream` (SSE)

## 📄 许可证

MIT
