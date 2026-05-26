#!/usr/bin/env python3
"""正确版patch - 在Ombre-Brain-main文件夹运行：python patch_server3.py"""
import os

API_CODE = '''

# ==================== 前端数据接口 ====================
from fastapi import Request as _FRequest
from fastapi.middleware.cors import CORSMiddleware as _CORS
from fastapi.responses import JSONResponse as _FJSON

app.add_middleware(
    _CORS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/diary")
async def api_save_diary(req: _FRequest):
    try:
        data = await req.json()
        who = data.get("who", "")
        title = data.get("title", "无题")
        content = data.get("content", "")
        mood = data.get("mood", "")
        date = data.get("date", "")
        if not content:
            return _FJSON({"ok": False, "msg": "内容为空"})
        text = f"【日记·{who}·{date}】{title}\\n心情：{mood}\\n{content}"
        bid = await bm.create(content=text, tags=[f"日记", who, "前端"], importance=5)
        return _FJSON({"ok": True, "id": str(bid)})
    except Exception as e:
        return _FJSON({"ok": False, "msg": str(e)})

@app.post("/api/letter")
async def api_save_letter(req: _FRequest):
    try:
        data = await req.json()
        who = data.get("who", "")
        title = data.get("title", "无题")
        content = data.get("content", "")
        date = data.get("date", "")
        if not content:
            return _FJSON({"ok": False, "msg": "内容为空"})
        text = f"【信件·{who}·{date}】{title}\\n{content}"
        bid = await bm.create(content=text, tags=["信件", who, "前端"], importance=6)
        return _FJSON({"ok": True, "id": str(bid)})
    except Exception as e:
        return _FJSON({"ok": False, "msg": str(e)})

@app.post("/api/quote")
async def api_save_quote(req: _FRequest):
    try:
        data = await req.json()
        text = data.get("text", "")
        feelings = data.get("feelings", [])
        date = data.get("date", "")
        if not text:
            return _FJSON({"ok": False, "msg": "内容为空"})
        feel_text = "\\n".join([f"{f.get('from','')}：{f.get('text','')}" for f in feelings]) if feelings else ""
        full = f"【摘录·{date}】{text}" + (f"\\n感受：\\n{feel_text}" if feel_text else "")
        bid = await bm.create(content=full, tags=["摘录", "书架", "前端"], importance=5)
        return _FJSON({"ok": True, "id": str(bid)})
    except Exception as e:
        return _FJSON({"ok": False, "msg": str(e)})

@app.get("/api/ping")
async def api_ping():
    return _FJSON({"ok": True, "service": "memory-library"})

# ==================== 前端数据接口结束 ====================
'''

server_path = "server.py"
if not os.path.exists(server_path):
    print("❌ 找不到 server.py")
    exit(1)

with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

if "前端数据接口" in content:
    print("✅ 接口已存在")
    exit(0)

# 找bm变量名
import re
bm_matches = re.findall(r'(\w+)\s*=\s*BucketManager\(', content)
bm_name = bm_matches[0] if bm_matches else "bm"
print(f"找到 BucketManager 变量名：{bm_name}")

fixed = API_CODE.replace("await bm.create(", f"await {bm_name}.create(")

with open("server.py.bak3", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已备份到 server.py.bak3")

with open(server_path, "a", encoding="utf-8") as f:
    f.write(fixed)

print("✅ 接口已添加")
print("运行：git add . && git commit -m 'fix frontend api v2' && git push")
