# ADR-0001 MVP 工程与运行约定

## 状态
Accepted

## 背景
项目即将从文档阶段进入正式开发阶段，但仍有若干工程级关键决策未冻结，包括前端包管理、Python 依赖管理、数据迁移方式、单用户模式处理方式，以及回测接口采用同步还是异步。

如果这些点不先定下来，后续在初始化工程和并行开发时会持续反复摇摆。

## 决策
1. 前端工作区使用 `pnpm`。
2. Python 依赖管理和运行命令使用 `uv`。
3. 数据库迁移统一使用 `Alembic`。
4. MVP 阶段采用单用户模式，但所有核心业务表都保留 `user_id`。
5. 回测接口采用“轻量异步 + 轮询”契约：创建回测后立即返回 `run_id`，前端轮询状态与结果。
6. 前端 MVP 阶段采用 `React Hook Form + Zod + TanStack Query + 组件局部状态`，暂不引入全局状态库。

## 备选方案
1. 前端使用 `npm` 或 `yarn`
2. Python 使用 `poetry` 或 `pip + venv`
3. 数据库迁移先手写 SQL
4. 回测直接同步阻塞请求
5. 前端先上 Zustand 或 Redux

## 决策原因
1. `pnpm` 更适合 monorepo，安装和依赖隔离都更清晰。
2. `uv` 对 Python 项目初始化、依赖安装和命令执行足够轻量，适合 MVP 快速推进。
3. `Alembic` 是 `FastAPI + PostgreSQL` 场景下最稳妥的迁移工具，不需要额外发明流程。
4. 保留 `user_id` 可以避免将来从单用户切多用户时推翻数据模型。
5. 异步回测契约能更自然地覆盖排队、运行中、失败和结果恢复场景，也更符合结果页状态设计。
6. 先不用全局状态库，可以降低前端结构复杂度，把注意力集中在表单、请求和结果展示上。

## 影响
1. 根目录和文档需要围绕 `pnpm`、`uv`、`Alembic` 建立工程基座。
2. `api-contracts` 和 `user-flow-and-page-states` 必须以 `run_id + polling` 为前提设计。
3. `domain-model` 必须明确单用户模式只是运行策略，不是数据模型简化。
4. 后续若改成消息队列或多用户登录，只需要在现有边界内扩展，不必推翻主契约。

## 后续动作
1. 更新 `docs/architecture/technical-solution-and-constraints.md`
2. 更新 `docs/contracts/domain-model.md`
3. 更新 `docs/contracts/api-contracts.md`
4. 更新 `docs/product/user-flow-and-page-states.md`
5. 补充 `.env.example`
