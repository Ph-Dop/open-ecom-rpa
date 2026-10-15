from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models import Task, TaskRun, TaskStatusEnum
from app.schemas.task import TaskCreate, TaskOut, TaskRunOut, TaskUpdate
from app.tasks.jobs import run_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(db_session)):
    return db.query(Task).order_by(Task.created_at.desc()).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(db_session)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, db: Session = Depends(db_session)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(db_session)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(db_session)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    task.status = TaskStatusEnum.disabled
    db.commit()


@router.post("/{task_id}/run", response_model=TaskRunOut)
def trigger_run(task_id: str, db: Session = Depends(db_session)):
    """立即触发一次任务执行。开发模式（eager）下同步返回结果。"""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    # eager 模式下会同步执行并落库；生产模式下返回 async result
    result = run_task.delay(task_id)

    # eager 模式直接拿返回值；生产模式下查最新一条 run
    from app.models import RunStatusEnum  # noqa: F401

    run = (
        db.query(TaskRun)
        .filter(TaskRun.task_id == task_id)
        .order_by(TaskRun.created_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(status_code=500, detail="run not created")
    return run


@router.get("/{task_id}/runs", response_model=list[TaskRunOut])
def list_runs(task_id: str, db: Session = Depends(db_session)):
    return (
        db.query(TaskRun)
        .filter(TaskRun.task_id == task_id)
        .order_by(TaskRun.created_at.desc())
        .all()
    )
