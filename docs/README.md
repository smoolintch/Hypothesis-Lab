# docs

文档目录用于把产品约束、技术边界、开发顺序和验收标准沉淀为长期可维护资产，避免关键信息只停留在 `MVP开发计划.md` 或聊天记录中。

## 当前文档体系

```text
architecture/             技术方案、架构设计、模块边界
contracts/                领域模型、接口契约
product/                  用户流程、页面状态
project/                  任务拆解、开发顺序
acceptance/               验收标准、测试清单
collaboration/            AI 协作规则
adr/                      技术决策记录
ops/                      部署与环境
samples/                  样例策略、样例数据、回归样例
```

## 当前优先级

### P0：正式开发前必须明确
1. `architecture/technical-solution-and-constraints.md`
2. `architecture/system-architecture-and-module-boundaries.md`
3. `contracts/domain-model.md`
4. `contracts/api-contracts.md`
5. `project/current-status.md`
6. `project/task-breakdown-and-development-order.md`
7. `acceptance/acceptance-criteria-and-test-checklist.md`
8. `collaboration/ai-collaboration-rules.md`

### P1：现在先写骨架，开发中持续补全
1. `product/user-flow-and-page-states.md`
2. `project/session-handoff.md`
3. `adr/ADR-0001-template.md`
4. `ops/deployment-and-environment.md`

### P2：随着实现逐步充实
1. `samples/` 下的固定样例策略
2. 回归样例数据
3. 试运行和上线后的运维记录

## 使用约定

1. `MVP开发计划.md` 是总纲，不直接承担所有细节文档职责。
2. 任何跨模块改动，优先更新 `contracts/` 与 `architecture/`。
3. 任何影响开发顺序或范围的变化，优先更新 `project/` 与 `acceptance/`。
4. 任何关键技术取舍，记录到 `adr/`。
5. `project/current-status.md` 是判断项目当前状态的唯一总入口。
6. `project/session-handoff.md` 用于处理中断、上下文丢失和任务交接。
