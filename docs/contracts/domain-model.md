# 数据模型与领域模型

## 1. 目标
本文件用于冻结 MVP 阶段的核心对象、对象关系和关键字段，作为前后端、回测引擎和数据库设计的共同基础。

## 2. 核心对象

| 对象 | 说明 | 当前状态 |
| --- | --- | --- |
| `StrategyCard` | 用户正在编辑和管理的策略假设卡 | P0 |
| `StrategySnapshot` | 发起回测时冻结的输入快照 | P0 |
| `BacktestRun` | 一次回测运行记录 | P0 |
| `BacktestResult` | 指标、曲线、交易明细、摘要 | P0 |
| `Conclusion` | 用户对实验结果的判断 | P0 |
| `HandbookEntry` | 纳入交易手册的条目 | P0 |
| `RuleTemplate` | 模板化规则定义 | P0 |
| `MarketDataset` | 标准化行情数据集 | P0 |

## 3. 对象关系

```text
StrategyCard
  -> StrategySnapshot
    -> BacktestRun
      -> BacktestResult
        -> Conclusion
          -> HandbookEntry
```

## 4. 关键字段建议

### 4.1 StrategyCard
- `id`
- `user_id`
- `name`
- `symbol`
- `timeframe`
- `backtest_range`
- `entry_rule`
- `exit_rule`
- `stop_loss_rule`
- `fee_rate`
- `status`
- `created_at`
- `updated_at`

### 4.2 StrategySnapshot
- `id`
- `strategy_card_id`
- `version`
- `normalized_config`
- `created_at`

### 4.3 BacktestRun
- `id`
- `strategy_snapshot_id`
- `status`
- `started_at`
- `finished_at`
- `error_message`

### 4.4 BacktestResult
- `id`
- `backtest_run_id`
- `summary_metrics`
- `equity_curve`
- `drawdown_curve`
- `trades`
- `result_summary`

### 4.5 Conclusion
- `id`
- `strategy_card_id`
- `backtest_result_id`
- `is_worth_researching`
- `can_accept_drawdown`
- `market_condition_notes`
- `next_action`
- `notes`

### 4.6 HandbookEntry
- `id`
- `strategy_card_id`
- `backtest_result_id`
- `conclusion_id`
- `status`
- `memo`

## 5. 建模约束
1. 每次回测必须绑定一个不可变快照。
2. 历史回测结果必须保留，不因策略继续编辑而丢失。
3. 结论与手册条目都必须可追溯到具体结果。
4. 指标口径只能有一套来源。

## 6. 待补充项
1. 字段类型
2. 枚举值
3. 数据库表结构
4. 索引设计
