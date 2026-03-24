# 接口契约

## 1. 目标
本文件用于冻结前后端主链路接口的资源命名、请求结构、响应结构和错误格式，确保工程初始化后可以直接按契约编码。

## 2. 当前冻结范围
1. 只覆盖 MVP P0 主链路和少量紧邻主链路的查询接口。
2. 默认采用单用户模式，但接口仍保留 `user_id` 对应的服务端语义。
3. 回测采用轻量异步模式：创建回测返回 `run_id`，由前端轮询状态与结果。
4. 所有指标和结果摘要均由后端统一生成，前端只消费结果。

## 3. 全局约定
1. 接口统一前缀为 `/api`。
2. 请求体和响应体均使用 `application/json`。
3. 所有 `id`、`run_id`、`conclusion_id` 等主键都使用 `uuid` 字符串。
4. 所有时间字段使用 UTC `ISO 8601` 字符串。
5. 费率、收益率、金额在 API 层以 JSON `number` 传输，在服务端按 `decimal` 语义处理。
6. 列表分页统一采用页码分页：`page` 从 `1` 开始，`page_size` 默认 `20`，最大 `100`。

### 3.1 成功响应格式
```json
{
  "success": true,
  "data": {},
  "error": null
}
```

### 3.2 失败响应格式
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "BACKTEST_RESULT_NOT_READY",
    "message": "Backtest result is not ready yet.",
    "details": {},
    "request_id": "2d9f0e76-66af-4e5f-a8b9-bf5d45f88888"
  }
}
```

## 4. 共享 Schema

### 4.1 `BacktestRange`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `start_at` | `string` | 是 | UTC 时间 |
| `end_at` | `string` | 是 | 必须晚于 `start_at` |

### 4.2 `RuleInstance`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `template_key` | `string` | 是 | 见 `docs/contracts/rule-template-schema-v1.md` |
| `params` | `object` | 是 | 结构由对应模板决定 |

### 4.3 `StrategyRuleSet`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `entry` | `RuleInstance` | 是 | 入场规则 |
| `exit` | `RuleInstance` | 是 | 出场规则 |
| `stop_loss` | `RuleInstance \| null` | 否 | 止损规则 |
| `take_profit` | `RuleInstance \| null` | 否 | 止盈规则 |

### 4.4 `StrategyCardUpsertPayload`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `name` | `string` | 是 | `1-120` 字符 |
| `symbol` | `string` | 是 | `BTCUSDT`、`ETHUSDT` |
| `timeframe` | `string` | 是 | `4H`、`1D` |
| `backtest_range` | `BacktestRange` | 是 | 回测区间 |
| `initial_capital` | `number` | 是 | `> 0`，默认建议 `10000` |
| `fee_rate` | `number` | 是 | `0 <= fee_rate <= 0.01` |
| `rule_set` | `StrategyRuleSet` | 是 | 规则集合 |

### 4.5 `StrategyCardSummary`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | 策略卡主键 |
| `name` | `string` | 是 | 策略名称 |
| `symbol` | `string` | 是 | 标的 |
| `timeframe` | `string` | 是 | 周期 |
| `status` | `string` | 是 | `draft`、`ready`、`archived` |
| `updated_at` | `string` | 是 | 最近更新时间 |
| `latest_backtest_run_id` | `string \| null` | 否 | 最近回测运行 |

### 4.6 `StrategyCardDetail`
`StrategyCardDetail = StrategyCardSummary + StrategyCardUpsertPayload + { created_at: string }`

### 4.7 `BacktestRunResponse`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `run_id` | `string` | 是 | 回测运行主键 |
| `strategy_card_id` | `string` | 是 | 来源策略卡 |
| `strategy_snapshot_id` | `string` | 是 | 冻结快照 |
| `status` | `string` | 是 | `queued`、`running`、`succeeded`、`failed`、`cancelled` |
| `error_code` | `string \| null` | 否 | 失败错误码 |
| `error_message` | `string \| null` | 否 | 失败原因 |
| `started_at` | `string \| null` | 否 | 开始时间 |
| `finished_at` | `string \| null` | 否 | 结束时间 |
| `result_url` | `string \| null` | 否 | 结果可用时返回 |
| `created_at` | `string` | 是 | 创建时间 |

### 4.8 `SummaryMetrics`
| 字段 | 类型 | 必填 |
| --- | --- | --- |
| `total_return_rate` | `number` | 是 |
| `max_drawdown_rate` | `number` | 是 |
| `win_rate` | `number` | 是 |
| `profit_factor` | `number` | 是 |
| `trade_count` | `number` | 是 |
| `avg_holding_bars` | `number` | 是 |
| `final_equity` | `number` | 是 |

### 4.9 `CurvePoint`
| 字段 | 类型 | 必填 |
| --- | --- | --- |
| `ts` | `string` | 是 |
| `value` | `number` | 是 |

### 4.10 `TradeRecord`
| 字段 | 类型 | 必填 |
| --- | --- | --- |
| `trade_id` | `string` | 是 |
| `entry_at` | `string` | 是 |
| `exit_at` | `string` | 是 |
| `entry_price` | `number` | 是 |
| `exit_price` | `number` | 是 |
| `quantity` | `number` | 是 |
| `pnl_amount` | `number` | 是 |
| `pnl_rate` | `number` | 是 |
| `exit_reason` | `string` | 是 |

### 4.11 `BacktestResultResponse`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `result_id` | `string` | 是 | 结果主键 |
| `run_id` | `string` | 是 | 回测运行主键 |
| `strategy_card_id` | `string` | 是 | 来源策略卡 |
| `strategy_snapshot_id` | `string` | 是 | 来源快照 |
| `dataset_version` | `string` | 是 | 行情数据版本 |
| `summary_metrics` | `SummaryMetrics` | 是 | 核心指标 |
| `equity_curve` | `CurvePoint[]` | 是 | 资金曲线 |
| `drawdown_curve` | `CurvePoint[]` | 是 | 回撤曲线 |
| `trades` | `TradeRecord[]` | 是 | 交易明细 |
| `result_summary` | `object` | 是 | 模板化结果摘要 |
| `created_at` | `string` | 是 | 结果生成时间 |

### 4.12 `ConclusionUpsertPayload`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `backtest_result_id` | `string` | 是 | 必须属于当前策略卡 |
| `is_worth_researching` | `boolean` | 是 | 是否值得继续研究 |
| `can_accept_drawdown` | `boolean` | 是 | 是否接受当前回撤 |
| `market_condition_notes` | `string` | 否 | 最多 `2000` 字符 |
| `next_action` | `string` | 是 | `rerun`、`refine_rules`、`observe_only`、`add_to_handbook`、`discard` |
| `notes` | `string` | 否 | 最多 `4000` 字符 |

### 4.13 `ConclusionResponse`
`ConclusionResponse = ConclusionUpsertPayload + { id: string, strategy_card_id: string, created_at: string, updated_at: string }`

### 4.14 `HandbookCreatePayload`
| 字段 | 类型 | 必填 | 约束 |
| --- | --- | --- | --- |
| `conclusion_id` | `string` | 是 | 必须存在且 `next_action = add_to_handbook` |
| `memo` | `string` | 否 | 最多 `2000` 字符 |

### 4.15 `HandbookEntryResponse`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `string` | 是 | 主键 |
| `strategy_card_id` | `string` | 是 | 策略卡 |
| `backtest_result_id` | `string` | 是 | 回测结果 |
| `conclusion_id` | `string` | 是 | 结论 |
| `status` | `string` | 是 | `active`、`archived` |
| `memo` | `string \| null` | 否 | 备注 |
| `created_at` | `string` | 是 | 创建时间 |
| `updated_at` | `string` | 是 | 更新时间 |

### 4.16 `DashboardOverviewResponse`
| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `strategy_card_count` | `number` | 是 | 策略卡总数 |
| `handbook_entry_count` | `number` | 是 | 手册条目总数 |
| `latest_strategy_cards` | `StrategyCardSummary[]` | 是 | 最近策略卡 |
| `latest_backtest_runs` | `BacktestRunResponse[]` | 是 | 最近回测记录 |

### 4.17 `PaginationMeta`
| 字段 | 类型 | 必填 |
| --- | --- | --- |
| `page` | `number` | 是 |
| `page_size` | `number` | 是 |
| `total` | `number` | 是 |

## 5. P0 主链路接口

### 5.1 `POST /api/strategy-cards`
- 作用：创建策略卡
- 请求：`StrategyCardUpsertPayload`
- 成功：`201 Created`，返回 `StrategyCardDetail`
- 失败：`400`、`422`

### 5.2 `GET /api/strategy-cards`
- 作用：获取策略卡列表
- 查询参数：`page`、`page_size`、`status?`
- 成功：`200 OK`
- 返回：
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 0
    }
  },
  "error": null
}
```

