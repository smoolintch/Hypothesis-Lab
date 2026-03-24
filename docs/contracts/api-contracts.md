# 接口契约

## 1. 目标
本文件用于定义前后端之间的接口边界、资源命名和输入输出格式。在前后端并行开发前，这份文档必须冻结主链路接口。

## 2. 当前接口范围
1. 策略卡接口
2. 回测接口
3. 结果查询接口
4. 结论接口
5. 交易手册接口
6. 首页概览接口

## 3. 推荐接口分组

### 3.1 Strategy Cards
- `POST /api/strategy-cards`
- `GET /api/strategy-cards`
- `GET /api/strategy-cards/{id}`
- `PUT /api/strategy-cards/{id}`
- `POST /api/strategy-cards/{id}/duplicate`
- `DELETE /api/strategy-cards/{id}`

### 3.2 Backtests
- `POST /api/strategy-cards/{id}/backtests`
- `GET /api/backtests/{run_id}`
- `GET /api/backtests/{run_id}/result`

### 3.3 Conclusions
- `POST /api/strategy-cards/{id}/conclusions`
- `PUT /api/conclusions/{id}`

### 3.4 Handbook
- `POST /api/handbook`
- `GET /api/handbook`
- `PUT /api/handbook/{id}`
- `DELETE /api/handbook/{id}`

### 3.5 Dashboard
- `GET /api/dashboard/overview`

## 4. 通用响应约定

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

## 5. 当前必须先冻结的契约
1. 创建和更新 `StrategyCard` 的请求结构
2. 发起回测的请求结构
3. `BacktestResult` 的返回结构
4. 结论保存结构
5. 错误返回结构

## 6. 待补充项
1. 详细字段 schema
2. 状态码规范
3. 分页格式
4. 错误码清单
5. 异步回测状态轮询格式
