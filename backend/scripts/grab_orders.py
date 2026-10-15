"""进入订单列表页，抓订单数据。"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = b.contexts[0]
        page = ctx.pages[0]

        # 关右侧消息弹窗 X
        try:
            page.locator('div[aria-label="关闭"], button:has-text("关闭")').first.click(timeout=2000)
        except Exception:
            pass
        # 兜底：按 ESC
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        # 点左侧"销售管理"子菜单（二级菜单第一个）
        # 父菜单已展开，直接点文本
        sub = page.locator("text=销售管理 >> nth=1")
        sys.stdout.write(f"sub count: {sub.count()}\n")
        sub.first.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(3000)

        page.screenshot(path=".auth/temu_orders2.png", full_page=False)
        sys.stdout.write(f"url: {page.url}\n")

        # 抓表格行
        rows = page.locator("table tbody tr")
        sys.stdout.write(f"rows: {rows.count()}\n")
        for i in range(min(rows.count(), 5)):
            text = rows.nth(i).inner_text()
            sys.stdout.write(f"--- row {i} ---\n{text}\n")

        sys.stdout.flush()
        b.close()


if __name__ == "__main__":
    main()
