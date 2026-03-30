# 阶段 2 正式验收记录

**验收日期**：2026-03-30
**验收结论**：**通过**——阶段 2 可正式结束，可进入阶段 3

---

## 1. 验收范围

阶段 2 目标：`让系统对标准化策略配置执行真实、稳定、可重复的历史回测`

涉及模块：
- `packages/backtest-engine`：回测执行引擎
- `services/api`：回测链路 API（快照 + run + result 持久化）
- `data/market/fixture/*`：BTC/ETH × 4H/1D 固定样本数据

---

## 2. 逐条退出标准判断

### 标准 1：系统已具备真实、稳定、可重复的历史回测能力

**结论：通过**

**依据**：
- `packages/backtest-engine/src/backtest_engine/core/runner.py` 实现了完整的 `run_backtest()` 函数，支持 `ma_cross`、`rsi_threshold`、`fixed_stop_loss`、`fixed_take_profit` 规则子集，以及单标的、`long_only`、`all_in` 执行逻辑。
- `services/api/app/application/backtests/service.py::BacktestRunService._execute_and_persist_result()` 将引擎调用、结果持久化、状态更新完整串联，在进程内同步执行。
- 实际测试运行验证：`packages/backtest-engine` **9/9** 测试通过（含标准化固定样本可运行）。

---

### 标准 2：StrategySnapshot → BacktestRun → BacktestResult 主链路完整成立

**结论：通过**

**依据**：
- `BacktestRunService.start_backtest_for_strategy_card()` 完整实现链路：
  1. 从 `StrategyCard` 生成不可变 `StrategySnapshot`（含 `normalized_config`、递增 `version`）
  2. 创建 `BacktestRun`（`status=queued`）
  3. 调用 `run_backtest()` 执行引擎
  4. 持久化 `BacktestResult`（`summary_metrics`、`equity_curve`、`drawdown_curve`、`trades`、`dataset_version`）
  5. 更新 `BacktestRun.status` 为 `succeeded`（或 `failed`）
- `GET /api/backtests/{run_id}/result` 返回完整 `BacktestResultResponse`，`result_url` 在 `succeeded` 时自动填充。
- 集成测试 `test_start_backtest_runs_and_produces_succeeded_status` + `test_get_backtest_result_returns_real_metrics` PASSED，确认链路端到端成立。

---

### 标准 3：同一输入重复运行结果一致

**结论：通过**

**依据**：
| 测试 | 层级 | 标的 | 结果 |
|---|---|---|---|
| `test_run_backtest_is_deterministic_for_same_input` | 引擎 | BTCUSDT/1D | PASSED |
| `test_get_backtest_result_consistent_on_repeated_runs` | API | BTCUSDT/4H | PASSED |
| `test_repeated_runs_produce_consistent_metrics[BTCUSDT-1D]` | API | BTCUSDT/1D | PASSED |
| `test_repeated_runs_produce_consistent_metrics[ETHUSDT-4H]` | API | ETHUSDT/4H | PASSED |
| `test_repeated_runs_produce_consistent_metrics[ETHUSDT-1D]` | API | ETHUSDT/1D | PASSED |

一致性验证粒度：`summary_metrics` 全字段相等，`equity_curve` 长度一致，`trades` 数量一致，`dataset_version` 一致。

---

### 标准 4：回测失败时具备明确、可见、可定位的错误信息

**结论：通过**

**依据**：
- `_execute_and_persist_result()` 捕获三类异常并分类映射到标准错误码：
  - `BacktestConfigError` / `BacktestExecutionError` → `BACKTEST_EXECUTION_FAILED`
  - `MarketDatasetNotFoundError` / `InvalidMarketDatasetError` → `BACKTEST_DATASET_UNAVAILABLE`
  - 未预期异常 → `BACKTEST_EXECUTION_FAILED`（含 `type(exc).__name__` 前缀）
- `BacktestRun.error_message` 截断保存异常信息（最多 2000 字符）。
- `GET /api/backtests/{run_id}/result` 对 failed run 返回 `422 + BACKTEST_RESULT_UNAVAILABLE`。
- 集成测试 `test_get_result_returns_422_when_run_failed`（日期超出 fixture 覆盖范围触发失败）PASSED。
- 集成测试 `test_get_result_returns_409_when_run_not_finished` PASSED。

---

### 标准 5：BTC/ETH、1D/4H 预设范围均可稳定出结果

**结论：通过**

**依据**：

| 组合 | 覆盖测试文件 | 结果 |
|---|---|---|
| BTCUSDT/4H | `test_backtest_real_execution.py`（全部 6 个测试均使用此组合）| PASSED |
| BTCUSDT/1D | `test_backtest_all_symbols_independent.py[BTCUSDT-1D]` × 2 | PASSED |
| ETHUSDT/4H | `test_backtest_all_symbols_independent.py[ETHUSDT-4H]` × 2 | PASSED |
| ETHUSDT/1D | `test_backtest_all_symbols_independent.py[ETHUSDT-1D]` × 2 | PASSED |

4 组 fixture 数据文件均存在：`data/market/fixture/{BTCUSDT,ETHUSDT}/{4H,1D}/sample-v1/`

---

### 标准 6：当前是否存在阻止阶段切换的缺口

**结论：无功能性阻塞缺口**

已确认不阻塞阶段切换的事项：
- `result_summary` 当前为空 `{}`：这是阶段 2 计划内的延迟项，阶段 3 的"模板化结果摘要"负责填充，不阻塞验收。
- `packages/backtest-engine/` 全部文件尚未 git commit：属于工程 checkpoint 问题，不影响功能验收，**但在进入阶段 3 之前必须完成 checkpoint commit**。

---

## 3. 验证采信的测试与代码事实

| 来源 | 内容 | 实际运行 |
|---|---|---|
| `packages/backtest-engine/tests/` | 9/9 通过 | ✅ 本轮实际运行确认 |
| `services/api/tests/integration/` | 26/26 通过（含 17 个回测相关）| ✅ 本轮实际运行确认 |
| `services/api/app/application/backtests/service.py` | 主链路实现代码直接审查 | ✅ 代码审查 |
| `data/market/fixture/` | 4 组 manifest.json 存在 | ✅ glob 验证 |

---

## 4. 最终结论

**阶段 2 正式验收：通过**

所有退出标准均满足，无功能性阻塞项。

---

## 5. 进入阶段 3 的前置建议

在开始阶段 3 实现前，建议先完成一次 checkpoint commit，提交以下内容：
1. `packages/backtest-engine/`（全部新增文件，当前未跟踪）
2. `services/api/pyproject.toml`（新增 backtest-engine 依赖）
3. `services/api/uv.lock`（依赖锁定文件更新）
4. 已修改的文档文件（`current-status.md` 等）

这不是阶段切换的阻塞条件，但不 commit 会增加后续混杂风险。
