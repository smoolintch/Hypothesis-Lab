# web

前端应用目录，负责承载 MVP 的页面、交互和用户体验。

## 建议子目录

```text
src/
  app/                    页面入口与路由
  features/               按业务能力拆分的前端模块
    strategy-card/        策略假设卡创建与编辑
    backtest-result/      回测结果展示与摘要阅读
    handbook/             交易手册展示与操作
  components/             跨页面复用组件
  lib/                    前端工具、请求封装、状态辅助
public/                   静态资源
```

## 目录职责

- `src/app`: 页面级入口，不承载复杂业务逻辑。
- `src/features`: 以业务闭环为中心组织代码，避免按技术碎片化拆分。
- `src/components`: 通用展示组件和基础交互组件。
- `src/lib`: 请求、格式化、常量、前端通用工具。

## 当前阶段建议

优先落地：

1. 首页
2. 策略假设编辑页
3. 回测结果页
4. 交易手册页
