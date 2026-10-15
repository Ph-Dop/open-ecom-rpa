import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    disabled = "disabled"


def _uuid() -> str:
    return str(uuid.uuid4())


class Task(Base):
    """编排后的自动化任务定义（DAG）"""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    # 例如 {"source": "temu", "target": "mabang", "steps": [...]}
    flow: Mapped[dict] = mapped_column(JSON, default=dict)

    status: Mapped[str] = mapped_column(
        Enum(TaskStatusEnum, native_enum=False, length=16),
        default=TaskStatusEnum.active,
    )

    # cron 表达式，空表示手动触发
    cron: Mapped[str] = mapped_column(String(64), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
