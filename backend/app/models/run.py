import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RunStatusEnum(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


def _uuid() -> str:
    return str(uuid.uuid4())


class TaskRun(Base):
    """任务的一次执行实例"""

    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False)

    status: Mapped[str] = mapped_column(
        Enum(RunStatusEnum, native_enum=False, length=16),
        default=RunStatusEnum.pending,
        index=True,
    )

    # 重试次数
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # 每步执行的结构化日志：[{"step": "login", "status": "ok", "ts": ...}, ...]
    step_log: Mapped[list] = mapped_column(JSON, default=list)

    error: Mapped[str] = mapped_column(Text, default="")

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
