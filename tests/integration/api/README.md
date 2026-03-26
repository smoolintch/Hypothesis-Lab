# api integration tests

这里放 API 与应用编排相关的集成测试。

## 当前基线

1. `test_api_smoke.py`：验证最小 FastAPI 应用可以创建。
2. 验证默认 `docs`、`redoc`、`openapi.json` 端点在当前仓库状态下可访问。

## 当前刻意不做的事

1. 不新增 `/health`、`/ping`、`/ready` 等自定义健康检查接口。
2. 不依赖数据库连接或业务表结构。
3. 不提前实现策略卡、回测、结论、手册等业务链路测试。
