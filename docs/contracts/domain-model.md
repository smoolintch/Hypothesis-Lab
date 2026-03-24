# 数据模型与领域模型

## 1. 目标
本文件用于冻结 MVP 阶段的核心对象、对象关系、字段类型和数据库映射草案，作为前端、后端、回测引擎和数据库设计的共同基础。

## 2. 当前冻结范围
1. 只覆盖 MVP P0 主链路对象。
2. 默认采用单用户模式，但所有核心对象都保留 `user_id`。
3. 回测执行采用轻量异步模型：创建 `BacktestRun` 后轮询状态。
4. 所有历史回测结果必须可追溯，不允许被后续编辑覆盖。

## 3. 全局建模约定
1. 所有主键使用 `uuid`。
2. 所有时间字段使用 UTC `ISO 8601` 语义。
3. 金额与费率在领域层按 `decimal` 语义处理；数据库层使用 `numeric`。
4. `StrategyCard` 可编辑，`StrategySnapshot` 不可编辑。
5. 每次发起回测都必须先从 `StrategyCard` 生成一份新的 `StrategySnapshot`。
6. `BacktestResult` 只允许由回测引擎和结果分析模块生成。
7. MVP 阶段每个 `BacktestResult` 只维护一条当前结论；结论可更新，但不做版本化。

## 4. 核心枚举
| 枚举 | 取值 |
| --- | --- |
| `Symbol` | `BTCUSDT`、`ETHUSDT` |
| `Timeframe` | `4H`、`1D` |
| `StrategyCardStatus` | `draft`、`ready`、`archived` |
| `BacktestRunStatus` | `queued`、`running`、`succeeded`、`failed`、`cancelled` |
| `ConclusionNextAction` | `rerun`、`refine_rules`、`observe_only`、`add_to_handbook`、`discard` |
| `HandbookEntryStatus` | `active`、`archived` |
| `RuleTemplateKey` | `ma_cross`、`rsi_threshold`、`price_breakout`、`streak_reversal`、`fixed_take_profit`、`fixed_stop_loss` |

## 5. 共享值对象

### 5.1 `BacktestRange`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_at` | `datetime` | 是 | 回测开始时间 |
| `end_at` | `datetime` | 是 | 回测结束时间，必须晚于 `start_at` |

### 5.2 `RuleInstance`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `template_key` | `RuleTemplateKey` | 是 | 模板键 |
| `params` | `json object` | 是 | 模板参数，具体结构见 `rule-template-schema-v1` |

### 5.3 `StrategyRuleSet`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `entry` | `RuleInstance` | 是 | 入场规则 |
| `exit` | `RuleInstance` | 是 | 出场规则 |
| `stop_loss` | `RuleInstance \| null` | 否 | 止损规则，可为空 |
| `take_profit` | `RuleInstance \| null` | 否 | 止盈规则，可为空 |

### 5.4 `NormalizedStrategyConfig`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `market.symbol` | `Symbol` | 是 | 标的 |
| `market.timeframe` | `Timeframe` | 是 | 周期 |
| `market.backtest_range` | `BacktestRange` | 是 | 回测区间 |
| `execution.initial_capital` | `decimal(18,2)` | 是 | 初始资金 |
| `execution.fee_rate` | `decimal(8,6)` | 是 | 手续费率 |
| `execution.position_mode` | `string` | 是 | 固定为 `all_in` |
| `execution.trade_direction` | `string` | 是 | 固定为 `long_only` |
| `rules` | `StrategyRuleSet` | 是 | 标准化规则集 |

### 5.5 `SummaryMetrics`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `total_return_rate` | `decimal(10,6)` | 是 | 总收益率 |
| `max_drawdown_rate` | `decimal(10,6)` | 是 | 最大回撤 |
| `win_rate` | `decimal(10,6)` | 是 | 胜率 |
| `profit_factor` | `decimal(10,6)` | 是 | 盈亏比 |
| `trade_count` | `integer` | 是 | 交易次数 |
| `avg_holding_bars` | `decimal(10,2)` | 是 | 平均持仓 K 线数 |
| `final_equity` | `decimal(18,2)` | 是 | 期末权益 |

