"""前端数据接口 - memory library - Starlette版"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def api_diary(req: Request):
    try:
        d = await req.json()
        who = d.get("who", "")
        text = "【日记·" + who + "·" + d.get("date","") + "】" + d.get("title","无题") + "\n心情：" + d.get("mood","") + "\n" + d.get("content","")
        if not d.get("content"):
            return JSONResponse({"ok": False})
        bucket_mgr = req.app.state.bucket_mgr
        bid = await bucket_mgr.create(content=text, tags=["日记", who, "前端"], importance=5)
        return JSONResponse({"ok": True, "id": str(bid)})
    except Exception as e:
        return JSONResponse({"ok": False, "msg": str(e)})


async def api_letter(req: Request):
    try:
        d = await req.json()
        who = d.get("who", "")
        text = "【信件·" + who + "·" + d.get("date","") + "】" + d.get("title","无题") + "\n" + d.get("content","")
        if not d.get("content"):
            return JSONResponse({"ok": False})
        bucket_mgr = req.app.state.bucket_mgr
        bid = await bucket_mgr.create(content=text, tags=["信件", who, "前端"], importance=6)
        return JSONResponse({"ok": True, "id": str(bid)})
    except Exception as e:
        return JSONResponse({"ok": False, "msg": str(e)})


async def api_quote(req: Request):
    try:
        d = await req.json()
        text = d.get("text", "")
        if not text:
            return JSONResponse({"ok": False})
        feelings = d.get("feelings", [])
        feel = "\n".join([f.get("from","") + "：" + f.get("text","") for f in feelings])
        full = "【摘录·" + d.get("date","") + "】" + text + ("\n感受：\n" + feel if feel else "")
        bucket_mgr = req.app.state.bucket_mgr
        bid = await bucket_mgr.create(content=full, tags=["摘录", "书架", "前端"], importance=5)
        return JSONResponse({"ok": True, "id": str(bid)})
    except Exception as e:
        return JSONResponse({"ok": False, "msg": str(e)})


async def api_ping(req: Request):
    return JSONResponse({"ok": True, "service": "memory-library"})


async def api_memories(req: Request):
    """返回所有记忆桶，供前端记忆库页面直接读取"""
    try:
        bucket_mgr = req.app.state.bucket_mgr
        buckets = await bucket_mgr.list_all(include_archive=False)
        result = []
        for b in buckets:
            result.append({
                "id": b.get("id", ""),
                "title": b.get("title") or b.get("id", "")[:8],
                "content": b.get("content", ""),
                "tags": b.get("tags", []),
                "importance": b.get("importance", 5),
                "pinned": b.get("pinned", False),
            })
        # 按重要度降序
        result.sort(key=lambda x: (x["pinned"], x["importance"]), reverse=True)
        return JSONResponse({"ok": True, "memories": result})
    except Exception as e:
        return JSONResponse({"ok": False, "msg": str(e)})


FRONTEND_ROUTES = [
    Route("/api/diary", api_diary, methods=["POST"]),
    Route("/api/letter", api_letter, methods=["POST"]),
    Route("/api/quote", api_quote, methods=["POST"]),
    Route("/api/ping", api_ping, methods=["GET"]),
    Route("/api/memories", api_memories, methods=["GET"]),
]


def register_frontend_routes(app, bucket_mgr):
    app.state.bucket_mgr = bucket_mgr
    app.routes.extend(FRONTEND_ROUTES)