### 5.3 `GET /api/strategy-cards/{id}`
- 作用：获取策略卡详情
- 成功：`200 OK`，返回 `StrategyCardDetail`
- 失败：`404`

### 5.4 `PUT /api/strategy-cards/{id}`
- 作用：更新策略卡
- 请求：`StrategyCardUpsertPayload`
- 成功：`200 OK`，返回 `StrategyCardDetail`
- 失败：`404`、`422`

### 5.5 `POST /api/strategy-cards/{id}/backtests`
- 作用：基于当前策略卡生成新快照并发起回测
- 请求：空对象 `{}` 即可；MVP 不接受额外回测参数
- 成功：`202 Accepted`，返回 `BacktestRunResponse`
- 失败：`404`、`409`、`422`

### 5.6 `GET /api/backtests/{run_id}`
- 作用：轮询回测运行状态
- 成功：`200 OK`，返回 `BacktestRunResponse`
- 失败：`404`

### 5.7 `GET /api/backtests/{run_id}/result`
- 作用：获取回测结果
- 成功：`200 OK`，返回 `BacktestResultResponse`
- 失败：
  - `404 Not Found`：运行不存在
  - `409 Conflict`：结果尚未生成
  - `422 Unprocessable Entity`：运行失败，无可返回结果

### 5.8 `POST /api/strategy-cards/{id}/conclusions`
- 作用：为指定策略卡和结果创建结论
- 请求：`ConclusionUpsertPayload`
- 成功：`201 Created`，返回 `ConclusionResponse`
- 失败：`404`、`409`、`422`

