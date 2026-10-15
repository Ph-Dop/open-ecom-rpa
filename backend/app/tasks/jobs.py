"""Celery 任务执行闭环。

P2 阶段：
- 根据 task.flow 组装流程（目前先 mock，P4 接真实 adapter）
- 每一步写 step_log 到 TaskRun
- 状态流转：pending -> running -> success / failed
"""

from __future__ import annotations

import traceback
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Task, TaskRun, RunStatusEnum
from app.tasks.celery_app import celery_app


def _log(step_log: list[dict], step: str, status: str, detail: str = "") -> None:
    step_log.append(
        {
            "step": step,
            "status": status,
            "detail": detail,
            "ts": datetime.utcnow().isoformat(),
        }
    )


def _execute_flow(db: Session, task: Task, run: TaskRun) -> None:
    """根据 task.flow 跑一遍：Temu 抓单 → 马帮推送。"""
    flow = task.flow or {}
    source = flow.get("source", "temu")
    target = flow.get("target", "mabang")

    step_log: list[dict] = []
    orders: list = []

    # Step 1: 拉取新订单（真实 Adapter）
    _log(step_log, "fetch_orders", "running", f"platform={source}")
    if source == "temu":
        from app.adapters.platforms.temu import TemuAdapter

        try:
            adapter = TemuAdapter()
            orders = adapter.fetch_new_orders()
            _log(step_log, "fetch_orders", "ok", f"got {len(orders)} orders")
        except Exception as e:  # noqa: BLE001
            _log(step_log, "fetch_orders", "failed", f"CDP 未连接或浏览器未启动: {e!s}")
            raise
    else:
        _log(step_log, "fetch_orders", "ok", f"platform={source} (mock, no adapter yet)")

    # Step 2: 推送到 ERP
    _log(step_log, "push_to_erp", "running", f"erp={target}")
    if target == "mabang":
        from app.adapters.erps.mabang import MabangAdapter

        erp = MabangAdapter()
        result = erp.push_orders(orders)
        _log(step_log, "push_to_erp", "ok", f"pushed {result['pushed']} orders ({result['message']})")
    else:
        pushed = len(orders)
        _log(step_log, "push_to_erp", "ok", f"pushed {pushed} orders (mock, no erp adapter)")

    run.step_log = step_log


def run_task_sync(task_id: str) -> dict:
    """同步执行任务，供 API 直接调用 / Celery eager 模式复用。"""
    db: Session = SessionLocal()
    run: TaskRun | None = None
    try:
        task = db.get(Task, task_id)
        if not task:
            raise ValueError(f"task {task_id} not found")

        run = TaskRun(task_id=task_id, status=RunStatusEnum.running, started_at=datetime.utcnow())
        db.add(run)
        db.commit()
        db.refresh(run)

        _execute_flow(db, task, run)

        run.status = RunStatusEnum.success
        run.finished_at = datetime.utcnow()
        db.commit()
        return {"run_id": run.id, "status": run.status}
    except Exception as e:  # noqa: BLE001
        if run:
            run.status = RunStatusEnum.failed
            run.error = f"{e}\n{traceback.format_exc()}"
            run.finished_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task
def run_task(task_id: str) -> dict:
    return run_task_sync(task_id)
