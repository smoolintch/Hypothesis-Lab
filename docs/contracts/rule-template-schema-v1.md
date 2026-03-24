# 规则模板 Schema v1

## 1. 目标
本文件用于冻结 MVP 阶段规则模板的参数结构、校验规则和标准化输出约定，保证前端表单、后端校验和回测引擎使用同一套规则语言。

## 2. 当前冻结范围
1. 只支持单标的、单周期、只做多。
2. 每张策略卡固定包含：
   - `1` 个入场规则
   - `1` 个出场规则
   - `0..1` 个止损规则
   - `0..1` 个止盈规则
3. 不支持多条件组合、AND/OR 嵌套、脚本表达式和自定义指标。

## 3. 标准化规则集结构
```json
{
  "rule_set": {
    "entry": {
      "template_key": "ma_cross",
      "params": {}
    },
    "exit": {
      "template_key": "rsi_threshold",
      "params": {}
    },
    "stop_loss": null,
    "take_profit": null
  }
}
```

## 4. 标准化策略配置结构
```json
{
  "market": {
    "symbol": "BTCUSDT",
    "timeframe": "4H",
    "backtest_range": {
      "start_at": "2023-01-01T00:00:00Z",
      "end_at": "2024-01-01T00:00:00Z"
    }
  },
  "execution": {
    "initial_capital": 10000,
    "fee_rate": 0.001,
    "position_mode": "all_in",
    "trade_direction": "long_only"
  },
  "rules": {
    "entry": {
      "template_key": "ma_cross",
      "params": {
        "ma_type": "ema",
        "fast_period": 20,
        "slow_period": 50,
        "cross_direction": "golden"
      }
    },
    "exit": {
      "template_key": "rsi_threshold",
      "params": {
        "period": 14,
        "comparison": "gte",
        "threshold": 70
      }
    },
    "stop_loss": {
      "template_key": "fixed_stop_loss",
      "params": {
        "stop_loss_rate": 0.08
      }
    },
    "take_profit": null
  }
}
```

## 5. 通用校验规则
1. `entry` 和 `exit` 必填。
2. `stop_loss`、`take_profit` 可为空。
3. 所有周期参数必须为正整数。
4. 所有费率、阈值、收益率参数必须为正数。
5. 时间范围不属于规则模板本身，统一由策略卡字段承载。
6. 同一模板键的参数必须严格匹配本文件定义，禁止透传多余字段。

## 6. 模板定义

### 6.1 `ma_cross`
- 作用：均线穿越信号
- 可用位置：`entry`、`exit`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `ma_type` | `string` | 是 | `sma`、`ema` | 均线类型 |
| `fast_period` | `integer` | 是 | `2-200` | 快线周期 |
| `slow_period` | `integer` | 是 | `3-400` 且 `slow_period > fast_period` | 慢线周期 |
| `cross_direction` | `string` | 是 | `golden`、`dead` | 金叉或死叉 |

标准化输出：
```json
{
  "template_key": "ma_cross",
  "params": {
    "ma_type": "ema",
    "fast_period": 20,
    "slow_period": 50,
    "cross_direction": "golden"
  }
}
```

### 6.2 `rsi_threshold`
- 作用：RSI 阈值信号
- 可用位置：`entry`、`exit`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `period` | `integer` | 是 | `2-100` | RSI 周期 |
| `comparison` | `string` | 是 | `lte`、`gte` | 小于等于或大于等于 |
| `threshold` | `number` | 是 | `0-100` | RSI 阈值 |

### 6.3 `price_breakout`
- 作用：价格突破最近区间高点或低点
- 可用位置：`entry`、`exit`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `lookback_bars` | `integer` | 是 | `2-200` | 回看 K 线数 |
| `breakout_side` | `string` | 是 | `break_high`、`break_low` | 突破方向 |

### 6.4 `streak_reversal`
- 作用：连续涨跌后的反转触发
- 可用位置：`entry`、`exit`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `direction` | `string` | 是 | `up`、`down` | 连涨或连跌 |
| `streak_count` | `integer` | 是 | `2-10` | 连续根数 |

### 6.5 `fixed_take_profit`
- 作用：固定比例止盈
- 可用位置：`take_profit`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `take_profit_rate` | `number` | 是 | `0 < x < 1` | 例如 `0.15` 表示 15% 止盈 |

### 6.6 `fixed_stop_loss`
- 作用：固定比例止损
- 可用位置：`stop_loss`

| 参数 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `stop_loss_rate` | `number` | 是 | `0 < x < 1` | 例如 `0.08` 表示 8% 止损 |

## 7. 模板位置约束
| 模板键 | `entry` | `exit` | `stop_loss` | `take_profit` |
| --- | --- | --- | --- | --- |
| `ma_cross` | 是 | 是 | 否 | 否 |
| `rsi_threshold` | 是 | 是 | 否 | 否 |
| `price_breakout` | 是 | 是 | 否 | 否 |
| `streak_reversal` | 是 | 是 | 否 | 否 |
| `fixed_stop_loss` | 否 | 否 | 是 | 否 |
| `fixed_take_profit` | 否 | 否 | 否 | 是 |

## 8. 前后端实现要求
1. 前端表单层可以按模板渲染不同参数输入项，但提交结构必须回到本文件定义。
2. 后端保存策略卡前必须按模板键校验参数合法性。
3. 回测引擎只消费标准化后的 `template_key + params`，不接触页面私有字段。
4. 如需新增模板，必须先更新本文件，再更新 `domain-model` 和相关测试。
