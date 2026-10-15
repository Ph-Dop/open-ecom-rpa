"""列出当前 Edge 所有 tab 的 URL 和标题，并保存 storage_state。"""

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]

        print("=== 当前所有 tab ===")
        for i, p in enumerate(ctx.pages):
            print(f"[{i}] {p.url}")
            print(f"    title: {p.title()}")

        # 保存 storage_state（不管哪个 tab）
        ctx.storage_state(path=".auth/temu_default.json")
        print("\n[ok] storage_state 已保存")

        # 对最后一个非 login 的 tab 截图
        for p in ctx.pages:
            if "login" not in p.url:
                p.screenshot(path=".auth/temu_home.png", full_page=False)
                print(f"[ok] 截图: {p.url}")
                break

        browser.close()


if __name__ == "__main__":
    main()
