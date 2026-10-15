"""oerc 命令行工具。

用法：
    python -m app.cli list
    python -m app.cli run <task_id>
    python -m app.cli health
"""

from __future__ import annotations

import sys

import typer
from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.models import Task, TaskRun
from app.tasks.jobs import run_task_sync

app = typer.Typer(help="OpenEcom-RPA 命令行")


@app.command()
def list() -> None:
    """列出所有任务。"""
    init_db()
    db = SessionLocal()
    tasks = db.execute(select(Task).order_by(Task.created_at.desc())).scalars().all()
    if not tasks:
        typer.echo("(no tasks)")
        return
    for t in tasks:
        typer.echo(f"{t.id}  [{t.status:8}]  {t.name}  (cron={t.cron or '-'})")
    db.close()


@app.command()
def run(task_id: str) -> None:
    """立即触发一次任务。"""
    init_db()
    try:
        result = run_task_sync(task_id)
        typer.echo(f"ok: {result}")
    except Exception as e:  # noqa: BLE001
        typer.echo(f"failed: {e}", err=True)
        sys.exit(1)


@app.command()
def runs(task_id: str, limit: int = 10) -> None:
    """查看任务最近的运行记录。"""
    init_db()
    db = SessionLocal()
    rows = (
        db.query(TaskRun)
        .filter(TaskRun.task_id == task_id)
        .order_by(TaskRun.created_at.desc())
        .limit(limit)
        .all()
    )
    for r in rows:
        typer.echo(f"{r.created_at:%Y-%m-%d %H:%M}  {r.status:8}  steps={len(r.step_log)}  {r.error[:80]}")
    db.close()


@app.command()
def health() -> None:
    """检查数据库连接。"""
    init_db()
    db = SessionLocal()
    from sqlalchemy import text

    db.execute(text("SELECT 1"))
    typer.echo("db: ok")
    db.close()


if __name__ == "__main__":
    app()
