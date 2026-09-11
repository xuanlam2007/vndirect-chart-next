#!/usr/bin/env python3
"""
Công cụ nhận dữ liệu trực tiếp từ dchart-socket VNDirect

Giao thức được phân tích từ HAR, dùng Engine.IO v3 và Socket.IO v2

  connect: wss://dchart-socket.vndirect.com.vn/socket.io/?EIO=3&transport=websocket

  máy chủ -> máy khách, gói mở Engine.IO loại '0':
      0{"sid":"...","upgrades":[...],"pingInterval":25000,"pingTimeout":60000}

  máy khách -> máy chủ, kết nối namespace mặc định và namespace "/socket.io"
      40
      40/socket.io

  máy chủ -> máy khách, xác nhận kết nối từng namespace
      40{"sid":"..."}
      40/socket.io,{"sid":"..."}

  máy khách -> máy chủ, đăng ký mã qua sự kiện Socket.IO
      42/socket.io,["addsymbol","VN30"]

  máy chủ -> máy khách, tick trực tiếp
      42/socket.io,["price",{"symbol":"VN30","price":1970.35,"volume":63375.0,"time":1789020600000}]

  giữ kết nối, trả lời PING ('2') bằng PONG ('3') hoặc gửi PING định kỳ

Mỗi tick được gom thành nến OHLCV và ghi lại vào file CSV hoặc JSON trực tiếp

Cách dùng:
  python3 vndirect_realtime_tail.py --symbol VN30 --resolution 1 --outdir ./live
"""

import argparse
import asyncio
import csv
import json
import os
import time
from datetime import datetime, timezone
from urllib.parse import quote

import websockets

WS_URL = "wss://dchart-socket.vndirect.com.vn/socket.io/"
NAMESPACE = "/socket.io"

RESOLUTION_SECONDS = {
    "1": 60, "5": 300, "15": 900, "30": 1800, "60": 3600,
    "D": 86400, "W": 604800,
}


def bucket_start(ts_ms, resolution):
    secs = RESOLUTION_SECONDS.get(resolution, 60)
    return (int(ts_ms // 1000) // secs) * secs


class BarBuilder:
    def __init__(self, resolution, outpath):
        self.resolution = resolution
        self.outpath = outpath
        self.bars = {}  # thời gian nến -> [mở,cao,thấp,đóng,khối lượng]
        os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)

    def add_tick(self, price, volume, ts_ms):
        b = bucket_start(ts_ms, self.resolution)
        if b not in self.bars:
            self.bars[b] = [price, price, price, price, volume or 0]
        else:
            o, h, l, c, v = self.bars[b]
            h = max(h, price)
            l = min(l, price)
            c = price
            v = v + (volume or 0)
            self.bars[b] = [o, h, l, c, v]
        self._flush()

    def _flush(self):
        rows = sorted(self.bars.items())
        with open(self.outpath, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "datetime_utc", "open", "high", "low", "close", "volume"])
            for t, (o, h, l, c, v) in rows:
                dt = datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
                w.writerow([t, dt, o, h, l, c, v])


async def keepalive(ws, interval_s):
    while True:
        await asyncio.sleep(interval_s)
        try:
            await ws.send("2")  # Gửi PING Engine.IO
        except websockets.ConnectionClosed:
            return


async def run(symbol, resolution, outdir):
    outpath = os.path.join(outdir, resolution, f"{symbol}.csv")
    builder = BarBuilder(resolution, outpath)

    ws_url = f"{WS_URL}?symbol={quote(symbol)}&EIO=3&transport=websocket"
    async with websockets.connect(ws_url, ping_interval=None) as ws:
        # 1) Gói mở Engine.IO
        opened = await ws.recv()
        assert opened[0] == "0", f"unexpected open packet: {opened!r}"
        meta = json.loads(opened[1:])
        ping_interval_s = meta.get("pingInterval", 25000) / 1000
        print(f"connected sid={meta.get('sid')} pingInterval={ping_interval_s}s")

        ka_task = asyncio.create_task(keepalive(ws, ping_interval_s))

        # 2) Kết nối namespace mặc định và namespace đích
        await ws.send("40")
        await ws.send(f"40{NAMESPACE}")

        # 3) Đăng ký mã trong namespace đích
        await ws.send(f'42{NAMESPACE},["addsymbol","{symbol}"]')
        print(f"subscribed to {symbol}, writing bars to {outpath}")

        try:
            async for msg in ws:
                if msg == "2":  # PING từ máy chủ, trả lời PONG
                    await ws.send("3")
                    continue
                if msg == "3":  # Bỏ qua PONG
                    continue
                if not msg.startswith("42"):
                    continue
                # Bỏ tiền tố Engine.IO và Socket.IO cùng namespace nếu có
                payload = msg[2:]
                if payload.startswith(NAMESPACE + ","):
                    payload = payload[len(NAMESPACE) + 1:]
                try:
                    event, data = json.loads(payload)
                except (ValueError, json.JSONDecodeError):
                    continue
                if event == "price" and data.get("symbol") == symbol:
                    builder.add_tick(data["price"], data.get("volume", 0), data["time"])
                    print(f"{datetime.now().isoformat(timespec='seconds')} "
                          f"{symbol} {data['price']} vol={data.get('volume')}")
        finally:
            ka_task.cancel()


def main():
    ap = argparse.ArgumentParser(description="Tail VNDirect realtime prices into OHLCV bars")
    ap.add_argument("--symbol", required=True, help="e.g. VN30, VNM, VNINDEX")
    ap.add_argument("--resolution", default="1", choices=list(RESOLUTION_SECONDS.keys()))
    ap.add_argument("--outdir", default="./live")
    args = ap.parse_args()

    while True:
        try:
            asyncio.run(run(args.symbol, args.resolution, args.outdir))
        except (websockets.ConnectionClosed, OSError) as e:
            print(f"disconnected ({e}), reconnecting in 3s...")
            time.sleep(3)


if __name__ == "__main__":
    main()
