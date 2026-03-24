# 项目当前状态

## 1. 当前阶段
`阶段 0：文档冻结与工程底座`

## 2. 当前总体情况
1. 产品定义与 MVP 功能清单已完成。
2. `MVP开发计划.md` 已完成，作为总纲存在。
3. 项目目录骨架已建立。
4. 文档体系已建立，包括架构、契约、项目、验收、协作、ADR、部署等目录。
5. `apps/web` 与 `services/api` 尚未初始化具体技术栈。
6. `domain-model` 与 `api-contracts` 仍是第一版骨架，尚未细化到可直接编码的程度。

## 3. 当前已冻结或基本确定的事项
1. 架构方向：模块化单体
2. 前端建议：`Next.js + React + TypeScript`
3. 后端建议：`FastAPI`
4. 回测引擎建议：Python 独立领域模块
5. 数据库建议：`PostgreSQL`
6. MVP 核心范围：策略假设卡、回测、结果、结论、交易手册

## 4. 当前最优先任务
1. 细化 `docs/contracts/domain-model.md`
2. 细化 `docs/contracts/api-contracts.md`
3. 补齐 `docs/product/user-flow-and-page-states.md` 的主流程与关键状态

只有这三项到达可执行级别后，才建议正式初始化前后端工程并开始主链路开发。

## 5. 当前推荐的下一步
1. 冻结核心对象字段类型、枚举值和对象关系
2. 冻结主链路 API 的请求响应 schema
3. 明确回测同步/异步返回策略
4. 再初始化 `apps/web`
5. 再初始化 `services/api`

## 6. 当前未决问题
1. 前端状态管理方案未定
2. Python 包管理方案未定
3. 数据迁移工具未定
4. 单用户模式与最简账号体系尚未最终拍板

## 7. 最近已完成事项
1. 项目顶层目录与模块子目录已建立
2. 各核心目录已补充说明文档
3. 文档体系已按开发前优先级拆分
4. 已建立项目级 `AGENTS.md`

## 8. 开工前必读文档
1. `AGENTS.md`
2. `docs/MVP开发计划.md`
3. `docs/architecture/technical-solution-and-constraints.md`
4. `docs/architecture/system-architecture-and-module-boundaries.md`
5. `docs/contracts/domain-model.md`
6. `docs/contracts/api-contracts.md`
7. `docs/project/task-breakdown-and-development-order.md`
8. `docs/acceptance/acceptance-criteria-and-test-checklist.md`

## 9. 更新规则
遇到以下情况，必须更新本文件：

1. 当前阶段变化
2. 最优先任务变化
3. 关键决策冻结
4. 关键阻塞点出现或解除
5. 主链路能力完成一个里程碑

## 10. 最后一条原则
如果聊天上下文和本文件冲突，以本文件为准，再结合代码现状校验。
