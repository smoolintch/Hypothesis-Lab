# backtest-engine

回测引擎目录，负责将标准化策略配置应用到标准化历史数据上，输出稳定、可复现的回测结果。

## 建议子目录

```text
src/
  core/                   回测主流程与执行器
  metrics/                收益率、回撤、胜率等指标计算
  data/                   数据读取、数据适配、时间序列预处理
```

## 使用原则

- 只消费标准化输入，不依赖页面状态。
- 每次回测都应支持输入快照追溯。
- 指标计算口径必须固定。
- 同一输入重复运行时，结果必须一致。

## 当前阶段建议

优先完成：

1. 单标的
2. 单策略
3. 单周期
4. 只做多
5. 全仓进出

## 当前已落地

当前已落地最小“标准化行情数据读取接口”，位于：

```text
src/backtest_engine/data/
```

当前入口函数：

```python
from backtest_engine.data import BacktestRange, load_market_candles
```

最小调用示例：

```python
dataset = load_market_candles(
    symbol="BTCUSDT",
    timeframe="4H",
    version="sample-v1",
    backtest_range=BacktestRange(
        start_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
)
```

返回结果：
1. `dataset.metadata`：标准化数据集元信息
2. `dataset.candles`：按时间升序输出的标准化 `Candle` 序列

当前接口只负责：
1. 数据集定位
2. manifest 读取
3. CSV 解析
4. 基础字段校验
5. UTC 时间与升序校验
6. 可选按 `backtest_range` 过滤

当前接口不负责：
1. 技术指标计算
2. 策略逻辑
3. 回测执行
4. 结果指标生成

## 本轮新增最小回测执行入口

当前最小执行入口：

```python
from backtest_engine import (
    load_market_candles,
    parse_normalized_strategy_config,
    run_backtest,
)
```

最小调用示例：

```python
dataset = load_market_candles(
    symbol="BTCUSDT",
    timeframe="1D",
    version="sample-v1",
)

config = parse_normalized_strategy_config(
    {
        "market": {
            "symbol": "BTCUSDT",
            "timeframe": "1D",
            "backtest_range": {
                "start_at": "2024-01-01T00:00:00Z",
                "end_at": "2024-01-06T00:00:00Z",
            },
        },
        "execution": {
            "initial_capital": 10000,
            "fee_rate": 0.001,
            "position_mode": "all_in",
            "trade_direction": "long_only",
        },
        "rules": {
            "entry": {
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "lte",
                    "threshold": 30,
                },
            },
            "exit": {
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "gte",
                    "threshold": 70,
                },
            },
            "stop_loss": {
                "template_key": "fixed_stop_loss",
                "params": {
                    "stop_loss_rate": 0.08,
                },
            },
            "take_profit": None,
        },
    }
)

result = run_backtest(config, dataset.candles)
```

当前返回：
1. `result.trades`：最小交易记录序列
2. `result.equity_curve`：每根 bar 收盘后的资金曲线基础点位
3. `result.final_equity`：期末权益
4. `result.total_fees_paid`：本次回测累计手续费

## 当前支持范围

当前最小支持范围固定为：

1. 单标的
2. 单策略
3. 单周期
4. `long_only`
5. `all_in`

当前支持的模板子集：

1. 入场：`ma_cross`、`rsi_threshold`
2. 出场：`ma_cross`、`rsi_threshold`
3. 风控：`fixed_stop_loss`
4. 可选：`fixed_take_profit`

## 当前执行约定

为保证结果稳定、可重复，当前执行口径固定为：

1. 普通入场/出场信号按触发 bar 的 `close` 成交。
2. 止损/止盈优先于普通出场规则，按阈值价成交。
3. 若同一根 bar 同时命中止损和止盈，优先止损。
4. 同一根 bar 最多执行一个动作；平仓后不在同一根 bar 重新开仓。
5. 最后一根 bar 不再新开仓；若仍有持仓，则按最后一根 bar 的 `close` 强制平仓，`exit_reason=end_of_data`。
