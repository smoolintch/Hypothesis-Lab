# 项目当前状态

## 1. 当前阶段
`阶段 0：文档冻结与工程底座`

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
10. `apps/web` 与 `services/api` 尚未初始化具体技术栈。

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
1. 初始化 `apps/web`
2. 初始化 `services/api`
3. 准备固定行情数据
4. 建立最小测试基线

当前已经可以进入“阶段 0B：工程底座”执行，不建议再回到契约骨架阶段反复摇摆。

## 5. 当前推荐的下一步
1. 用 `pnpm` 初始化根工作区与 `apps/web`
2. 用 `uv` 初始化 `services/api`
3. 在 `services/api` 中接入 `Alembic`
4. 补齐固定行情数据
5. 建立最小测试基线

## 6. 当前未决问题
1. 本地数据库采用容器方式还是本地安装方式，尚未最终记录
2. 固定行情样本的来源与导入脚本尚未落地
3. `apps/web` 与 `services/api` 的实际初始化命令尚未执行

## 7. 最近已完成事项
1. 项目顶层目录与模块子目录已建立
2. 各核心目录已补充说明文档
3. 文档体系已按开发前优先级拆分
4. 已建立项目级 `AGENTS.md`
5. Git 与 GitHub 版本管理已就绪
6. 已冻结 `domain-model`、`api-contracts`、`rule-template-schema-v1`、`user-flow-and-page-states`
7. 已统一阶段定义，明确当前进入“阶段 0B：工程底座”
8. 已补充 `.env.example` 与 `pnpm-workspace.yaml`
9. 已建立最小 CI 骨架 `repo-guardrails.yml`
10. 已补充第一批固定样例策略

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
