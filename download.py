"""
Ollama 本地模型下载与管理工具
================================
基于 Ollama HTTP API 实现：
  1. 查看本地已下载的模型列表
  2. 拉取（下载）新模型，实时展示下载进度与百分比

环境要求：本机已安装并启动 Ollama（默认服务地址 http://localhost:11434）
"""

import json
import sys

import requests

OLLAMA_HOST = "http://localhost:11434"


def list_models():
    """列出本地已下载的模型"""
    resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    resp.raise_for_status()
    models = resp.json().get("models", [])
    if not models:
        print("（暂无本地模型，请先执行 pull 下载）")
        return
    print(f"{'模型名':<22}{'大小':<10}{'修改日期'}")
    print("-" * 50)
    for m in models:
        size_gb = m["size"] / 1024**3
        modified = m.get("modified_at", "")[:10]
        print(f"{m['name']:<22}{size_gb:.2f} GB   {modified}")


def pull_model(name: str):
    """拉取（下载）模型，实时显示进度条"""
    payload = {"name": name, "stream": True}
    try:
        with requests.post(
            f"{OLLAMA_HOST}/api/pull", json=payload, stream=True, timeout=None
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                status = data.get("status", "")

                if status == "success":
                    print(f"\n✅ 模型 {name} 下载完成")
                    return
                if status == "downloading":
                    total = data.get("total", 0) or 0
                    completed = data.get("completed", 0) or 0
                    pct = data.get("percentage") or (
                        completed / total * 100 if total else 0
                    )
                    print(
                        f"\r⬇️  已下载 {completed/1024**2:.1f} MB / "
                        f"{total/1024**2:.1f} MB（{pct:.1f}%）",
                        end="",
                        flush=True,
                    )
                else:
                    # 其它状态：pulling manifest / verifying sha256 / writing model ...
                    print(f"📦 {status}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接 Ollama 服务，请先启动 Ollama（命令行运行 ollama serve）")


def main():
    args = sys.argv[1:]
    if args and args[0] == "list":
        list_models()
    elif args and args[0] == "pull" and len(args) >= 2:
        pull_model(args[1])
    else:
        print(
            "用法：\n"
            "  python download.py list            # 查看本地模型\n"
            "  python download.py pull qwen3:0.8b # 下载模型（示例）\n"
        )
        # 默认展示本地模型
        list_models()


if __name__ == "__main__":
    main()