### 5.9 `PUT /api/conclusions/{id}`
- 作用：更新结论
- 请求：`ConclusionUpsertPayload`
- 成功：`200 OK`，返回 `ConclusionResponse`
- 失败：`404`、`422`

### 5.10 `POST /api/handbook`
- 作用：把结论加入交易手册
- 请求：`HandbookCreatePayload`
- 成功：`201 Created`，返回 `HandbookEntryResponse`
- 失败：`404`、`409`、`422`

### 5.11 `GET /api/handbook`
- 作用：查询交易手册列表
- 查询参数：`page`、`page_size`、`status?`
- 成功：`200 OK`
- 返回：`{ items: HandbookEntryResponse[], pagination: PaginationMeta }`

### 5.12 `GET /api/dashboard/overview`
- 作用：查询首页概览
- 成功：`200 OK`
- 返回：`DashboardOverviewResponse`

## 6. P1 预留接口
1. `POST /api/strategy-cards/{id}/duplicate`
2. `DELETE /api/strategy-cards/{id}`
3. `PUT /api/handbook/{id}`
4. `DELETE /api/handbook/{id}`

说明：这些接口不阻塞当前阶段初始化，但资源命名已预留。

## 7. 状态码规范
| 状态码 | 使用场景 |
| --- | --- |
| `200` | 查询成功、更新成功 |
| `201` | 创建成功 |
| `202` | 已受理异步回测 |
| `400` | 请求格式错误 |
| `404` | 资源不存在 |
| `409` | 状态冲突，例如结果未就绪、手册重复加入 |
| `422` | 业务校验失败 |
| `500` | 未预期的系统错误 |
| `503` | 数据集不可用或依赖服务临时不可用 |

## 8. 错误码清单
| 错误码 | 场景 |
| --- | --- |
| `STRATEGY_CARD_NOT_FOUND` | 策略卡不存在 |
| `STRATEGY_CARD_VALIDATION_FAILED` | 策略卡字段校验失败 |
| `RULE_TEMPLATE_INVALID` | 规则模板或参数不合法 |
| `UNSUPPORTED_SYMBOL` | 不支持的标的 |
| `UNSUPPORTED_TIMEFRAME` | 不支持的周期 |
| `BACKTEST_RUN_NOT_FOUND` | 回测运行不存在 |
| `BACKTEST_RESULT_NOT_READY` | 回测结果尚未准备好 |
| `BACKTEST_RESULT_UNAVAILABLE` | 回测运行失败，无法提供结果 |
| `BACKTEST_DATASET_UNAVAILABLE` | 缺少对应数据集 |
| `BACKTEST_EXECUTION_FAILED` | 回测执行失败 |
| `CONCLUSION_NOT_FOUND` | 结论不存在 |
| `CONCLUSION_ALREADY_EXISTS` | 该结果已有结论 |
| `CONCLUSION_NOT_ELIGIBLE_FOR_HANDBOOK` | 当前结论不允许加入手册 |
| `HANDBOOK_ENTRY_ALREADY_EXISTS` | 重复加入手册 |
| `HANDBOOK_ENTRY_NOT_FOUND` | 手册条目不存在 |

## 9. 异步回测轮询约定
1. 前端发起回测后立即跳转到结果页占位状态，使用 `run_id` 轮询 `GET /api/backtests/{run_id}`。
2. 当状态为 `queued` 或 `running` 时，前端展示“运行中”状态，不调用结果接口。
3. 当状态为 `succeeded` 且 `result_url` 不为空时，前端调用 `GET /api/backtests/{run_id}/result`。
4. 当状态为 `failed` 时，前端展示标准错误态，并使用 `error_code`、`error_message` 给出反馈。
