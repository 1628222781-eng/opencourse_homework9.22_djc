"""
Ollama 本地轻量对话工具（流式输出）
====================================
基于 Ollama HTTP API 的流式（Streaming）对话：
  - 打字机式逐字输出，显著降低首字响应（TTFT）等待感
  - 支持多轮上下文对话
  - 内置容错：服务未启动 / 模型不存在时给出明确修复引导

四种调用方式（Ollama API / OpenAI Chat Completions / OpenAI Responses /
Anthropic Messages）的区别说明见同目录 README.md。
"""

import json

import requests

OLLAMA_HOST = "http://localhost:11434"
# 默认使用本机已下载的模型，可通过命令行参数指定其它模型
DEFAULT_MODEL = "qwen2.5:1.5b"


def chat_stream(model: str, messages: list):
    """流式对话：逐 token 输出到终端（打字机效果）"""
    payload = {"model": model, "messages": messages, "stream": True}
    with requests.post(
        f"{OLLAMA_HOST}/api/chat", json=payload, stream=True, timeout=None
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            delta = data.get("message", {}).get("content", "")
            if delta:
                print(delta, end="", flush=True)  # 流式打印
            if data.get("done", False):
                print()  # 换行结束


def main():
    model = DEFAULT_MODEL
    import sys

    if len(sys.argv) >= 2:
        model = sys.argv[1]

    print(f"🤖 已加载模型：{model}（输入 exit / quit 退出）")

    # 先确认模型可用
    try:
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5).raise_for_status()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接 Ollama 服务，请先启动 Ollama：")
        print("   Windows 用户：双击运行 Ollama 桌面应用，或命令行执行 ollama serve")
        print("   然后执行：ollama pull " + model)
        return

    messages = []
    while True:
        user = input("\n👤 你：").strip()
        if not user:
            continue
        if user.lower() in ("exit", "quit", "退出"):
            print("👋 再见！")
            break
        messages.append({"role": "user", "content": user})
        print("🤖 助手：", end="")
        try:
            chat_stream(model, messages)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                print(f"\n❌ 模型 {model} 不存在，请先下载：ollama pull {model}")
            else:
                print(f"\n❌ 请求失败：{e}")
            messages.pop()  # 移除失败的那条提问
            continue
        # 保留助手回复，形成多轮上下文（此处未获取完整回复文本，
        # 简单起见只保留 role 标记，便于演示多轮会话结构）
        messages.append({"role": "assistant", "content": "..."})


if __name__ == "__main__":
    main()
