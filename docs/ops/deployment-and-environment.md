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

## 5. 数据库与迁移约定
1. 业务主库统一使用 `PostgreSQL`。
2. 表结构变更统一通过 `Alembic` 管理。
3. 不允许把“手动在本地执行一次 SQL”当作长期迁移方案。
4. 在 `services/api` 初始化后，应补充：
   - `Alembic` 配置位置
   - 首次建库方式
   - 本地迁移命令

## 6. 本地启动约定
当前只冻结启动方式，不冻结最终命令：
1. 前端通过 `pnpm` 启动。
2. 后端通过 `uv run` 启动。
3. 数据库需要先于 API 启动。
4. 行情样本数据准备完成后，API 和回测引擎才能进入集成调试。

说明：具体启动命令应在初始化 `apps/web` 与 `services/api` 后补齐。

## 7. 测试环境说明
1. 单元测试和集成测试优先在本地执行。
2. 核心闭环 E2E 使用 `Playwright`。
3. 固定样例策略与固定行情数据将作为回归基线。

## 8. 仍待补齐的内容
1. 前端实际启动命令
2. 后端实际启动命令
3. 数据库容器或本地安装方案
4. 最小 CI 工作流
5. 试运行环境部署步骤
6. 日志、监控、备份方案
