from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "open_ecom_rpa",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    # 开发模式同步执行
    task_always_eager=settings.celery_always_eager,
    task_eager_propagates=True,
)
