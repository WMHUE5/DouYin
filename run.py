# coding:utf-8
import os
import asyncio
import json
import requests
import websockets
import time

# ==========================
# 配置
# ==========================
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "clt.39afc90818a46c217f520832f4c0bec72dq4f589e8USLqwqJV8Ig5fn65eL_lf")
ROOM_ID = os.environ.get("ROOM_ID", "570021721892")
RECONNECT_DELAY = 5  # 秒

# ==========================
# 获取 WebSocket 地址
# ==========================
def get_ws_url():
    url = f"https://open.douyin.com/live/data/room?access_token={ACCESS_TOKEN}&room_id={ROOM_ID}"
    resp = requests.get(url)
    data = resp.json()
    if "data" in data and "ws_url" in data["data"]:
        return data["data"]["ws_url"]
    else:
        raise Exception(f"获取 ws_url 失败: {data}")

# ==========================
# 弹幕监听
# ==========================
async def listen_live():
    while True:
        try:
            ws_url = get_ws_url()
            print(f"[INFO] 连接 WebSocket: {ws_url}")
            async with websockets.connect(ws_url) as ws:

                # 心跳协程
                async def heartbeat():
                    while True:
                        try:
                            await ws.send(json.dumps({"type": "heartbeat"}))
                            await asyncio.sleep(30)
                        except Exception as e:
                            print("[ERROR] 心跳异常:", e)
                            break

                asyncio.create_task(heartbeat())

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # 弹幕
                    if data.get("type") == "danmaku":
                        print(f"[弹幕] {data['user_name']}: {data['content']}")
                    # 礼物
                    elif data.get("type") == "gift":
                        print(f"[礼物] {data['user_name']} 送了 {data['gift_name']} x {data.get('quantity',1)}")
                    else:
                        print(f"[消息] {data}")
        except Exception as e:
            print(f"[ERROR] 连接异常，{RECONNECT_DELAY}s 后重连: {e}")
            time.sleep(RECONNECT_DELAY)

# ==========================
# 启动
# ==========================
if __name__ == "__main__":
    asyncio.run(listen_live())
