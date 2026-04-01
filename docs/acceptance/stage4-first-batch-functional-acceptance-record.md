# 阶段 4 首批闭环功能验收记录（策略列表 + 复制策略卡）

## 1. 验收目标
独立验收首页 `/` 上两条阶段 4 首批最小链路是否已经达到当前里程碑收口标准：
1. 策略列表
2. 复制策略卡并继续编辑

本轮仅验证首批闭环范围，不扩展到阶段 4 的后续能力，也不升级为整个阶段 4 总验收。

## 2. 验收范围
### 2.1 在范围内
- 首页 `/` 的策略列表承接
- `GET /api/strategy-cards?page=1&page_size=20`
- 列表的 loading / error / empty / populated 四态
- 列表项最小信息展示：`name`、`symbol`、`timeframe`、`updated_at`
- 从首页进入 `/strategy-cards/{id}/edit`
- `POST /api/strategy-cards/{id}/duplicate`
- 复制中的显式提交反馈
- 复制失败的显式错误反馈
- 复制成功后跳转到新卡编辑页并加载成功

### 2.2 不在范围内
- 最近实验记录
- 历史回测记录
- 搜索 / 筛选
- 复杂分页
- 删除策略卡
- 整个阶段 4 终验

## 3. 文档与契约核对
1. 首页 `/` 被定义为策略列表入口页，首页应覆盖 loading / empty / success / error 状态；空状态应强调主 CTA。[user-flow-and-page-states.md:61-72](../product/user-flow-and-page-states.md#L61-L72)
2. 编辑页路由为 `/strategy-cards/{id}/edit`。[user-flow-and-page-states.md:20-24](../product/user-flow-and-page-states.md#L20-L24)
3. 阶段 4 当前推荐顺序是：策略列表、复制策略卡、最近实验记录、历史回测记录，本轮只覆盖前两项。[task-breakdown-and-development-order.md:49-53](../project/task-breakdown-and-development-order.md#L49-L53)
4. 列表接口契约为 `GET /api/strategy-cards`，采用 `page=1`、`page_size=20` 的分页约定，返回 `items + pagination`。[api-contracts.md:18](../contracts/api-contracts.md#L18) [api-contracts.md:76-85](../contracts/api-contracts.md#L76-L85) [api-contracts.md:188-193](../contracts/api-contracts.md#L188-L193) [api-contracts.md:203-221](../contracts/api-contracts.md#L203-L221)
5. `current-status.md` 已把“策略列表 + 复制策略卡前后端最小闭环已落地”列为当前已完成事实，且下一步就是交付测试 Agent 验收。[current-status.md:42-51](../project/current-status.md#L42-L51)

## 4. 代码证据
### 4.1 首页承接策略列表
首页直接渲染 `StrategyCardList`，并保留首页主 CTA `新建策略假设`，满足空状态下仍有清晰主入口。[page.tsx:7-31](../../apps/web/src/app/page.tsx#L7-L31)

### 4.2 策略列表调用真实接口
前端列表请求固定通过 `getStrategyCardList()` 发起，默认参数为 `page = 1`、`pageSize = 20`，最终请求 `/strategy-cards?page=1&page_size=20`。[api.ts:25-30](../../apps/web/src/features/strategy-card/api.ts#L25-L30) [api.ts:64-68](../../apps/web/src/features/strategy-card/api.ts#L64-L68)

### 4.3 列表四态与最小信息展示
`StrategyCardList` 已实现：
- loading 态 `strategy-card-list-loading`
- error 态 `strategy-card-list-error`
- empty 态 `strategy-card-list-empty`
- populated 态 `strategy-card-list`

并在列表项展示 `item.name`、`item.symbol`、`item.timeframe`、`item.updated_at`，且提供进入编辑页链接 `/strategy-cards/{id}/edit`。[strategy-card-list.tsx:25-121](../../apps/web/src/features/strategy-card/components/strategy-card-list.tsx#L25-L121)

### 4.4 复制策略卡链路接入真实接口
前端复制动作通过 `duplicateStrategyCard(strategyCardId)` 调用真实接口 `POST /api/strategy-cards/{id}/duplicate`，成功后还会失效列表查询缓存。[api.ts:47-52](../../apps/web/src/features/strategy-card/api.ts#L47-L52) [api.ts:77-85](../../apps/web/src/features/strategy-card/api.ts#L77-L85)

后端路由已暴露对应真实接口，并返回 `201 Created` + `StrategyCardDetailResponse`。[strategy_cards.py:98-108](../../services/api/app/api/routes/strategy_cards.py#L98-L108)

### 4.5 复制中的提交反馈、失败反馈、成功跳转
首页列表项为每张卡提供复制按钮；点击后：
- 当前项文案切换为 `复制中…`
- 按钮禁用，避免重复提交
- 失败时展示 `strategy-card-duplicate-error`
- 成功后跳转到 `/strategy-cards/{newId}/edit`

对应实现见 [strategy-card-list.tsx:33-47](../../apps/web/src/features/strategy-card/components/strategy-card-list.tsx#L33-L47) 和 [strategy-card-list.tsx:97-113](../../apps/web/src/features/strategy-card/components/strategy-card-list.tsx#L97-L113)。

## 5. 测试证据
### 5.1 E2E：首批闭环主链路
执行：`npx playwright test tests/e2e/core-flow/strategy-list.spec.ts`

结果：`3 passed`

覆盖内容：
1. 空状态首页展示
2. 有数据列表展示 + 进入编辑页
3. 复制策略卡后跳转到新卡编辑页，并验证新卡表单正确加载与回填

关键测试位于 [strategy-list.spec.ts:47-56](../../tests/e2e/core-flow/strategy-list.spec.ts#L47-L56)、[strategy-list.spec.ts:58-86](../../tests/e2e/core-flow/strategy-list.spec.ts#L58-L86)、[strategy-list.spec.ts:88-120](../../tests/e2e/core-flow/strategy-list.spec.ts#L88-L120)。

其中复制链路测试明确断言：
- 列表中存在复制入口
- 点击后出现“复制中”反馈
- 跳转到新的 `/strategy-cards/{id}/edit`
- 新旧 `strategyId` 不相同
- 新卡编辑页可见并正确回填关键字段

### 5.2 前端静态校验
执行：`cd apps/web && npm run typecheck`

结果：通过。

执行：`npm run lint`

结果：通过。

### 5.3 后端最小接口验证
执行：`cd services/api && uv run pytest ../../tests/integration/api -q`

结果：`2 passed`。

该轮验证覆盖 API 基线集，未出现与本轮首批闭环相冲突的问题。

## 6. 范围控制检查
本轮验收目标要求“不混入未完成的阶段 4 后续能力”。当前首页与本次测试证据中，未看到以下内容进入本轮闭环：
- 最近实验记录
- 历史回测记录
- 搜索 / 筛选
- 复杂分页
- 删除策略卡

因此本轮实现仍保持在“阶段 4 首批闭环”的最小收口范围内。

## 7. 结论
### 7.1 是否达到当前里程碑收口标准
达到。

### 7.2 最终结论
**通过**

### 7.3 判断依据
1. 策略列表链路已满足首页承接、真实接口调用、四态覆盖、最小信息展示、进入编辑页。
2. 复制策略卡链路已满足真实接口调用、提交中反馈、失败反馈、成功跳转到新卡编辑页，并由 E2E 证明“复制后继续编辑”链路成立。
3. 当前实现未混入阶段 4 后续能力，范围收敛正确。
4. 文档真相源 `current-status.md` 与代码、测试结果一致，无冲突。

### 7.4 是否建议作为当前 checkpoint 收口
**建议现在做 checkpoint。**

原因：阶段 4 首批两条最小链路已经形成稳定闭环，并且已有独立代码证据与自动化验证证据支撑，适合作为当前里程碑收口。
