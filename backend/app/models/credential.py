import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlatformTypeEnum(str, enum.Enum):
    # 卖家平台
    temu = "temu"
    shopee = "shopee"
    amazon = "amazon"
    # ERP
    mabang = "mabang"
    dianxiaomi = "dianxiaomi"
    jijia = "jijia"


def _uuid() -> str:
    return str(uuid.uuid4())


class Credential(Base):
    """各平台账号凭据（P1 阶段再加密）"""

    __tablename__ = "credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    platform: Mapped[str] = mapped_column(
        Enum(PlatformTypeEnum, native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    account_name: Mapped[str] = mapped_column(String(128), nullable=False)

    # {"username": "...", "password": "...", "cookie": "..."}
    secret: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
