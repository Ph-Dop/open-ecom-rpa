"""简易 cron 调度器：FastAPI 启动时跑一个后台协程。

每分钟扫一次 active 且配置了 cron 的 task，到点就触发 run_task_sync。
不依赖 Redis / Celery beat，适合开发和小规模部署。
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from croniter import croniter

from app.core.database import SessionLocal
from app.models import Task, TaskStatusEnum
from app.tasks.jobs import run_task_sync

logger = logging.getLogger("scheduler")

# 内存里记录每个 task 上次触发时间，避免 1 分钟内重复触发
_last_fired: dict[str, datetime] = {}


def _due(t: Task) -> bool:
    if not t.cron:
        return False
    try:
        base = _last_fired.get(t.id, t.created_at)
        itr = croniter(t.cron, base)
        next_time = itr.get_next(datetime)
        return next_time <= datetime.utcnow()
    except Exception:  # noqa: BLE001
        return False


async def scheduler_loop() -> None:
    while True:
        try:
            db = SessionLocal()
            tasks = (
                db.query(Task)
                .filter(Task.status == TaskStatusEnum.active)
                .filter(Task.cron != "")
                .all()
            )
            for t in tasks:
                if _due(t):
                    logger.info("auto trigger task %s (%s)", t.id, t.name)
                    # 同步执行放到线程池，不阻塞事件循环
                    await asyncio.to_thread(run_task_sync, t.id)
                    _last_fired[t.id] = datetime.utcnow()
            db.close()
        except Exception:  # noqa: BLE001
            logger.exception("scheduler tick failed")
        await asyncio.sleep(60)


_scheduler_task: asyncio.Task | None = None


def start_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task is None:
        _scheduler_task = asyncio.create_task(scheduler_loop())


def stop_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        _scheduler_task = None
