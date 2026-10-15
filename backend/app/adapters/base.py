"""适配器抽象层。

平台侧（卖家后台）实现 `EcomPlatformAdapter`，ERP 侧实现 `ErpAdapter`。
新增平台 = 新增一个文件实现接口，不改核心调度代码。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    sku: str
    qty: int
    raw: dict


class EcomPlatformAdapter(ABC):
    """卖家平台适配器：Temu / Shopee / Amazon ..."""

    platform: str = ""

    @abstractmethod
    def login(self, credential: dict) -> None: ...

    @abstractmethod
    def fetch_new_orders(self) -> list[Order]: ...

    @abstractmethod
    def mark_synced(self, order_ids: list[str]) -> None: ...


class ErpAdapter(ABC):
    """ERP 适配器：马帮 / 店小秘 / 积加 ..."""

    erp: str = ""

    @abstractmethod
    def login(self, credential: dict) -> None: ...

    @abstractmethod
    def push_orders(self, orders: list[Order]) -> dict: ...
