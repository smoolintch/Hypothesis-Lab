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
3. `MARKET_DATA_DIR` 当前默认指向 `./data/market`，用于定位仓库内固定行情样本根目录。
4. `BACKTEST_DATASET_VERSION` 当前默认值为 `sample-v1`，表示后续回测开发应优先绑定首批固定样本版本，而不是任意文件。

## 5. 固定行情样本约定
当前固定行情样本采用仓库内文件方案，不接第三方交易所 API，不引入额外数据基础设施。

目录结构固定为：

```text
data/market/<source>/<symbol>/<timeframe>/<version>/
  manifest.json
  candles.csv
```

当前 MVP 范围内的固定值：
1. `source` 固定样本统一使用 `fixture`。
2. `symbol` 只允许 `BTCUSDT`、`ETHUSDT`。
3. `timeframe` 只允许 `4H`、`1D`。
4. `version` 当前首个固定版本为 `sample-v1`。

文件格式约束：
1. `candles.csv` 表头固定为 `ts,open,high,low,close,volume`。
2. `ts` 使用 UTC `ISO 8601` 字符串。
3. 数据按时间升序排列，且不允许重复时间戳。
4. `manifest.json` 负责声明 `id`、`source`、`symbol`、`timeframe`、`version`、覆盖区间、K 线数量和数据文件位置。

## 6. 固定行情样本导入与校验
后续 API 或回测引擎接入固定样本时，建议遵循以下最小流程：

1. 从 `MARKET_DATA_DIR` 开始定位目标目录，例如 `data/market/fixture/BTCUSDT/4H/sample-v1`。
2. 先读取 `manifest.json`，确认 `symbol`、`timeframe`、`version`、`storage_uri` 与目录一致。
3. 再读取 `candles.csv`，校验表头、时间升序和行数。
4. 通过校验后，将 `manifest.version` 作为 `dataset_version` 进入后续回测结果快照。

当前建议的最小校验规则：
1. `manifest.json` 必填字段完整。
2. `manifest.storage_uri` 指向当前数据集目录下的 `candles.csv`。
3. `candles.csv` 仅包含 `ts,open,high,low,close,volume` 六列。
4. `candle_count` 与实际数据行数一致。
5. `coverage_start_at` 等于首行 `ts`。
6. `coverage_end_at` 等于最后一行 `ts + timeframe`。

当前可执行的本地校验命令约定为：
1. 在仓库根目录执行 `python scripts/market-data/validate_market_data.py`
2. 如只校验单个数据集，可执行 `python scripts/market-data/validate_market_data.py data/market/fixture/BTCUSDT/4H/sample-v1`

## 7. 数据库与迁移约定
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

## 8. 本地启动约定
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
6. 当前后端已落地首批业务接口：
   - `POST /api/strategy-cards`
   - `GET /api/strategy-cards/{id}`
   - `PUT /api/strategy-cards/{id}`
7. 当前后端仍未新增任何自定义健康检查接口。

## 9. 测试环境说明
1. 单元测试和集成测试优先在本地执行。
2. 核心闭环 E2E 使用 `Playwright`。
3. 固定样例策略与固定行情数据将作为回归基线。
4. 当前仓库已建立最小测试入口：在仓库根目录执行 `npm run test`。
5. 当前最小测试基线包含：
   - `npm run test:repo-guardrails`：验证仓库关键文件、样例策略和固定数据集 manifest 是否齐备
   - `npm run test:api-smoke`：验证 `services/api` 最小 FastAPI 应用可创建，且默认 `docs/openapi/redoc` 端点可访问
6. `services/api` 的测试依赖通过 `uv` 管理；如需单独执行 `StrategyCard` 最小链路测试，可在 `services/api` 目录执行 `uv run pytest tests/integration/test_strategy_cards_api.py`
7. 如需在无 PostgreSQL 的情况下验证迁移脚本，可在 `services/api` 目录执行 `DATABASE_URL=sqlite+pysqlite:///./strategy_cards_smoke.db uv run alembic upgrade head`
8. 当前 `.github/workflows/repo-guardrails.yml` 已覆盖仓库护栏检查和 API smoke baseline

## 10. 仍待补齐的内容
1. 数据库容器或本地安装方案
2. 完整 Playwright 套件与真实页面闭环 E2E
3. 试运行环境部署步骤
4. 日志、监控、备份方案
5. 更多业务迁移版本与真实 PostgreSQL 联调记录
