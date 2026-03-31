# 阶段 4 里程碑验收记录：策略列表后端最小闭环

**验收日期**：2026-03-31
**验收范围**：阶段 4 第一个里程碑——「策略列表」后端最小闭环
**验收结论**：**通过**

---

## 1. 验收目标

确认 `GET /api/strategy-cards` 后端能力是否已完成，是否达到阶段 4 第一个里程碑的最小后端标准。

---

## 2. 参考文档

| 文档 | 角色 |
|------|------|
| `docs/MVP开发计划.md §8 阶段 4` | 阶段核心产出（"策略卡列表页"） |
| `docs/contracts/api-contracts.md §4.5/4.17/5.2` | 接口契约定义 |
| `docs/project/task-breakdown-and-development-order.md §2 阶段 4` | 任务顺序（"策略列表"为阶段 4 第一项） |
| `docs/project/current-status.md §4/§7 条目 61` | 项目当前状态（后端落地已记录） |

---

## 3. 契约对照

### api-contracts.md §5.2 `GET /api/strategy-cards`

| 契约项 | 状态 |
|--------|------|
| 接口路径 `GET /api/strategy-cards` 存在 | ✅ `routes/strategy_cards.py` L56-68 |
| 查询参数 `page`（默认 1）| ✅ `Query(default=1, ge=1)` |
| 查询参数 `page_size`（默认 20，最大 100）| ✅ `Query(default=20, ge=1, le=100)` |
| 查询参数 `status?`（可选筛选）| ✅ `Query(default=None, alias="status")` |
| 成功返回 `200 OK` | ✅ |
| 响应格式 `{ success, data: { items, pagination }, error }` | ✅ `SuccessResponse[StrategyCardListResponse]` |

### api-contracts.md §4.5 `StrategyCardSummary` 字段

| 字段 | 状态 |
|------|------|
| `id` | ✅ |
| `name` | ✅ |
| `symbol` | ✅ |
| `timeframe` | ✅ |
| `status` | ✅ |
| `updated_at` | ✅ |
| `latest_backtest_run_id` | ✅（可为 null）|
| 详情字段不出现（`rule_set`、`backtest_range` 等）| ✅ 集成测试 `test_list_strategy_cards_summary_fields` 已验证 |

### api-contracts.md §4.17 `PaginationMeta`

| 字段 | 状态 |
|------|------|
| `page` | ✅ |
| `page_size` | ✅ |
| `total` | ✅ |

---

## 4. 实现层级核查

| 层级 | 文件 | 状态 |
|------|------|------|
| 路由层 | `app/api/routes/strategy_cards.py` `list_strategy_cards()` | ✅ |
| 服务层 | `app/application/strategy_cards/service.py` `list_cards()` | ✅ |
| 仓储层 | `app/infrastructure/database/repositories/strategy_card.py` `list_paginated()` | ✅ |
| Schema | `app/schemas/strategy_cards.py`：`StrategyCardSummaryResponse`、`PaginationMeta`、`StrategyCardListResponse` | ✅ |

### `list_paginated()` 行为核查

| 行为 | 状态 |
|------|------|
| 按 `updated_at` 倒序排列 | ✅ `.order_by(StrategyCardModel.updated_at.desc())` |
| `status` 可选筛选 | ✅ 有 `status` 参数时追加 filter |
| offset/limit 分页 | ✅ `.offset((page - 1) * page_size).limit(page_size)` |
| 返回 `(items, total)` 二元组 | ✅ |

---

## 5. 集成测试结果

测试文件：`services/api/tests/integration/test_strategy_cards_list.py`

| 测试用例 | 覆盖点 | 结果 |
|----------|--------|------|
| `test_list_strategy_cards_empty` | 空列表返回结构正确 | ✅ PASSED |
| `test_list_strategy_cards_returns_created_cards` | 有数据时返回 total 与 items | ✅ PASSED |
| `test_list_strategy_cards_summary_fields` | 字段子集校验（有无详情字段）| ✅ PASSED |
| `test_list_strategy_cards_ordered_by_updated_at_desc` | 按更新时间倒序 | ✅ PASSED |
| `test_list_strategy_cards_pagination` | 分页边界（page1/page2/超出页）| ✅ PASSED |
| `test_list_strategy_cards_page_size_max_100` | `page_size=101` 返回 422 | ✅ PASSED |
| `test_list_strategy_cards_status_filter` | 状态筛选（draft/ready 各自）| ✅ PASSED |
| `test_list_strategy_cards_no_filter_returns_all_statuses` | 无筛选返回全部 | ✅ PASSED |
| `test_list_strategy_cards_reflects_latest_backtest_run_id` | 发起回测后 ID 反映最新 run | ✅ PASSED |
| **合计** | | **9/9 ✅** |

全套集成测试：**52/52 ✅**

---

## 6. 最终验收结论

**阶段 4「策略列表」后端最小闭环——通过。**

- `GET /api/strategy-cards` 已完整实现，与 `api-contracts.md §5.2` 完全对齐
- 分页、状态筛选、按 `updated_at` 倒序、`StrategyCardSummary` 字段子集均正确
- 9/9 专项集成测试通过，全套 52/52 通过
- 无契约漂移，无阻塞缺口

**建议**：可进入 checkpoint，之后进入阶段 4「前端接入策略列表页」里程碑。
