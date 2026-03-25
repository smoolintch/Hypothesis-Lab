# 部署与环境文档

## 1. 目标
本文件用于记录开发环境、测试环境、部署方式和运行依赖。

## 2. 当前状态
当前已冻结以下基础约定：
1. 仓库已完成 Git 初始化并连接远程仓库。
2. 前端包管理采用 `pnpm`。
3. Python 包管理采用 `uv`。
4. 数据库采用 `PostgreSQL`。
5. 数据迁移采用 `Alembic`。
6. MVP 运行在单用户模式。

## 3. 本地开发环境基线
| 项目 | 当前约定 |
| --- | --- |
| Node 工作区 | `pnpm-workspace.yaml` |
| Python 运行方式 | `uv run ...` |
| 数据库 | 本地 `PostgreSQL` |
| 环境变量模板 | 根目录 `.env.example` |
| API 基地址 | `http://localhost:8000/api` |

## 4. 环境变量清单
当前统一维护在根目录 `.env.example`，最低要求如下：
1. `APP_ENV`
2. `LOG_LEVEL`
3. `APP_USER_MODE`
4. `DEFAULT_USER_ID`
5. `NEXT_PUBLIC_API_BASE_URL`
6. `API_HOST`
7. `API_PORT`
8. `DATABASE_URL`
9. `MARKET_DATA_DIR`
10. `BACKTEST_DATASET_VERSION`

补充说明：
1. `DATABASE_URL` 采用 SQLAlchemy URL 格式，当前推荐写法为 `postgresql+psycopg://hypothesis:hypothesis@localhost:5432/hypothesis_lab`。
2. `services/api` 启动时优先读取根目录 `.env`；若本地尚未创建 `.env`，会回退读取 `.env.example` 作为默认开发配置。

## 5. 数据库与迁移约定
1. 业务主库统一使用 `PostgreSQL`。
2. 表结构变更统一通过 `Alembic` 管理。
3. 不允许把“手动在本地执行一次 SQL”当作长期迁移方案。
4. 当前 `Alembic` 配置入口位于 `services/api/alembic.ini`。
5. 迁移脚本目录位于 `services/api/alembic/versions`。
6. 本地执行迁移命令前，需先确保 `DATABASE_URL` 指向的 PostgreSQL 已启动并可连接。
7. 当前最小迁移命令如下：
   - 在 `services/api` 目录执行 `uv run alembic current`
   - 在 `services/api` 目录执行 `uv run alembic revision -m "init"`
   - 在 `services/api` 目录执行 `uv run alembic upgrade head`

## 6. 本地启动约定
当前约定如下：
1. 前端通过 `pnpm` 启动。
2. 后端通过 `uv run` 启动。
3. 数据库需要先于 API 启动。
4. 行情样本数据准备完成后，API 和回测引擎才能进入集成调试。

当前已落地并验证通过的前端最小启动命令：
1. 在仓库根目录安装依赖：`corepack pnpm install`
2. 启动前端开发服务器：`npm run dev`
3. 单独执行前端 lint：`corepack pnpm --filter @hypothesis-lab/web lint`
4. 单独执行前端类型检查：`corepack pnpm --filter @hypothesis-lab/web typecheck`
5. 单独执行前端生产构建：`corepack pnpm --filter @hypothesis-lab/web build`

说明：
1. 根目录已补充最小 `package.json` 作为 `pnpm` workspace root。
2. `apps/web` 已按 `Next.js + React + TypeScript` 初始化为 App Router + `src/` 目录模式。
3. 根目录脚本内部通过 `corepack pnpm` 转发到工作区包，避免在 `lab` 环境下找不到 `pnpm` 可执行文件。
4. `services/api` 已按 `FastAPI + uv + Alembic` 初始化最小工程骨架。
5. 当前后端最小启动命令：
   - 在 `services/api` 目录执行 `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
   - 或在 `services/api` 目录执行 `uv run python -m app`
6. 当前后端仅保留 FastAPI 默认 `docs/openapi/redoc` 能力，未新增任何自定义健康检查或业务接口。

## 7. 测试环境说明
1. 单元测试和集成测试优先在本地执行。
2. 核心闭环 E2E 使用 `Playwright`。
3. 固定样例策略与固定行情数据将作为回归基线。

## 8. 仍待补齐的内容
1. 数据库容器或本地安装方案
2. 最小 CI 工作流
3. 试运行环境部署步骤
4. 日志、监控、备份方案
5. 首个真实业务迁移版本与建表脚本
