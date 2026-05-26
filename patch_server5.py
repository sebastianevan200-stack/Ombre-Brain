#!/usr/bin/env python3
"""
patch v5 - 单独文件方式，不破坏server.py结构
在 Ombre-Brain-main 文件夹运行：python patch_server5.py
"""
import os
import re

# 1. 写 frontend_routes.py
routes_code = '''"""前端数据接口 - memory library"""
from fastapi import Request
from fastapi.responses import JSONResponse


def register_frontend_routes(app, bucket_mgr):
    """注册前端路由到app"""

    @app.post("/api/diary")
    async def api_diary(req: Request):
        try:
            d = await req.json()
            who = d.get("who", "")
            text = f"【日记·{who}·{d.get('date','')}】{d.get('title','无题')}\\n心情：{d.get('mood','')}\\n{d.get('content','')}"
            if not d.get("content"):
                return JSONResponse({"ok": False})
            bid = await bucket_mgr.create(content=text, tags=["日记", who, "前端"], importance=5)
            return JSONResponse({"ok": True, "id": str(bid)})
        except Exception as e:
            return JSONResponse({"ok": False, "msg": str(e)})

    @app.post("/api/letter")
    async def api_letter(req: Request):
        try:
            d = await req.json()
            who = d.get("who", "")
            text = f"【信件·{who}·{d.get('date','')}】{d.get('title','无题')}\\n{d.get('content','')}"
            if not d.get("content"):
                return JSONResponse({"ok": False})
            bid = await bucket_mgr.create(content=text, tags=["信件", who, "前端"], importance=6)
            return JSONResponse({"ok": True, "id": str(bid)})
        except Exception as e:
            return JSONResponse({"ok": False, "msg": str(e)})

    @app.post("/api/quote")
    async def api_quote(req: Request):
        try:
            d = await req.json()
            text = d.get("text", "")
            if not text:
                return JSONResponse({"ok": False})
            feelings = d.get("feelings", [])
            feel = "\\n".join([f"{f.get('from','')}：{f.get('text','')}" for f in feelings])
            full = f"【摘录·{d.get('date','')}】{text}" + (f"\\n感受：\\n{feel}" if feel else "")
            bid = await bucket_mgr.create(content=full, tags=["摘录", "书架", "前端"], importance=5)
            return JSONResponse({"ok": True, "id": str(bid)})
        except Exception as e:
            return JSONResponse({"ok": False, "msg": str(e)})

    @app.get("/api/ping")
    async def api_ping():
        return JSONResponse({"ok": True, "service": "memory-library"})
'''

with open("frontend_routes.py", "w", encoding="utf-8") as f:
    f.write(routes_code)
print("✅ 已创建 frontend_routes.py")

# 2. 在 server.py 里找 uvicorn.run 那一行，在前面加两行
server_path = "server.py"
with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 清掉之前的接口代码
if "前端数据接口" in content:
    start = content.find("\n# ==================== 前端数据接口")
    if start != -1:
        content = content[:start]
        print("✅ 已清除旧接口代码")

# 找 uvicorn.run(_app 所在的行，在那行之前插入两行
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if 'uvicorn.run(_app' in line:
        insert_idx = i
        break

if insert_idx is None:
    print("❌ 找不到 uvicorn.run(_app")
    exit(1)

print(f"✅ 找到 uvicorn.run 在第 {insert_idx+1} 行")

# 在那行之前插入
insert_lines = [
    "    # 注册前端路由",
    "    from frontend_routes import register_frontend_routes",
    "    register_frontend_routes(_app, bucket_mgr)",
    "",
]

lines = lines[:insert_idx] + insert_lines + lines[insert_idx:]
new_content = '\n'.join(lines)

with open("server.py.bak5", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已备份到 server.py.bak5")

with open(server_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ server.py 修改完成")
print("运行：git add . && git commit -m 'add frontend routes v5' && git push")
