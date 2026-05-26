#!/usr/bin/env python3
"""
运行这个脚本，自动把前端API接口加到server.py里
在 Ombre-Brain-main 文件夹里运行：python patch_server.py
"""

import os

API_CODE = '''

# ==================== 前端数据接口 ====================
from fastapi.middleware.cors import CORSMiddleware

# 允许前端跨域访问（如果已有CORSMiddleware可跳过）
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    pass

@app.post("/api/diary")
async def api_save_diary(request):
    from fastapi import Request
    data = await request.json()
    who = data.get("who", "")
    title = data.get("title", "无题")
    content = data.get("content", "")
    mood = data.get("mood", "")
    date = data.get("date", "")
    if not content:
        return {"ok": False}
    text = f"【日记·{who}·{date}】{title}\\n心情：{mood}\\n{content}"
    bucket_id = bucket_manager.create_bucket(content=text, tags=f"日记,{who},前端", importance=5)
    return {"ok": True, "bucket_id": str(bucket_id)}

@app.post("/api/letter")
async def api_save_letter(request):
    from fastapi import Request
    data = await request.json()
    who = data.get("who", "")
    title = data.get("title", "无题")
    content = data.get("content", "")
    date = data.get("date", "")
    if not content:
        return {"ok": False}
    text = f"【信件·{who}·{date}】{title}\\n{content}"
    bucket_id = bucket_manager.create_bucket(content=text, tags=f"信件,{who},前端", importance=6)
    return {"ok": True, "bucket_id": str(bucket_id)}

@app.post("/api/quote")
async def api_save_quote(request):
    from fastapi import Request
    data = await request.json()
    text = data.get("text", "")
    feelings = data.get("feelings", [])
    date = data.get("date", "")
    if not text:
        return {"ok": False}
    feel_text = "\\n".join([f"{f['from']}：{f['text']}" for f in feelings]) if feelings else ""
    full = f"【摘录·{date}】{text}" + (f"\\n感受：\\n{feel_text}" if feel_text else "")
    bucket_id = bucket_manager.create_bucket(content=full, tags="摘录,书架,前端", importance=5)
    return {"ok": True, "bucket_id": str(bucket_id)}

@app.get("/api/ping")
async def api_ping():
    return {"ok": True}

# ==================== 前端数据接口结束 ====================
'''

server_path = "server.py"

if not os.path.exists(server_path):
    print("❌ 找不到 server.py，请确认在正确的文件夹里")
    exit(1)

with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

if "前端数据接口" in content:
    print("✅ 接口已经存在，不需要重复添加")
    exit(0)

# 备份
with open("server.py.bak", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已备份到 server.py.bak")

# 追加到末尾
with open(server_path, "a", encoding="utf-8") as f:
    f.write(API_CODE)

print("✅ 接口已添加到 server.py")
print("现在运行：git add . && git commit -m 'add frontend api' && git push")
