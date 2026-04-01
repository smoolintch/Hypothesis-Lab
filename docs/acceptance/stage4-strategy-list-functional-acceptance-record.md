# 阶段 4 功能级验收记录：策略列表前后端最小闭环

**验收日期**：2026-04-01
**验收范围**：阶段 4 子项——「策略列表前后端最小闭环」
**验收对象**：`apps/web` 首页 `/` + `services/api` `GET /api/strategy-cards`
**验收结论**：**通过**

---

## 1. 本轮验收目标

确认阶段 4 的「策略列表前后端最小闭环」是否已经达到当前里程碑收口标准。

本轮仅验收：
- 首页 `/` 是否真实接入 `GET /api/strategy-cards?page=1&page_size=20`
- 是否形成最小可演示列表闭环
- 是否存在阶段越界或 scope creep

本轮不扩展到：
- 复制策略卡
- 最近实验
- 历史回测记录
- 搜索 / 筛选
- 复杂分页
- 阶段 4 总验收

---

## 2. 验收依据

### 文档边界
1. `docs/project/current-status.md`
2. `docs/project/task-breakdown-and-development-order.md`
3. `docs/MVP开发计划.md`
4. `docs/acceptance/acceptance-criteria-and-test-checklist.md`
5. `docs/contracts/api-contracts.md`
6. `docs/product/user-flow-and-page-states.md`

### 关键边界结论
- 阶段 4 的当前子项是「策略列表」
- 首页 `/` 是允许承接策略列表入口的页面
- 列表接口契约为 `GET /api/strategy-cards?page=1&page_size=20`
- 当前子项目标是最小列表闭环，而不是阶段 4 的全部能力

---

## 3. 实际核查的实现与测试证据

### 前端实现
- `apps/web/src/app/page.tsx`
- `apps/web/src/features/strategy-card/components/strategy-card-list.tsx`
- `apps/web/src/features/strategy-card/api.ts`
- `apps/web/src/features/strategy-card/types.ts`

### 后端边界
- `services/api/app/api/routes/strategy_cards.py`

### 测试证据
- `tests/e2e/core-flow/strategy-list.spec.ts`
- `tests/e2e/core-flow/home-entry.spec.ts`
- 实际执行：`npx playwright test tests/e2e/core-flow/strategy-list.spec.ts` → **2/2 通过**
- 实际执行：`npm run typecheck` → **通过**
- 实际执行：`npm run lint` → **通过**

---

## 4. 能力点逐项验收

### 4.1 当前能力属于阶段 4 合法范围，且未越界扩展
**结果：满足**

首页仅新增最小策略列表能力：
- 已有策略卡列表展示
- 空状态
- 错误态
- 加载中
- 进入编辑页入口

未混入以下未完成能力：
- 复制策略卡
- 最近实验
- 历史回测记录
- 搜索 / 筛选
- 复杂分页

符合阶段 4「策略列表」子项的最小范围。

### 4.2 首页 `/` 已真实接入 `GET /api/strategy-cards?page=1&page_size=20`
**结果：满足**

`apps/web/src/features/strategy-card/api.ts` 中：
- `getStrategyCardList(page = 1, pageSize = 20)` 默认拼出 `page=1&page_size=20`
- `useStrategyCardListQuery()` 直接调用该查询

`apps/web/src/app/page.tsx` 中：
- 首页直接渲染 `StrategyCardList`

`tests/e2e/core-flow/strategy-list.spec.ts` 中：
- 空状态测试明确 mock 了 `**/api/strategy-cards?page=1&page_size=20`
- 有数据测试通过真实创建策略卡后回到首页验证列表展示与跳转

### 4.3 首页已形成可演示的最小列表闭环
**结果：满足**

`apps/web/src/features/strategy-card/components/strategy-card-list.tsx` 明确覆盖：
- 加载中：`data-testid="strategy-card-list-loading"`
- 错误态：`data-testid="strategy-card-list-error"`
- 空状态：`data-testid="strategy-card-list-empty"`
- 有数据状态：`data-testid="strategy-card-list"` + `strategy-card-list-items`

其中：
- 空状态有明确提示文案
- 有数据状态可展示最小列表项
- 错误态有明确失败提示

### 4.4 有数据时展示最小必要信息
**结果：满足**

列表项展示内容包含：
- 策略名称
- 标的
- 周期
- 最近更新时间

证据：
`strategy-card-list.tsx` 列表项文案为：
`{item.symbol} · {item.timeframe} · 最近更新 {formatUpdatedAt(item.updated_at)}`

E2E 用例也显式断言：
- 名称可见
- `BTCUSDT · 1D · 最近更新 ...` 可见

### 4.5 有数据时可进入 `/strategy-cards/{id}/edit`
**结果：满足**

列表项提供：
- `href="/strategy-cards/${item.id}/edit"`
- `data-testid="strategy-card-edit-link-${item.id}"`

E2E 已验证：
- 点击后跳转到 `/strategy-cards/{id}/edit`
- 编辑页标题、表单和名称回填均可见

### 4.6 空状态下有明确主操作入口，不是空白页
**结果：满足**

虽然空状态区块本身未内嵌 CTA，但首页外层始终保留主操作入口：
- `home-create-strategy-link`
- 指向 `/strategy-cards/new`

结合首页结构，用户在空状态时不会落入空白页，且有明确下一步动作。

`home-entry.spec.ts` 已验证该主入口存在并可跳转。

### 4.7 没有伪造或混入未完成能力
**结果：满足**

核查 `page.tsx` 与 `strategy-card-list.tsx` 后确认：
- 没有复制策略卡按钮
- 没有最近实验区块
- 没有历史回测记录区块
- 没有搜索框 / 筛选器
- 没有复杂分页控件

属于严格的最小闭环实现，无明显 scope creep。

---

## 5. 不满足项

**无。**

本轮功能级验收范围内，未发现阻止该子项通过的缺口。

---

## 6. Scope Creep / 阶段越界判断

**不存在明显 scope creep 或阶段越界。**

当前交付物严格围绕：
- 首页承接策略列表
- 调用真实列表接口
- 支持最小四态 UI
- 提供进入编辑页入口

没有把阶段 4 后续能力提前塞入本轮里程碑。

---

## 7. 最终结论

**通过。**

理由：
1. 当前能力属于阶段 4「策略列表」合法范围
2. 首页 `/` 已真实接入 `GET /api/strategy-cards?page=1&page_size=20`
3. 已形成可演示的最小前后端闭环
4. 加载中 / 错误态 / 空状态 / 有数据状态全部成立
5. 有数据时展示最小必要信息，并可进入编辑页
6. 无 scope creep，无阻塞缺口
7. E2E、typecheck、lint 均已通过

---

## 8. checkpoint 建议

**适合形成 checkpoint 里程碑。**

原因：
- 该子项已形成独立、可解释、可回滚的小里程碑
- 已有自动化验证
- 已完成功能级验收
- 继续推进下一子项前，保存当前状态可降低后续混杂风险
