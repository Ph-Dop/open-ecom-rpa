"""Adapter 接口骨架测试：不依赖浏览器，只验证类结构。"""

from app.adapters.base import EcomPlatformAdapter, ErpAdapter
from app.adapters.erps.mabang import MabangAdapter
from app.adapters.platforms.temu import TemuAdapter


def test_adapter_interfaces():
    assert issubclass(TemuAdapter, EcomPlatformAdapter)
    assert issubclass(MabangAdapter, ErpAdapter)
    assert TemuAdapter.platform == "temu"
    assert MabangAdapter.erp == "mabang"


def test_mabang_mock_push():
    erp = MabangAdapter()
    result = erp.push_orders([])
    assert result["pushed"] == 0
    assert "mock" in result["message"]
