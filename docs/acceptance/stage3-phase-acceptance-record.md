# 阶段 3 阶段级验收记录：结果与沉淀链路

**验收日期**：2026-03-31
**验收范围**：阶段 3「结果与沉淀链路」整体
**验收结论**：**有条件阶段通过**

---

## 1. 验收目标

从阶段层面判断阶段 3 三条主链路是否整体成立，是否可以结束阶段 3、进入下一阶段。

---

## 2. 参考文档

| 文档 | 角色 |
|------|------|
| `docs/MVP开发计划.md §8 阶段 3` | **阶段退出标准**（真相优先级第 3 位） |
| `docs/acceptance/acceptance-criteria-and-test-checklist.md §2/4` | 验收重点与 P0 核验项（优先级第 7 位） |
| `docs/product/user-flow-and-page-states.md §3/7` | 路由定义与页面状态要求（优先级第 5 位） |
| `docs/contracts/domain-model.md §6/7` | 领域模型约束 |
| `docs/contracts/api-contracts.md §4/5` | 接口契约 |

---

## 3. 三条主链路逐项核查

### 3.1 结果页可读

| 检查项 | 状态 |
|--------|------|
| 7 项核心指标卡片（total_return_rate、max_drawdown_rate、win_rate 等）| ✅ |
| SVG 资金曲线（equity_curve）| ✅ |
| SVG 回撤曲线（drawdown_curve） | ✅ |
| 最近 20 笔交易明细 | ✅ |
| queued / running / failed / succeeded 各状态有对应 UI | ✅ |
| 非存在 run_id → not-found 状态 | ✅ |
| build / typecheck / lint 零错误 | ✅ |
| E2E 测试（`backtest-result-page.spec.ts`）| ✅ 4/4 PASSED |

**结论：结果页可读 ✅**

---

### 3.2 结论可保存

| 检查项 | 状态 |
|--------|------|
| 结论表单（2 checkbox + select + 2 textarea）| ✅ |
| 保存调用 `POST /api/strategy-cards/{id}/conclusions`（201）| ✅ |
| 保存成功转只读摘要（`SavedConclusionView`）| ✅ |
| 保存失败含 `CONCLUSION_ALREADY_EXISTS` 文案 | ✅ |
| 后端 10 个集成测试全部通过 | ✅ |
| E2E 测试（`conclusion-save.spec.ts`）| ✅ 2/2 PASSED |
| **刷新后展示已保存结论（"再次查看"）** | ⚠️ **缺口** |

**已知缺口**：`/backtests/{run_id}` 页面刷新后，`savedConclusion` React state 重置为 null，结论区块重新呈现为空表单，不会从服务端加载已保存结论。结论数据已持久化（`ConclusionModel` 有效存储），但前端无法在下次访问时加载。

- 对应 MVP开发计划.md: "用户可以保存结论并**再次查看**"
- 对应 acceptance-criteria-and-test-checklist.md P0 item 7: "关键数据刷新后不丢失"
- 该功能需要 `GET /api/conclusions?backtest_result_id=xxx` 或等价端点 + 前端结论查询层

**结论：结论可保存 ✅（含已接受的单次保存限制），但"再次查看"缺口 ⚠️**

---

### 3.3 加入交易手册闭环成立

| 检查项 | 状态 |
|--------|------|
| 结论保存成功后，`next_action === "add_to_handbook"` 时展示手册区块 | ✅ |
| 可选 memo textarea | ✅ |
| 调用 `POST /api/handbook`（201）| ✅ |
| 保存成功转只读摘要 + "前往交易手册"链接 | ✅ |
| `HANDBOOK_ENTRY_ALREADY_EXISTS` 错误文案 | ✅ |
| `CONCLUSION_NOT_ELIGIBLE_FOR_HANDBOOK` 错误文案 | ✅ |
| 后端 7 个集成测试全部通过 | ✅ |
| E2E 测试（`handbook.spec.ts`）| ✅ 2/2 PASSED |
| **`/handbook` 交易手册页存在** | ⚠️ **缺口** |

