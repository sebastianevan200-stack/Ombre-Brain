"""前端数据接口 - memory library"""
from fastapi import Request
from fastapi.responses import JSONResponse


def register_frontend_routes(app, bucket_mgr):
    """注册前端路由到app"""

    @app.post("/api/diary")
    async def api_diary(req: Request):
        try:
            d = await req.json()
            who = d.get("who", "")
            text = f"【日记·{who}·{d.get('date','')}】{d.get('title','无题')}\n心情：{d.get('mood','')}\n{d.get('content','')}"
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
            text = f"【信件·{who}·{d.get('date','')}】{d.get('title','无题')}\n{d.get('content','')}"
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
            feel = "\n".join([f"{f.get('from','')}：{f.get('text','')}" for f in feelings])
            full = f"【摘录·{d.get('date','')}】{text}" + (f"\n感受：\n{feel}" if feel else "")
            bid = await bucket_mgr.create(content=full, tags=["摘录", "书架", "前端"], importance=5)
            return JSONResponse({"ok": True, "id": str(bid)})
        except Exception as e:
            return JSONResponse({"ok": False, "msg": str(e)})

    @app.get("/api/ping")
    async def api_ping():
        return JSONResponse({"ok": True, "service": "memory-library"})
