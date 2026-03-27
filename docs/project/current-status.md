# 项目当前状态

## 1. 当前阶段
`阶段 1：策略输入链路（阶段 0 已正式完成）`

## 2. 当前总体情况
1. 产品定义与 MVP 功能清单已完成。
2. `MVP开发计划.md` 已完成，作为总纲存在。
3. 项目目录骨架已建立。
4. 文档体系已建立，包括架构、契约、项目、验收、协作、ADR、部署等目录。
5. Git 仓库已初始化，并已连接 GitHub 远程仓库。
6. `domain-model`、`api-contracts`、`rule-template-schema-v1`、`user-flow-and-page-states` 已补到可执行级别。
7. 根目录已补充 `pnpm-workspace.yaml` 与 `.env.example`。
8. 已建立最小 CI 骨架 `repo-guardrails.yml`。
9. 已补充第一批固定样例策略。
10. `apps/web` 已完成最小前端技术栈初始化。
11. `services/api` 已完成最小后端技术栈初始化：`FastAPI + uv + Alembic` 工程骨架已落地。
12. 固定行情样本目录规范、CSV/manifest 格式、版本规则和最小校验脚本已落地。
13. 仓库级最小测试基线与最小 CI 护栏已落地：可执行仓库护栏检查与 API 基础 smoke test。
14. 阶段 0 所需的文档冻结与工程底座目标已完成，当前优先级已切换到阶段 1 的起步任务。
15. `services/api` 已落地 `StrategyCard` 最小后端闭环：持久化模型、迁移、`POST/GET/PUT` 接口与基础校验已可用。
16. `apps/web` 已落地 `StrategyCard` 最小前端闭环：`/strategy-cards/new`、`/strategy-cards/{id}/edit`、规则模板驱动表单、真实 API 新建/读取/更新、保存后跳转与编辑回填已可用。
17. `services/api` 已落地「发起回测」占位后端链路：`StrategySnapshot`（含 `normalized_config`、按策略卡递增 `version`）、`BacktestRun`（`run_id`、关联快照、初始 `status=queued`）、`POST /api/strategy-cards/{id}/backtests`（`202`）与 `GET /api/backtests/{run_id}`；不执行真实回测、不落地 `BacktestResult`。
18. `apps/web` 已接入「发起回测 → 结果页占位」主链路：编辑页 `发起回测`（未保存时先校验并保存）、`POST /api/strategy-cards/{id}/backtests` 成功后跳转 `/backtests/{run_id}`，结果页用 `GET /api/backtests/{run_id}` 展示真实 `run_id` 与 `status`（占位文案，不伪造结果指标）。

## 3. 当前已冻结或基本确定的事项
1. 架构方向：模块化单体
2. 前端建议：`Next.js + React + TypeScript`
3. 后端建议：`FastAPI`
4. 回测引擎建议：Python 独立领域模块
5. 数据库建议：`PostgreSQL`
6. 前端包管理：`pnpm`
7. Python 包管理：`uv`
8. 数据迁移工具：`Alembic`
9. MVP 运行模式：单用户模式，保留 `user_id`
10. 回测接口策略：轻量异步 + `run_id` 轮询
11. MVP 核心范围：策略假设卡、回测、结果、结论、交易手册

## 4. 当前最优先任务
1. 在不引入列表接口的前提下继续推进阶段 1 后续页面
2. 衔接下一段主链路：真实回测执行与结果页消费
3. 持续维护 `StrategyCard` 与回测占位链路的自动化基线稳定性并纳入验收执行

阶段 0 已正式收尾，当前最优先工作应围绕“阶段 1：策略输入链路”的首批闭环任务推进。

## 5. 当前推荐的下一步
1. 保持不依赖 `GET /api/strategy-cards` 列表接口的推进方式，暂不扩展首页完整列表
2. 将 `test:e2e:strategy-card` 与 `tests/e2e/core-flow/backtest-placeholder.spec.ts` 纳入验收环境固定检查项
3. 衔接下一阶段：真实回测执行与 `GET /api/backtests/{run_id}/result` 消费（契约已预留，非本轮范围）
4. 保持固定行情样本与回测链路准备状态，暂不扩展阶段 1 之外的基础设施

## 6. 当前未决问题
1. 本地数据库采用容器方式还是本地安装方式，尚未最终记录
2. 真实市场数据来源尚未冻结；当前仅提供仓库内固定样本 `fixture`
3. 本地 PostgreSQL 是否已启动，取决于各开发环境；当前已完成首个 `StrategyCard` 业务迁移，但未在本机 PostgreSQL 上做真实连库验证

