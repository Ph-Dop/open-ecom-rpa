from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    name: str = Field(..., max_length=128)
    description: str = ""
    flow: dict = Field(default_factory=dict)
    cron: str = ""


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    flow: dict | None = None
    cron: str | None = None
    status: str | None = None


class TaskOut(TaskBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskRunOut(BaseModel):
    id: str
    task_id: str
    status: str
    retry_count: int
    step_log: list
    error: str
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
