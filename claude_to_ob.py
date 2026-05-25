"""
Claude JSON导出 → Ombre Brain buckets 导入工具
用法: python claude_to_ob.py --input "JSON文件路径"
"""

import os
import json
import uuid
import argparse
from datetime import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
BUCKETS_DIR = Path(__file__).parent / "buckets" / "dynamic"
CHUNK_SIZE = 8  # 每几轮对话合并成一个bucket
# ─────────────────────────────────────────────────────


def gen_id():
    return uuid.uuid4().hex[:12]


def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def parse_claude_json(data):
    """解析Claude导出的JSON格式，返回对话轮次列表"""
    turns = []
    conversations = data if isinstance(data, list) else [data]

    for conv in conversations:
        if not isinstance(conv, dict):
            continue
        messages = conv.get("chat_messages", conv.get("messages", []))
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            content = msg.get("text", msg.get("content", ""))
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "") for p in content if isinstance(p, dict)
                )
            if not content or not content.strip():
                continue
            role = msg.get("sender", msg.get("role", "user"))
            turns.append({"role": role, "content": content.strip()})

    return turns


def chunk_turns(turns, size=CHUNK_SIZE):
    """把对话轮次分成若干块"""
    chunks = []
    for i in range(0, len(turns), size):
        chunks.append(turns[i:i + size])
    return chunks


def write_bucket(name, content, index, total):
    """写入一个bucket文件"""
    BUCKETS_DIR.mkdir(parents=True, exist_ok=True)
    mid = gen_id()
    ts = now_iso()

    front = f"""---
id: {mid}
name: {name}
created_at: {ts}
updated_at: {ts}
domain:
- 对话记录
tags:
- 历史导入
- claude
importance: 6
valence: 0.6
arousal: 0.4
resolved: false
pinned: false
---
"""
    filepath = BUCKETS_DIR / f"{mid}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(front)
        f.write(content)

    return filepath.name


def main():
    parser = argparse.ArgumentParser(description="Claude JSON → Ombre Brain 导入工具")
    parser.add_argument("--input", required=True, help="Claude JSON导出文件路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 找不到文件: {input_path}")
        return

    print(f"📂 读取文件: {input_path.name}")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("🔍 解析对话内容...")
    turns = parse_claude_json(data)
    print(f"✅ 找到 {len(turns)} 条消息")

    if not turns:
        print("❌ 没有找到任何对话内容，请检查JSON格式")
        return

    chunks = chunk_turns(turns, CHUNK_SIZE)
    print(f"📦 分成 {len(chunks)} 个记忆块，开始写入...")

    for i, chunk in enumerate(chunks):
        lines = []
        for turn in chunk:
            role_label = "我" if turn["role"] in ("user", "human") else "Claude"
            lines.append(f"**{role_label}**: {turn['content']}\n")
        content = "\n".join(lines)
        name = f"导入记录 {i+1}/{len(chunks)}"
        fname = write_bucket(name, content, i + 1, len(chunks))
        print(f"  [{i+1}/{len(chunks)}] {fname}")

    print(f"\n🎉 完成！共写入 {len(chunks)} 个记忆桶")
    print(f"📁 保存位置: {BUCKETS_DIR}")


if __name__ == "__main__":
    main()
