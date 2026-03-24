# domain-contracts

核心领域模型与跨模块共享契约目录。

这里应优先沉淀那些不会随着页面变化而频繁波动的定义，例如：

1. `StrategyCard`
2. `StrategySnapshot`
3. `BacktestRun`
4. `BacktestResult`
5. `Conclusion`
6. `HandbookEntry`
7. `RuleTemplate`

## 目录建议

```text
src/
```

## 使用原则

- 这里放“系统共同语言”，不放页面私有结构。
- 前端、后端、回测引擎之间的字段含义应从这里统一。
- 一旦字段进入闭环主链路，修改必须谨慎。
