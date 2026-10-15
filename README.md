# OpenEcom-RPA

统一跨境电商**卖家平台**与 **ERP 系统**的自动化中台。

> MVP 闭环：从 Temu 卖家后台抓取新订单 → 自动同步到马帮 ERP → 状态回写。

## 设计目标

- **Adapter 抽象**：平台侧（`EcomPlatformAdapter`）和 ERP 侧（`ErpAdapter`）各自独立，新增平台不改核心
- **任务可编排**：DAG 定义、定时触发、失败重试、步骤日志落库
- **可观测**：每次运行的每一步都有结构化日志，可在控制台回看
- **自托管**：Docker Compose 一键起；开发模式零依赖（SQLite + Celery eager）

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic v2 |
| 任务队列 | Celery + Redis（开发模式 eager 同步跑，无需 Redis） |
| 数据库 | PostgreSQL 16（开发默认 SQLite） |
| 浏览器自动化 | Playwright（CDP 接管已登录浏览器） |
| 前端 | 单文件 Vue3 + Element Plus（CDN，FastAPI 托管） |

## 快速启动（开发模式，零外部依赖）

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium
.\.venv\Scripts\uvicorn app.main:app --reload
```

访问：
- 控制台：http://localhost:8000/
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 跑测试

```bash
cd backend
.\.venv\Scripts\pytest tests/ -v
```

## 接入真实 Temu（CDP 模式）

1. 关闭所有 Edge 窗口
2. 用调试模式启动 Edge：
   ```powershell
   & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
     --remote-debugging-port=9222 `
     "https://seller.kuajingmaihuo.com/"
   ```
3. 在 Edge 里手动登录 Temu 卖家后台
4. 触发任务：`POST /tasks/{id}/run`，TemuAdapter 会自动接管这个浏览器抓数据

## 目录结构

```
open-ecom-rpa/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI 路由：/health、/tasks
│   │   ├── core/               # 配置、DB 引擎
│   │   ├── models/             # Task / TaskRun / Credential
│   │   ├── schemas/            # Pydantic
│   │   ├── adapters/
│   │   │   ├── base.py        # EcomPlatformAdapter / ErpAdapter 抽象
│   │   │   ├── platforms/temu.py
│   │   │   └── erps/mabang.py
│   │   ├── browser/pool.py     # 浏览器池（storage_state 持久化）
│   │   └── tasks/jobs.py       # run_task 闭环
│   ├── static/index.html      # Vue3 控制台
│   ├── scripts/               # 登录、冒烟、抓单脚本
│   └── tests/
└── deploy/                     # Dockerfile / docker-compose
```

## 新增一个平台/ERP 要做什么

1. 在 `adapters/platforms/` 或 `adapters/erps/` 新建一个文件
2. 继承对应抽象类，实现 `login()` / `fetch_new_orders()` 或 `push_orders()`
3. 在 `tasks/jobs.py` 里加一个 `if source == "xxx"` 分支

**核心调度代码不用改。**

## Roadmap

- [x] P0 项目骨架 + FastAPI + DB 模型
- [x] P1 Playwright 封装 + 浏览器池
- [x] P2 Celery 任务闭环 + 步骤日志
- [x] P3 Vue3 控制台
- [x] P4 Temu 真实 Adapter（CDP 模式）
- [x] P5 马帮 Adapter 骨架 + 单元测试 + README
- [ ] P6 GitHub Actions + 马帮真实接入 + 定时调度（cron）
