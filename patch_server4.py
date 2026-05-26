#!/usr/bin/env python3
"""
正确版patch v4 - 在Ombre-Brain-main文件夹运行：python patch_server4.py
"""
import os
import re

server_path = "server.py"

if not os.path.exists(server_path):
    print("❌ 找不到 server.py")
    exit(1)

with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 先清掉之前加的接口代码
if "前端数据接口" in content:
    start = content.find("\n# ==================== 前端数据接口")
    if start != -1:
        content = content[:start]
        print("✅ 已清除旧接口代码")

# 找到 uvicorn.run(_app 这一行，在它之前插入接口
target = 'uvicorn.run(_app,'
idx = content.find(target)
if idx == -1:
    target = 'uvicorn.run(_app ,'
    idx = content.find(target)
if idx == -1:
    print("❌ 找不到 uvicorn.run(_app，请截图给我看")
    exit(1)

# 往前找到这行的行首
line_start = content.rfind('\n', 0, idx) + 1

API_CODE = '''
    # ==================== 前端数据接口 ====================
    from fastapi import Request as _FReq
    from fastapi.responses import JSONResponse as _FJ

    @_app.post("/api/diary")
    async def _api_diary(req: _FReq):
        try:
            d = await req.json()
            who = d.get("who","")
            text = f"【日记·{who}·{d.get('date','')}】{d.get('title','无题')}\\n心情：{d.get('mood','')}\\n{d.get('content','')}"
            if not d.get('content'):
                return _FJ({"ok":False})
            bid = await bucket_mgr.create(content=text, tags=["日记",who,"前端"], importance=5)
            return _FJ({"ok":True,"id":str(bid)})
        except Exception as e:
            return _FJ({"ok":False,"msg":str(e)})

    @_app.post("/api/letter")
    async def _api_letter(req: _FReq):
        try:
            d = await req.json()
            who = d.get("who","")
            text = f"【信件·{who}·{d.get('date','')}】{d.get('title','无题')}\\n{d.get('content','')}"
            if not d.get('content'):
                return _FJ({"ok":False})
            bid = await bucket_mgr.create(content=text, tags=["信件",who,"前端"], importance=6)
            return _FJ({"ok":True,"id":str(bid)})
        except Exception as e:
            return _FJ({"ok":False,"msg":str(e)})

    @_app.post("/api/quote")
    async def _api_quote(req: _FReq):
        try:
            d = await req.json()
            text = d.get("text","")
            if not text:
                return _FJ({"ok":False})
            feelings = d.get("feelings",[])
            feel = "\\n".join([f"{f.get('from','')}：{f.get('text','')}" for f in feelings])
            full = f"【摘录·{d.get('date','')}】{text}" + (f"\\n感受：\\n{feel}" if feel else "")
            bid = await bucket_mgr.create(content=full, tags=["摘录","书架","前端"], importance=5)
            return _FJ({"ok":True,"id":str(bid)})
        except Exception as e:
            return _FJ({"ok":False,"msg":str(e)})

    @_app.get("/api/ping")
    async def _api_ping():
        return _FJ({"ok":True,"service":"memory-library"})

    # ==================== 前端数据接口结束 ====================

'''

# 插入到uvicorn.run之前
new_content = content[:line_start] + API_CODE + content[line_start:]

with open("server.py.bak4", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已备份到 server.py.bak4")

with open(server_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ 接口已正确插入到uvicorn.run之前")
print("运行：git add . && git commit -m 'fix api insert before uvicorn' && git push")
