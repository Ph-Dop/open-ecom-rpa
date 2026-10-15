"""浏览器池封装。

设计目标：
- 统一管理 Playwright 的 launch / new_context / close
- 每个账号一个独立 context，登录态通过 storage_state 持久化
- 支持 headless 开关、默认 UA、视口
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from app.core.config import settings

# 登录态统一存到项目根目录下 .auth/，gitignore 已忽略
AUTH_DIR = Path(__file__).resolve().parents[2] / ".auth"
AUTH_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)


class BrowserPool:
    """简单的单浏览器池：全局一个 Browser，按账号开多个 Context。"""

    def __init__(self, headless: bool | None = None) -> None:
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._headless = settings.playwright_headless if headless is None else headless

    def start(self) -> None:
        if self._browser is not None:
            return
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self._headless)

    def close(self) -> None:
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._pw:
            self._pw.stop()
            self._pw = None

    def _state_path(self, account_key: str) -> Path:
        return AUTH_DIR / f"{account_key}.json"

    def new_context(self, account_key: str, *, user_agent: str = DEFAULT_UA) -> BrowserContext:
        """按账号开 context。若已有 storage_state 则自动加载。"""
        assert self._browser is not None, "call start() first"

        state_file = self._state_path(account_key)
        kwargs: dict[str, Any] = {
            "user_agent": user_agent,
            "viewport": {"width": 1440, "height": 900},
            "locale": "zh-CN",
        }
        if state_file.exists():
            kwargs["storage_state"] = str(state_file)

        ctx = self._browser.new_context(**kwargs)
        # 把当前 context 的 storage_state 绑回路径，供后续 save
        ctx._state_path = state_file  # type: ignore[attr-defined]
        return ctx

    def save_state(self, ctx: BrowserContext) -> None:
        state_file: Path = getattr(ctx, "_state_path", None)
        if state_file is None:
            return
        ctx.storage_state(path=str(state_file))


_pool: BrowserPool | None = None


def get_pool() -> BrowserPool:
    global _pool
    if _pool is None:
        _pool = BrowserPool()
    return _pool
