# Ollama 本地模型管理与轻量对话工具

## 1. 项目简介

本项目是一个基于 **Python + Ollama API** 开发的本地大语言模型（LLM）管理与交互工具。
项目旨在降低本地大模型的使用门槛，提供**模型下载管理**与**流式实时对话**两大核心功能，
帮助开发者快速在本地部署、测试与集成各种开源大模型（如 Qwen、Llama 等），全程离线运行、无需联网调用云端 API。

本机实际运行环境：

- Ollama 0.34.2（Windows 11 本机服务，默认端口 11434）
- 已下载模型：`qwen2.5:3b`（1.9 GB）、`qwen2.5:1.5b`（986 MB）、`qwen2.5:0.5b`（397 MB）
- Python 3.14（本项目仅依赖 `requests` 标准第三方库）

## 2. 核心功能

- **模型下载管理（Download Manager）**：基于 Ollama HTTP API 实现模型的动态下载与更新，
  实时展示已下载体积与百分比进度条（`download.py`）。
- **低延迟流式对话（Stream Chat）**：采用打字机式的流式文本输出（Streaming Output），
  逐 token 打印，显著降低用户等待首字响应（TTFT）的时延体验，支持多轮上下文（`chat.py`）。
- **友好容错机制**：内置完善的异常捕获，针对 Ollama 服务未启动、模型不存在等常见报错提供明确的修复引导。

## 3. 快速开始

```bash
# 1. 安装并启动 Ollama（https://ollama.com/download）
ollama serve

# 2. 下载模型（本仓库也提供带进度条的下载工具）
ollama pull qwen2.5:1.5b
python download.py pull qwen2.5:1.5b   # 或使用本仓库脚本（实时进度条）
python download.py list                # 查看本地模型列表

# 3. 启动流式对话
python chat.py                        # 默认模型 qwen2.5:1.5b
python chat.py qwen2.5:3b             # 指定模型
```

运行效果：命令行输入问题后，模型以打字机效果逐字输出回答；输入 `exit` / `quit` 退出。

## 4. 不同方式调用本地模型的区别

| 调用方式 | 请求路径 | 协议/格式 | 适用场景 | 与原生 API 的区别 |
|---|---|---|---|---|
| **Ollama API（原生）** | `POST /api/chat`、`/api/generate` | Ollama 自有 JSON 格式 | 本地原生调用、最底层能力 | 基础方式，支持 `stream`、`keep_alive`、`format=json` 等原生参数 |
| **OpenAI Chat Completions** | `POST /v1/chat/completions` | OpenAI 标准格式（`messages`/`model`/`stream`） | 迁移 OpenAI 生态的既有代码 | Ollama 提供兼容层，字段与 OpenAI 一致，可无缝替换 `base_url` |
| **OpenAI Responses** | `POST /v1/responses` | OpenAI 新一代 Responses API | 使用较新的 OpenAI SDK 版本 | 支持 `tools`、结构化输出等新特性，兼容层同样可用 |
| **Anthropic Messages** | `POST /v1/messages` | Anthropic 标准格式（`system`/`messages`） | 迁移 Claude 生态代码 | Ollama 兼容 Anthropic 消息格式，字段如 `max_tokens` 需按 Anthropic 规范传参 |

**一句话总结**：Ollama 原生 API 是最底层、最完整的能力入口；
OpenAI Chat Completions / Responses / Anthropic Messages 三种都是**协议兼容层**，
让使用不同云厂商 SDK 的代码不用改逻辑，只需把 `base_url` 指向本地 `http://localhost:11434/v1` 即可在本地跑通。

## 5. 还可以给模型什么外挂？

在本地模型之外挂接能力，可以显著扩展模型的边界（课程作业点）：

| 外挂能力 | 说明 | 典型工具 |
|---|---|---|
| **RAG 知识库** | 把 PDF/文档切片 → Embedding 向量化 → 检索增强回答，让模型"读过"你的资料 | ChromaDB + sentence-transformers |
| **Function Calling / Tools** | 让模型按需调用本地函数（查天气、执行命令、查数据库） | OpenAI 兼容 `/v1/chat/completions` 的 `tools` 参数 |
| **Embedding 向量模型** | 单独下载 embedding 模型做文本向量化，支撑检索/聚类 | `paraphrase-multilingual-MiniLM-L12-v2` |
| **多模态（Vision）** | 外挂视觉模型，让文本模型看懂图片/截图 | `qwen2.5-vl`、`llava` |
| **记忆 / 长期上下文** | 用向量库持久化历史对话，实现跨会话记忆 | ChromaDB 持久化存储 |
| **语音（STT/TTS）** | 接入语音转文字 + 文字转语音，做成语音助手 | Whisper、Edge-TTS |

## 6. 课程实践记录

本次课程还完成了另一条实践链路（与本仓库互补）：

- 克隆课程仓库：`git clone https://gitcode.com/nicezack/ai-opensource-practice-course.git`
- 通过 **ModelScope** 下载 **Qwen3-0.6B** 模型（1.4 GB）与 embedding 模型（471 MB），
  使用 `snapshot_download` + `allow_patterns` 精确拉取必需文件
- 使用 `transformers` 在纯 CPU 环境完成本地推理验证
- 使用 **Streamlit** 部署本地 Web 聊天界面（`http://localhost:8501`）

两套方案对比：**Ollama** 开箱即用、一行命令下载运行；**ModelScope + transformers** 更适合需要
精细控制加载参数与自定义推理逻辑的场景。

## 7. 项目结构

```
opencourse_homework9.22
├── README.md      # 项目说明（本文档）
├── download.py    # 模型下载管理（实时进度）
└── chat.py        # 流式对话工具（打字机效果）
```
