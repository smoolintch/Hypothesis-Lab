# Hypothesis Lab

当前仓库已完成第一版项目骨架初始化，目标是围绕 MVP 核心闭环逐步开发：

`交易想法 -> 策略假设卡 -> 一键回测 -> 结果理解 -> 结论沉淀 -> 交易手册`

## 目录结构

```text
/apps
  /web
/services
  /api
/packages
  /domain-contracts
  /backtest-engine
  /rule-templates
  /shared-utils
/tests
  /integration
  /e2e
/docs
```

## 模块职责

- `apps/web`: 前端应用，负责页面、交互和用户体验。
- `services/api`: 主后端 API 与应用编排，负责业务流程、持久化和接口输出。
- `packages/domain-contracts`: 核心领域模型、接口契约和共享 schema。
- `packages/backtest-engine`: 回测执行与结果计算逻辑。
- `packages/rule-templates`: 模板化交易规则定义、参数校验和标准化转换。
- `packages/shared-utils`: 跨模块共享工具。
- `tests/integration`: 模块集成测试。
- `tests/e2e`: 核心闭环端到端测试。
- `docs`: 架构、契约、样例和验收文档。

## 当前状态

目前只完成目录骨架和说明文件，尚未初始化具体技术栈。

下一步建议优先做：

1. 冻结领域模型和接口契约。
2. 初始化 `apps/web` 与 `services/api`。
3. 定义回测输入输出 schema。
4. 建立第一批测试样例和固定数据集。
