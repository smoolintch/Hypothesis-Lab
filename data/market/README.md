# Market Data Fixtures

仓库内固定行情样本统一放在 `data/market`，用于：

1. 回测引擎开发阶段的标准化输入基线。
2. API 集成前的数据格式对齐。
3. 回归测试时的固定样本数据源。

这些文件是小体积、可版本化的开发样本，不是生产级全量历史数据，也不是实时抓取产物。

## 目录规范

固定目录结构如下：

```text
data/market/<source>/<symbol>/<timeframe>/<version>/
  manifest.json
  candles.csv
```

字段说明：

1. `source`：数据来源标识。当前仓库固定样本统一使用 `fixture`，表示“仓库内固定样本”，避免与未来真实交易所来源混淆。
2. `symbol`：交易标的，当前只允许 `BTCUSDT`、`ETHUSDT`。
3. `timeframe`：周期，当前只允许 `4H`、`1D`。
4. `version`：不可变版本目录名，当前固定样本采用 `sample-v<N>`。

当前 MVP 范围内，每个数据集目录必须同时包含：

1. `manifest.json`
2. `candles.csv`

## CSV 格式规范

`candles.csv` 约束如下：

1. 文件编码使用 UTF-8。
2. 第一行必须是表头，且字段顺序固定为 `ts,open,high,low,close,volume`。
3. `ts` 使用 UTC `ISO 8601` 字符串，格式示例：`2024-01-01T00:00:00Z`。
4. `ts` 表示该根 K 线的开盘时间。
5. 数据必须按 `ts` 严格升序排列，且不允许重复时间戳。
6. `open`、`high`、`low`、`close`、`volume` 使用十进制字面量。
7. 不允许额外列，也不允许缺少必需列。

## Manifest 规范

`manifest.json` 必须与 `MarketDataset` 约束对齐，当前最小字段如下：

1. `schema_version`
2. `id`
3. `source`
4. `symbol`
5. `timeframe`
6. `version`
7. `coverage_start_at`
8. `coverage_end_at`
9. `candle_count`
10. `storage_uri`
11. `created_at`
12. `timezone`
13. `sort_order`
14. `columns`

字段语义：

1. `coverage_start_at`：首根 K 线开盘时间，包含边界。
2. `coverage_end_at`：末根 K 线收盘时间，采用排他上界。
3. `candle_count`：`candles.csv` 中的数据行数，不包含表头。
4. `storage_uri`：仓库根目录相对路径，指向对应 `candles.csv`。
5. `timezone`：当前固定写为 `UTC`。
6. `sort_order`：当前固定写为 `ts_asc`。
7. `columns`：当前固定写为 `["ts", "open", "high", "low", "close", "volume"]`。

## 版本规则

固定样本版本遵循以下规则：

1. 版本目录名采用 `sample-v<N>`，从 `sample-v1` 开始递增。
2. 同一 `(source, symbol, timeframe, version)` 组合视为一个不可变数据集。
3. 只要 `candles.csv` 任意一行、任意排序、任意字段值，或 `manifest.json` 中影响数据语义的字段发生变化，就必须创建新版本目录，不能原地覆盖旧版本。
4. 仅更新说明文档，不修改数据集内容时，不需要 bump 版本。
5. 后续如引入真实来源数据，仍沿用同一目录结构，但 `source` 应改为真实来源标识，例如交易所名。

## 导入约定

后续回测引擎或 API 消费固定样本时，按以下顺序处理：

1. 先按 `source/symbol/timeframe/version` 定位数据集目录。
2. 先读取 `manifest.json`，确认元数据与支持范围。
3. 再读取 `candles.csv`，并按 manifest 做校验。
4. 读取成功后，将 `manifest.version` 作为 `dataset_version` 进入回测结果快照。

建议的最小校验项：

1. `manifest.json` 必填字段齐全。
2. 目录名与 manifest 中的 `source`、`symbol`、`timeframe`、`version` 一致。
3. `candles.csv` 表头与字段顺序正确。
4. 时间戳为 UTC，且严格升序、无重复。
5. `candle_count` 与 CSV 行数一致。
6. `coverage_start_at` 等于首行 `ts`。
7. `coverage_end_at` 等于末行 `ts + timeframe`。

## 当前固定样本

当前仓库内提供以下小体积样本切片：

1. `data/market/fixture/BTCUSDT/4H/sample-v1`
2. `data/market/fixture/BTCUSDT/1D/sample-v1`
3. `data/market/fixture/ETHUSDT/4H/sample-v1`
4. `data/market/fixture/ETHUSDT/1D/sample-v1`

这些切片用于格式对齐、导入验证和回归基线建设，不承诺覆盖完整历史区间。