### 5.6 `CurvePoint`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `ts` | `datetime` | 是 | 时间点 |
| `value` | `decimal(18,6)` | 是 | 曲线值 |

### 5.7 `TradeRecord`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `trade_id` | `uuid` | 是 | 交易记录主键 |
| `entry_at` | `datetime` | 是 | 入场时间 |
| `exit_at` | `datetime` | 是 | 出场时间 |
| `entry_price` | `decimal(18,8)` | 是 | 入场价 |
| `exit_price` | `decimal(18,8)` | 是 | 出场价 |
| `quantity` | `decimal(18,8)` | 是 | 持仓数量 |
| `pnl_amount` | `decimal(18,6)` | 是 | 单笔盈亏金额 |
| `pnl_rate` | `decimal(10,6)` | 是 | 单笔收益率 |
| `exit_reason` | `string` | 是 | 例如 `exit_rule`、`stop_loss`、`take_profit` |

## 6. 核心对象

### 6.1 `StrategyCard`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `user_id` | `uuid` | 是 | 用户主键，MVP 默认绑定固定用户 |
| `name` | `string(1-120)` | 是 | 策略名称 |
| `symbol` | `Symbol` | 是 | 交易标的 |
| `timeframe` | `Timeframe` | 是 | 交易周期 |
| `backtest_range` | `BacktestRange` | 是 | 回测区间 |
| `initial_capital` | `decimal(18,2)` | 是 | 初始资金，MVP 默认值 `10000` |
| `fee_rate` | `decimal(8,6)` | 是 | 手续费率，推荐默认值 `0.001` |
| `rule_set` | `StrategyRuleSet` | 是 | 规则配置 |
| `status` | `StrategyCardStatus` | 是 | 卡片状态 |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 更新时间 |

### 6.2 `StrategySnapshot`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `user_id` | `uuid` | 是 | 用户主键 |
| `strategy_card_id` | `uuid` | 是 | 来源策略卡 |
| `version` | `integer` | 是 | 该策略卡下的快照版本号，从 `1` 递增 |
| `source_strategy_updated_at` | `datetime` | 是 | 生成快照时策略卡的最后更新时间 |
| `normalized_config` | `NormalizedStrategyConfig` | 是 | 标准化后的不可变配置 |
| `created_at` | `datetime` | 是 | 快照生成时间 |

### 6.3 `BacktestRun`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键，同时作为 `run_id` 对外暴露 |
| `user_id` | `uuid` | 是 | 用户主键 |
| `strategy_snapshot_id` | `uuid` | 是 | 绑定的策略快照 |
| `status` | `BacktestRunStatus` | 是 | 运行状态 |
| `error_code` | `string \| null` | 否 | 失败时的标准错误码 |
| `error_message` | `string \| null` | 否 | 失败时的人类可读信息 |
| `started_at` | `datetime \| null` | 否 | 实际开始时间 |
| `finished_at` | `datetime \| null` | 否 | 结束时间 |
| `created_at` | `datetime` | 是 | 创建时间 |

### 6.4 `BacktestResult`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `user_id` | `uuid` | 是 | 用户主键 |
| `backtest_run_id` | `uuid` | 是 | 对应的回测运行 |
| `dataset_version` | `string` | 是 | 行情数据版本号 |
| `summary_metrics` | `SummaryMetrics` | 是 | 核心指标 |
| `equity_curve` | `CurvePoint[]` | 是 | 资金曲线 |
| `drawdown_curve` | `CurvePoint[]` | 是 | 回撤曲线 |
| `trades` | `TradeRecord[]` | 是 | 交易明细 |
| `result_summary` | `json object` | 是 | 模板化摘要，包含亮点、风险、建议 |
| `created_at` | `datetime` | 是 | 结果生成时间 |

### 6.5 `Conclusion`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `user_id` | `uuid` | 是 | 用户主键 |
| `strategy_card_id` | `uuid` | 是 | 关联策略卡 |
| `backtest_result_id` | `uuid` | 是 | 关联回测结果 |
| `is_worth_researching` | `boolean` | 是 | 是否值得继续研究 |
| `can_accept_drawdown` | `boolean` | 是 | 是否接受当前回撤水平 |
| `market_condition_notes` | `string(0-2000)` | 否 | 适用行情说明 |
| `next_action` | `ConclusionNextAction` | 是 | 下一步动作 |
| `notes` | `string(0-4000)` | 否 | 自由备注 |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 更新时间 |

