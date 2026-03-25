# api

主后端目录，负责应用编排、接口输出、数据持久化和与回测引擎协作。

当前已初始化最小工程底座，技术栈固定为 `FastAPI + uv + Alembic`，但尚未实现任何业务接口。

## 当前目录结构

```text
app/
  api/                    HTTP 接口层
  application/            用例编排与流程控制
  domain/                 领域对象与业务规则
  infrastructure/
    config/               配置加载
    database/             SQLAlchemy 基础定义
  schemas/                请求响应模型与内部 DTO
alembic/                  Alembic 迁移骨架
alembic.ini               Alembic 入口配置
pyproject.toml            uv 工程定义
uv.lock                   uv 依赖锁文件
```

## 分层职责

- `app/api`: 只负责 FastAPI 路由组织与 HTTP 入口。
- `app/application`: 承载用例编排与流程串联。
- `app/domain`: 承载领域模型与业务规则。
- `app/infrastructure/config`: 统一环境变量与配置加载。
- `app/infrastructure/database`: 统一数据库基类、引擎和会话工厂。
- `app/schemas`: 承载 API schema 与跨层 DTO。

## 当前已落地内容

1. `uv` 工程初始化与依赖锁定
2. 最小 FastAPI 应用入口 `app.main:app`
3. 基础配置加载，优先读取根目录 `.env`，缺失时回退到 `.env.example`
4. `Alembic` 初始化与数据库 URL 接线

## 当前刻意未做的内容

1. 不实现任何业务接口
2. 不新增 `/health`、`/ping`、`/ready` 等自定义路由
3. 不引入认证、多用户、任务队列、缓存、中间件体系

## 本地运行

在 `services/api` 目录下执行：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或：

```bash
uv run python -m app
```

## Alembic 常用命令

在 `services/api` 目录下执行：

```bash
uv run alembic current
uv run alembic revision -m "init"
uv run alembic upgrade head
```
