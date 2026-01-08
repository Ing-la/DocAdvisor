# src/ - 源代码目录

项目核心源代码模块。

## 目录结构

- `engine/` - 核心引擎模块（配置加载、状态管理、节点处理）
- `tools/` - 工具模块（案例检索等工具函数）
- `utils/` - 工具函数（通用工具函数）

## 模块说明

### engine/ - 核心引擎

实现 ReAct Agent 的核心逻辑：
- **config_loader.py**: 加载和解析 YAML 配置文件，支持模板渲染
- **state_manager.py**: 管理对话状态（变量、历史记录）
- **node_processor.py**: 处理节点执行逻辑，调用 LLM API

### tools/ - 工具模块

实现 Agent 可调用的工具函数：
- **search_cases.py**: 在文档库中搜索相关文档（关键词匹配）

### utils/ - 工具函数

通用工具函数（预留扩展）。

