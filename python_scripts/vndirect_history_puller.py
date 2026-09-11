#!/usr/bin/env python3
"""
Công cụ tải dữ liệu lịch sử OHLCV từ dchart-api VNDirect

Các endpoint công khai được phân tích từ dữ liệu mạng:

  Thông tin mã: GET https://dchart-api.vndirect.com.vn/dchart/symbols?symbol=<SYM>
  Lịch sử     : GET https://dchart-api.vndirect.com.vn/dchart/history
                    ?resolution=<1|5|15|30|60|D|W|M>&symbol=<SYM>&from=<unix>&to=<unix>
                -> {"t":[...],"o":[...],"h":[...],"l":[...],"c":[...],"v":[...],"s":"ok"}
  Danh sách mã: GET https://api-finfo.vndirect.com.vn/v4/stocks
                    ?q=type:IFC,ETF,STOCK~status:LISTED&fields=code,companyName,floor,industryName&size=3000
  Phái sinh   : GET https://api-finfo.vndirect.com.vn/v4/derivatives
                    ?q=underlyingType:BOND,INDEX~status:LISTED&size=10000

API lịch sử giới hạn khoảng thời gian mỗi lần gọi
Script phân trang ngược bằng thời gian của nến sớm nhất

Cách dùng:
  python3 vndirect_history_puller.py --symbols VN30 VNINDEX VNM --resolutions D 1
  python3 vndirect_history_puller.py --all-stocks --resolutions D --outdir ./data

Đầu ra: <outdir>/<resolution>/<symbol>.csv
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

HISTORY_URL = "https://dchart-api.vndirect.com.vn/dchart/history"
STOCKLIST_URL = "https://api-finfo.vndirect.com.vn/v4/stocks"
DERIVATIVES_URL = "https://api-finfo.vndirect.com.vn/v4/derivatives"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://dchart.vndirect.com.vn",
    "Referer": "https://dchart.vndirect.com.vn/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
}

RESOLUTIONS = ["1", "5", "15", "30", "60", "D", "W", "M"]
EARLIEST_TS = int(datetime(2000, 1, 1, tzinfo=timezone.utc).timestamp())


def fetch_stock_list(kinds="IFC,ETF,STOCK"):
    params = {
        "q": f"type:{kinds}~status:LISTED",
        "fields": "code,companyName,floor,industryName",
        "size": 3000,
    }
    r = requests.get(STOCKLIST_URL, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return [d["code"] for d in r.json().get("data", [])]


def fetch_index_derivative_list():
    params = {"q": "underlyingType:BOND,INDEX~status:LISTED", "size": 10000}
    r = requests.get(DERIVATIVES_URL, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return [d["code"] for d in r.json().get("data", [])]


def fetch_history_page(symbol, resolution, frm, to, session, retries=3):
    params = {"resolution": resolution, "symbol": symbol, "from": frm, "to": to}
    for attempt in range(retries):
        try:
            r = session.get(HISTORY_URL, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
            if data.get("s") != "ok":
                return None
            return data
        except (requests.RequestException, json.JSONDecodeError) as e:
            wait = 2 ** attempt
            print(f"    retry {symbol} {resolution} ({e}), sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None


def fetch_full_history(symbol, resolution, session, end_ts=None, earliest_ts=EARLIEST_TS, sleep=0.3):
    """Phân trang ngược đến khi API không trả thêm nến cũ"""
    end_ts = end_ts or int(time.time())
    all_rows = []
    to_ts = end_ts
    seen_min_t = None

    while to_ts > earliest_ts:
        page = fetch_history_page(symbol, resolution, earliest_ts, to_ts, session)
        if not page or not page.get("t"):
            break
        rows = list(zip(page["t"], page["o"], page["h"], page["l"], page["c"], page["v"]))
        if seen_min_t is not None:
            rows = [r for r in rows if r[0] < seen_min_t]
        if not rows:
            break
        all_rows = rows + all_rows
        new_min_t = rows[0][0]
        if seen_min_t is not None and new_min_t >= seen_min_t:
            break  # Không có tiến triển nên dừng để tránh lặp vô hạn
        seen_min_t = new_min_t
        to_ts = new_min_t - 1
        if len(rows) < 2:
            break  # API gần như đã hết dữ liệu cũ
        time.sleep(sleep)

    return all_rows


def save_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "datetime_utc", "open", "high", "low", "close", "volume"])
        for t, o, h, l, c, v in rows:
            dt = datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
            w.writerow([t, dt, o, h, l, c, v])


def main():
    ap = argparse.ArgumentParser(description="Pull historical OHLCV bars from VNDirect dchart-api")
    ap.add_argument("--symbols", nargs="+", default=[], help="Symbols e.g. VN30 VNINDEX VNM")
    ap.add_argument("--all-stocks", action="store_true", help="Add the full listed stock/ETF universe")
    ap.add_argument("--all-derivatives", action="store_true", help="Add listed index/bond futures")
    ap.add_argument("--resolutions", nargs="+", default=["D"], choices=RESOLUTIONS)
    ap.add_argument("--outdir", default="./data")
    ap.add_argument("--sleep", type=float, default=0.3, help="Delay between paged requests (s)")
    args = ap.parse_args()

    symbols = list(args.symbols)
    if args.all_stocks:
        print("Fetching stock/ETF universe from finfo...")
        symbols += fetch_stock_list()
    if args.all_derivatives:
        print("Fetching index/bond derivatives universe from finfo...")
        symbols += fetch_index_derivative_list()
    symbols = sorted(set(symbols))
    if not symbols:
        ap.error("Provide --symbols and/or --all-stocks/--all-derivatives")

    session = requests.Session()
    total = len(symbols) * len(args.resolutions)
    done = 0
    for symbol in symbols:
        for res in args.resolutions:
            done += 1
            print(f"[{done}/{total}] {symbol} {res} ...", end=" ", flush=True)
            rows = fetch_full_history(symbol, res, session, sleep=args.sleep)
            if not rows:
                print("no data")
                continue
            path = os.path.join(args.outdir, res, f"{symbol}.csv")
            save_csv(rows, path)
            first = datetime.fromtimestamp(rows[0][0], tz=timezone.utc).date()
            last = datetime.fromtimestamp(rows[-1][0], tz=timezone.utc).date()
            print(f"{len(rows)} bars ({first} -> {last}) -> {path}")


if __name__ == "__main__":
    main()