**已知缺口**："前往交易手册"链接（`href="/handbook"`）指向不存在的路由，Next.js 返回 404。

- 对应 user-flow-and-page-states.md §3: `/handbook` 路由已定义
- 对应 user-flow-and-page-states.md §4 规则 6: "留在当前页并展示'已加入手册'，同时提供跳转 `/handbook` 入口"
- 对应 user-flow-and-page-states.md §7.4: `/handbook` 页面状态已定义（加载中/空状态/已有条目/失败）
- 需要 `GET /api/handbook` 接口 + `/handbook` 前端页面（至少最小列表视图）

**结论：加入手册的操作链路 ✅，但"前往手册"为死链 ⚠️**

---

## 4. E2E 全套汇总

运行 `tests/e2e/core-flow/` 全部 14 个测试：

| 测试文件 | 通过 |
|----------|------|
| `backtest-placeholder.spec.ts` | 2/2 |
| `backtest-result-page.spec.ts` | 4/4 |
| `conclusion-save.spec.ts` | 2/2 |
| `handbook.spec.ts` | 2/2 |
| `home-entry.spec.ts` | 1/1 |
| `strategy-card.spec.ts` | 3/3 |
| **合计** | **14/14** |

API 集成测试（`services/api`）：43/43 通过。

---

## 5. 阶段退出标准对照（MVP开发计划.md §8 阶段3）

| 退出标准 | 状态 |
|----------|------|
| 用户可以在 30 秒内判断策略是否值得继续研究 | ✅ |
| 用户可以保存结论并**再次查看** | ⚠️ 保存 ✅，再次查看 ❌ |
| 用户可以把策略纳入交易手册，完整闭环首次成立 | ⚠️ 纳入操作 ✅，/handbook 页面 ❌ |

---

## 6. P0 核心验收对照（acceptance-criteria-and-test-checklist.md §2）

| P0 核验项 | 状态 |
|-----------|------|
| 用户可以创建并保存策略假设卡 | ✅ |
| 用户可以发起回测 | ✅ |
| 系统可以返回稳定的回测结果 | ✅ |
| 用户可以看懂核心指标与曲线 | ✅ |
| 用户可以保存结论 | ✅ |
| 用户可以加入交易手册 | ✅ |
| **关键数据刷新后不丢失** | ⚠️ 结论数据刷新后前端状态丢失 |

---

## 7. 阶段验收结论

### 结论：**有条件阶段通过**

**可以宣布成立的能力：**
- 结果页可读（7 指标 + 2 曲线 + 交易明细，状态机完整）✅
- 结论可保存（单次闭环完整，前后端全链路通过）✅
- 加入交易手册动作链路完整（校验 + 持久化 + 反馈）✅
- 全套 14/14 E2E、43/43 集成测试通过 ✅

**尚未满足的退出条件（须在阶段正式收尾前或进入阶段 4 早期解决）：**

| 缺口 | 优先级 | 描述 |
|------|--------|------|
| `/handbook` 最小列表页 | 🔴 高 | "前往交易手册"链接目前 404，破坏"完整闭环成立"的用户体验；需要 `GET /api/handbook` + 最小前端页（列表 + 空状态） |
| 结论"再次查看" | 🟡 中 | 刷新后结论区块重置为空表单；需要加载已保存结论（`GET /api/conclusions?backtest_result_id=xxx` 或类似端点） |

**切换到阶段 4 的推荐条件**：以上两个缺口至少完成 `/handbook` 最小列表页（高优先级），或明确记录为阶段 4 第一批任务。

---

## 8. Checkpoint 建议

**强烈建议立即做 checkpoint commit。**

当前积压了横跨阶段 2 + 阶段 3 的全部未提交变更：
- `packages/backtest-engine/`（全部未跟踪）
- `services/api`（pyproject.toml、uv.lock、阶段 2+3 全部业务代码）
- `apps/web`（结果页、结论表单、手册入口）
- `docs/`（验收记录、current-status.md）

以"阶段 2 + 阶段 3 主链路实现"为范围做一次 checkpoint，再继续推进两个缺口。
