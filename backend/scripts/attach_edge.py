"""通过 CDP 接管 Edge，等待用户在页面中登录，自动保存 storage_state。

前提：Edge 已用 --remote-debugging-port=9222 启动。
"""

from __future__ import annotations

import time

from playwright.sync_api import sync_playwright


LOGIN_KEYWORDS = ("login", "passport", "signin", "account")


def is_logged_in(url: str) -> bool:
    return not any(k in url.lower() for k in LOGIN_KEYWORDS)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]

        # 找到 Temu 标签
        page = None
        for p in ctx.pages:
            if "kuajingmaihuo" in p.url:
                page = p
                break
        if not page:
            print("[!] 没找到 Temu 标签页")
            return

        print(f"[等待] 当前页面: {page.url}")
        print("[提示] 请在 Edge 窗口中完成登录（手机号登录 tab）...")

        deadline = time.time() + 300
        while time.time() < deadline:
            url = page.url
            if is_logged_in(url):
                print(f"[ok] 检测到登录成功: {url}")
                break
            time.sleep(2)
        else:
            print("[warn] 超时，仍尝试保存")

        time.sleep(3)  # 等页面跳转完
        ctx.storage_state(path=".auth/temu_default.json")
        page.screenshot(path=".auth/temu_home.png", full_page=False)
        print("[ok] storage_state 已保存到 .auth/temu_default.json")
        print("[ok] 首页截图: .auth/temu_home.png")


if __name__ == "__main__":
    main()
