# DocAdvisor 🚀

> 基于 ReAct + RAG 的智能文档顾问系统，让 AI 帮你检索文档并生成专业方案

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 特性

- 🤖 **ReAct 循环推理** - Agent 自动检索文档并生成方案
- 📚 **知识库检索** - 基于本地文档库生成专业建议
- 🎨 **双界面支持** - 命令行和图形界面两种使用方式
- 🔄 **多轮对话** - 支持连续对话，保持上下文记忆
- ⚙️ **多模型支持** - 支持智谱AI、OpenAI、Claude、通义千问、Gemini

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/Ing-la/DocAdvisor.git
cd DocAdvisor
pip install -r requirements.txt
```

### 配置

1. **复制配置文件**：
   ```bash
   cp .env.example .env
   ```

2. **配置 API Key**（两种方式任选其一）：
   
   **方式一：GUI 界面配置（推荐）**
   - 运行 `python scripts/tkinter_app.py`
   - 如果未配置，会自动弹出提示
   - 点击"⚙️ 模型配置"按钮，输入你的 API Key 和选择模型
   
   **方式二：手动编辑**
   - 编辑 `.env` 文件，填入你的 API Key：
     ```env
     API_KEY=your_api_key_here
     MODEL=glm-4-flash
     PROVIDER=zhipu
     ```

### 运行

**GUI 版本（推荐）**：
```bash
python scripts/tkinter_app.py
```

**命令行版本**：
```bash
python scripts/main.py
```

## 💡 使用示例

输入你的需求，Agent 会自动检索相关文档并生成专业方案：

```
设计一款ESG可持续投资基金的销售策略
```

Agent 会：
1. 分析你的需求
2. 检索相关文档
3. 生成结构化方案

## 🏗️ 技术架构

- **ReAct 框架** - Reasoning + Acting 循环推理
- **RAG 检索** - 基于关键词的文档检索
- **多模型支持** - 支持 5+ 大模型服务提供商
- **YAML 配置** - 流程配置驱动，易于扩展

## 📖 详细文档

查看 [docs/README.md](docs/README.md) 了解完整文档和使用说明。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**
