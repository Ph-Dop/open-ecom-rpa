"""浏览器冒烟测试：起 chromium，打开 Temu 卖家首页，截图保存。

用法：
    cd backend
    .\\.venv\\Scripts\\python.exe -m scripts.smoke_browser
"""

from __future__ import annotations

from pathlib import Path

from app.browser.pool import BrowserPool


OUT_DIR = Path(__file__).resolve().parents[1] / ".smoke"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    pool = BrowserPool(headless=True)
    pool.start()
    try:
        ctx = pool.new_context("smoke")
        page = ctx.new_page()
        page.goto("https://www.temu.com", wait_until="domcontentloaded", timeout=30000)
        title = page.title()
        out = OUT_DIR / "temu_home.png"
        page.screenshot(path=str(out), full_page=False)
        print(f"[ok] title={title!r}")
        print(f"[ok] screenshot -> {out}")
    finally:
        pool.close()


if __name__ == "__main__":
    main()
