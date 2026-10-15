"""交互式登录 Temu 卖家后台，自动保存 storage_state。

用法：
    cd backend
    .\\.venv\\Scripts\\python.exe -m scripts.login_temu

流程：
1. 弹出真实浏览器（headless=False）打开 Temu 卖家后台登录页
2. 你在页面里完成登录（账号密码 + 滑块 / 短信验证码）
3. 脚本自动检测到登录成功（URL 离开登录页），自动保存 storage_state 并关闭
"""

from __future__ import annotations

import time

from app.browser.pool import BrowserPool


SELLER_HOME = "https://seller.kuajingmaihuo.com/"
LOGIN_KEYWORDS = ("login", "passport", "signin", "account")


def is_logged_in(url: str) -> bool:
    return not any(k in url.lower() for k in LOGIN_KEYWORDS)


def main() -> None:
    pool = BrowserPool(headless=False)
    pool.start()
    try:
        ctx = pool.new_context("temu::default")
        page = ctx.new_page()
        page.goto(SELLER_HOME, wait_until="domcontentloaded")

        print("\n[提示] 浏览器已打开，请在页面中完成登录。")
        print("脚本会自动检测登录成功并保存，最长等待 5 分钟...\n")

        deadline = time.time() + 300
        while time.time() < deadline:
            url = page.url
            if is_logged_in(url):
                print(f"[ok] 检测到登录成功，当前 URL: {url}")
                break
            time.sleep(2)
        else:
            print("[warn] 超时未检测到登录，仍然保存当前状态")

        pool.save_state(ctx)
        page.screenshot(path=".auth/temu_home.png", full_page=False)
        print("[ok] 登录态已保存到 .auth/temu::default.json")
        print("[ok] 首页截图: .auth/temu_home.png")

        # 再停留 2 秒让你看到首页
        time.sleep(2)
    finally:
        pool.close()


if __name__ == "__main__":
    main()