### 6.6 `HandbookEntry`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `user_id` | `uuid` | 是 | 用户主键 |
| `strategy_card_id` | `uuid` | 是 | 关联策略卡 |
| `backtest_result_id` | `uuid` | 是 | 关联回测结果 |
| `conclusion_id` | `uuid` | 是 | 关联结论 |
| `status` | `HandbookEntryStatus` | 是 | 手册条目状态 |
| `memo` | `string(0-2000)` | 否 | 补充说明 |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 更新时间 |

### 6.7 `RuleTemplate`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `template_key` | `RuleTemplateKey` | 是 | 模板键 |
| `version` | `integer` | 是 | 当前固定为 `1` |
| `display_name` | `string` | 是 | 展示名 |
| `category` | `string` | 是 | `entry`、`exit`、`risk` |
| `parameter_schema` | `json object` | 是 | 参数约束 |
| `normalized_output_shape` | `json object` | 是 | 标准化输出形状 |
| `enabled` | `boolean` | 是 | 是否可用 |

说明：MVP 阶段 `RuleTemplate` 优先作为代码注册表存在，不要求先建数据库表。

### 6.8 `MarketDataset`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `uuid` | 是 | 主键 |
| `symbol` | `Symbol` | 是 | 标的 |
| `timeframe` | `Timeframe` | 是 | 周期 |
| `source` | `string` | 是 | 数据来源 |
| `version` | `string` | 是 | 数据版本号 |
| `coverage_start_at` | `datetime` | 是 | 覆盖开始时间 |
| `coverage_end_at` | `datetime` | 是 | 覆盖结束时间 |
| `candle_count` | `integer` | 是 | K 线数量 |
| `storage_uri` | `string` | 是 | 原始文件或对象存储位置 |
| `created_at` | `datetime` | 是 | 导入时间 |

## 7. 对象关系与基数
```text
User 1 -> N StrategyCard
StrategyCard 1 -> N StrategySnapshot
StrategySnapshot 1 -> N BacktestRun
BacktestRun 1 -> 0..1 BacktestResult
BacktestResult 1 -> 0..1 Conclusion
Conclusion 1 -> 0..1 HandbookEntry
MarketDataset 1 -> N BacktestResult
```

补充约束：
1. `StrategySnapshot.version` 在同一 `StrategyCard` 下唯一。
2. `BacktestResult.backtest_run_id` 唯一。
3. `Conclusion.backtest_result_id` 唯一。
4. `HandbookEntry.conclusion_id` 唯一。

## 8. 数据库表草案
1. `users`：最简用户表；MVP 启动时插入一条默认用户记录。
2. `strategy_cards`
3. `strategy_snapshots`
4. `backtest_runs`
5. `backtest_results`
6. `conclusions`
7. `handbook_entries`
8. `market_datasets`

## 9. 索引建议
1. `strategy_cards (user_id, updated_at desc)`
2. `strategy_snapshots (strategy_card_id, version)` 唯一
3. `backtest_runs (strategy_snapshot_id, created_at desc)`
4. `backtest_runs (status, created_at desc)`
5. `backtest_results (backtest_run_id)` 唯一
6. `conclusions (backtest_result_id)` 唯一
7. `handbook_entries (user_id, status, updated_at desc)`
8. `market_datasets (symbol, timeframe, version)` 唯一

## 10. 建模约束
1. 页面层不得直接持久化 `normalized_config` 之外的临时 UI 结构。
2. 历史回测结果必须长期保留，不因策略继续编辑而丢失。
3. 指标口径只能由后端和回测引擎统一生成，前端只展示。
4. `StrategyCard` 删除能力可后置，但在实现前必须明确是软删还是硬删；MVP 推荐软删。
5. 在引入真实登录前，所有核心表都保留 `user_id`，但业务逻辑可默认注入固定用户。

## 11. 暂不进入 v1 的内容
1. 多用户协作
2. 做空与杠杆
3. 多标的组合策略
4. 结论版本历史
5. 手册条目标签体系