## 7. 最近已完成事项
1. 项目顶层目录与模块子目录已建立
2. 各核心目录已补充说明文档
3. 文档体系已按开发前优先级拆分
4. 已建立项目级 `AGENTS.md`
5. Git 与 GitHub 版本管理已就绪
6. 已冻结 `domain-model`、`api-contracts`、`rule-template-schema-v1`、`user-flow-and-page-states`
7. 已统一阶段定义，明确阶段 0 已正式完成，当前优先级转入“阶段 1：策略输入链路”
8. 已补充 `.env.example` 与 `pnpm-workspace.yaml`
9. 已建立最小 CI 骨架 `repo-guardrails.yml`
10. 已补充第一批固定样例策略
11. 已补充根级 `package.json`，形成最小 `pnpm` workspace root
12. 已初始化 `apps/web` 最小 Next.js App Router + TypeScript 骨架
13. 已安装前端基础依赖：`react-hook-form`、`zod`、`@hookform/resolvers`、`@tanstack/react-query`
14. `apps/web` 已通过 `lint`、`typecheck`、`build` 验证
15. 已初始化 `services/api` 最小 `FastAPI + uv + Alembic` 工程骨架
16. `services/api` 已建立 `app/api`、`app/application`、`app/domain`、`app/infrastructure`、`app/schemas` 分层目录
17. `services/api` 已接入基础配置加载与 Alembic 骨架
18. `services/api` 已验证应用可启动且当前不包含任何自定义业务接口
19. 已建立 `data/market/<source>/<symbol>/<timeframe>/<version>` 固定行情样本目录规范
20. 已提供 `BTCUSDT`、`ETHUSDT` 的 `4H`、`1D` 小体积 CSV 样本与 `manifest.json`
21. 已补充固定样本版本规则、导入约定与最小校验规则文档
22. 已新增 `scripts/market-data/validate_market_data.py` 并验证 4 组固定样本通过校验
23. 已补充仓库根最小测试入口 `npm run test`
24. 已为 `services/api` 接入 `pytest` 基线与最小 smoke test
25. 已在 `tests/integration`、`tests/e2e` 下建立清晰的测试基线结构
26. 已把 `.github/workflows/repo-guardrails.yml` 扩展为可运行的最小工作流，覆盖仓库护栏检查与 API smoke baseline
27. 阶段 0 所需的文档冻结、工程骨架、固定样本与最小测试基线已齐备，本次收尾后进入阶段 1
28. 已在 `services/api` 中落地 `StrategyCard` 持久化模型、仓储、服务与 `POST/GET/PUT` 最小接口
29. 已为 `StrategyCard` 接入基础字段校验、模板键位置校验和模板参数校验
30. 已通过 SQLite 临时库验证 `StrategyCard` 的创建、读取、更新与回填链路
31. 已通过 SQLite 临时库验证 `Alembic upgrade head` 可执行到首个 `StrategyCard` 迁移版本
32. 已在 `apps/web` 中接入 `StrategyCard` 请求层、React Query 查询/更新封装与规则模板表单 schema
33. 已实现 `/strategy-cards/new` 与 `/strategy-cards/{id}/edit` 两个页面路由及真实 API 对接
34. 已在 `apps/web` 中实现规则模板驱动的动态表单区块，并在模板切换时清理旧参数
35. 已通过浏览器验证“新建 -> 保存 -> 跳转编辑 -> 再次加载 -> 回填 -> 更新保存”最小前端闭环
36. 已在本机补齐 Playwright Chromium 依赖并跑通 `test:e2e:strategy-card`（3/3 通过）
37. 已将 `api-smoke` 基线断言更新为匹配当前公开的 `StrategyCard` OpenAPI 路由，恢复最小 CI 基线通过状态
38. 已在 `services/api` 落地 `StrategySnapshot`、`BacktestRun` 持久化模型与第二版 Alembic 迁移（`strategy_snapshots`、`backtest_runs`、策略卡 `latest_backtest_run_id`）
39. 已实现从 `StrategyCard` 生成不可变快照与 `normalized_config`、同一策略卡多次发起回测时 `version` 递增
40. 已通过 SQLite 临时库验证 `POST /api/strategy-cards/{id}/backtests` 与 `GET /api/backtests/{run_id}`；集成测试 `tests/integration/test_backtests_placeholder.py` 覆盖快照与 run 关联、latest 更新与 404
41. 已为 `StrategySnapshot(strategy_card_id, version)` 唯一约束冲突补齐保守处理：发起回测时若遇到版本冲突，会回滚当前事务并重试生成下一版 `version`，不再直接暴露为 `500`
42. 已在 `apps/web` 落地编辑页「发起回测」、占位结果页 `/backtests/{run_id}` 及真实 API 对接（`POST` 创建 run、`GET` 展示状态；`queued`/`running` 轻量轮询）
43. 已新增并跑通 `tests/e2e/core-flow/backtest-placeholder.spec.ts`，独立验证“发起回测 -> 跳转结果页占位”主链路与不存在 `run_id` 的错误态

## 8. 开工前必读文档
1. `AGENTS.md`
2. `docs/MVP开发计划.md`
3. `docs/architecture/technical-solution-and-constraints.md`
4. `docs/architecture/system-architecture-and-module-boundaries.md`
5. `docs/contracts/domain-model.md`
6. `docs/contracts/api-contracts.md`
7. `docs/contracts/rule-template-schema-v1.md`
8. `docs/product/user-flow-and-page-states.md`
9. `docs/project/task-breakdown-and-development-order.md`
10. `docs/acceptance/acceptance-criteria-and-test-checklist.md`
11. `docs/adr/ADR-0001-mvp-engineering-conventions.md`

## 9. 更新规则
遇到以下情况，必须更新本文件：

1. 当前阶段变化
2. 最优先任务变化
3. 关键决策冻结
4. 关键阻塞点出现或解除
5. 主链路能力完成一个里程碑

## 10. 最后一条原则
如果聊天上下文和本文件冲突，以本文件为准，再结合代码现状校验。
