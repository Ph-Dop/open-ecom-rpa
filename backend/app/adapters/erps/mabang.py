"""马帮 ERP 适配器（骨架）。

当前没有马帮账号，先 mock 实现：返回成功，不实际推送。
未来接入时：
1. 用 CDP 接管已登录马帮的浏览器
2. 定位到"批量创建订单"页面
3. 填表提交
"""

from __future__ import annotations

from app.adapters.base import ErpAdapter, Order


class MabangAdapter(ErpAdapter):
    erp = "mabang"

    def login(self, credential: dict) -> None:
        return None

    def push_orders(self, orders: list[Order]) -> dict:
        # TODO: 真实调用马帮"批量导入订单"接口/页面
        return {
            "pushed": len(orders),
            "failed": 0,
            "message": "mock: 马帮未接入，仅记录数量",
        }
