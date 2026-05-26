#!/usr/bin/env python3
"""patch v6 - 修正缩进问题"""
import os

server_path = "server.py"
with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 清掉旧的接口代码
if "前端数据接口" in content:
    start = content.find("\n# ==================== 前端数据接口")
    if start != -1:
        content = content[:start]

# 找 uvicorn.run(_app 所在行
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if 'uvicorn.run(_app' in line:
        insert_idx = i
        # 看这行的缩进
        indent = len(line) - len(line.lstrip())
        print(f"找到第{i+1}行，缩进={indent}：{line.strip()}")
        break

if insert_idx is None:
    print("❌ 找不到 uvicorn.run(_app")
    exit(1)

# 用同样的缩进
ind = ' ' * indent
insert_lines = [
    f"{ind}# 注册前端路由",
    f"{ind}from frontend_routes import register_frontend_routes",
    f"{ind}register_frontend_routes(_app, bucket_mgr)",
    f"",
]

lines = lines[:insert_idx] + insert_lines + lines[insert_idx:]
new_content = '\n'.join(lines)

with open("server.py.bak6", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 已备份到 server.py.bak6")

with open(server_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ 完成，缩进已修正")
print("运行：git add . && git commit -m 'fix indent v6' && git push")
