"""Temu 卖家平台适配器（CDP 模式）。

通过 CDP 接管已登录的 Edge/Chrome，复用用户已有的登录态。
前提：浏览器已用 --remote-debugging-port=9222 启动并登录 Temu。
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from app.adapters.base import EcomPlatformAdapter, Order


class TemuAdapter(EcomPlatformAdapter):
    platform = "temu"

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222") -> None:
        self.cdp_url = cdp_url

    def login(self, credential: dict) -> None:
        """CDP 模式下不需要主动 login，假设浏览器已登录。"""
        return None

    def fetch_new_orders(self) -> list[Order]:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(self.cdp_url)
            ctx = browser.contexts[0]

            # 找到 Temu 标签页
            page = None
            for p in ctx.pages:
                if "temu.com" in p.url or "kuajingmaihuo" in p.url:
                    page = p
                    break
            if not page:
                print("[Temu] 没找到 Temu 标签页", file=sys.stderr)
                browser.close()
                return []

            # TODO: 定位到订单列表页 URL（不同卖家后台版本可能不同）
            # 新店无订单，先抓当前页表格结构做验证
            rows = page.locator("table tbody tr")
            count = rows.count()
            print(f"[Temu] 表格行数: {count}")

            orders: list[Order] = []
            for i in range(min(count, 20)):
                cells = rows.nth(i).locator("td")
                if cells.count() < 3:
                    continue
                order_id = cells.nth(0).inner_text().strip()
                sku = cells.nth(1).inner_text().strip()
                try:
                    qty = int(cells.nth(2).inner_text().strip() or "0")
                except ValueError:
                    qty = 0
                orders.append(Order(order_id=order_id, sku=sku, qty=qty, raw={}))

            browser.close()
            return orders

    def mark_synced(self, order_ids: list[str]) -> None:
        # TODO: 回写"已同步"状态
        return None
