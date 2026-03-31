# 阶段 3 里程碑验收记录：前端结论填写与保存

**验收日期**：2026-03-30
**验收范围**：`apps/web` 结论填写前端最小闭环
**验收结论**：**通过**

---

## 1. 验收目标

确认用户端「填写结论 → 保存成功 / 保存失败反馈」这条前端链路是否已成立，是否达到阶段 3 中「结论可保存」的最小可验收标准。

---

## 2. 逐项核查

### 2.1 组件实现

| 检查项 | 文件 | 结论 |
|--------|------|------|
| 结论表单组件 `ConclusionForm` | `apps/web/src/features/backtest/components/conclusion-form.tsx` | ✅ 已实现 |
| 结论区块挂载位置（结果展示后） | `backtest-run-view.tsx:292-299` | ✅ `resultQuery.data` 成立后渲染 |
| 两个 checkbox 字段 | `conclusion-form.tsx:159, 171` | ✅ `is_worth_researching`、`can_accept_drawdown` |
| 下一步行动下拉（5 项枚举） | `conclusion-form.tsx:186-201` | ✅ `rerun / refine_rules / observe_only / add_to_handbook / discard` |
| 适用行情说明 textarea（选填） | `conclusion-form.tsx:205-222` | ✅ max 2000 字 Zod 校验 |
| 备注 textarea（选填） | `conclusion-form.tsx:224-243` | ✅ max 4000 字 Zod 校验 |
| 保存中状态 | `conclusion-form.tsx:263` | ✅ `"保存中…"` 禁用 |
| 保存成功转只读摘要 | `conclusion-form.tsx:109-111` | ✅ `savedConclusion` state → `SavedConclusionView` |
| 保存失败含 `CONCLUSION_ALREADY_EXISTS` 文案 | `conclusion-form.tsx:119-122` | ✅ `"该回测结果已有结论，无法重复保存。"` |
| `data-testid` 覆盖 | 各表单元素 | ✅ form / checkboxes / select / textareas / submit / error / saved |

### 2.2 API 接入

| 检查项 | 文件 | 结论 |
|--------|------|------|
| `useCreateConclusionMutation` | `api.ts:70-77` | ✅ 调用 `POST /api/strategy-cards/{id}/conclusions` |
| `ConclusionUpsertPayload` 类型 | `types.ts:77-84` | ✅ 与 api-contracts.md §4.12 对齐 |
| `ConclusionResponse` 类型 | `types.ts:86-97` | ✅ 与 api-contracts.md §4.13 对齐 |
| `CONCLUSION_NEXT_ACTION_LABELS` 映射 | `types.ts:69-75` | ✅ 5 项中文标签齐备 |

### 2.3 构建验证

```
✓ Compiled successfully in 9.3s
✓ TypeScript: 0 errors
✓ Build: 0 errors
```

### 2.4 E2E 测试

| 测试用例 | 文件 | 结果 |
|----------|------|------|
| 提交结论 → 转只读摘要 | `conclusion-save.spec.ts:69` | ✅ PASSED |
| 重复提交 → `CONCLUSION_ALREADY_EXISTS` 错误提示 | `conclusion-save.spec.ts:91` | ✅ PASSED |

**2/2 通过**（运行耗时 33.7s）

---

## 3. 验收标准对照

| 阶段 3 标准（acceptance-criteria-and-test-checklist.md §4） | 状态 |
|--------------------------------------------------------------|------|
| 结果页可读（前序里程碑） | ✅ 已通过 |
| **结论可保存** | ✅ **本次通过** |
| 手册链路闭环成立 | 待实现 |

---

## 4. 遗留项（不阻塞本里程碑）

1. **`PUT /api/conclusions/{id}`**（更新结论）：后端未实现，前端暂无编辑入口。当前每次回测只有一次保存机会，与阶段 3 MVP 范围一致，不阻塞。
2. **`POST /api/handbook`**（加入交易手册）：下一个里程碑，尚未实现。
3. **Checkpoint commit 仍未提交**：`packages/backtest-engine/`（未跟踪）、`services/api/pyproject.toml`、`uv.lock`、`apps/web` 结论表单代码均未 commit，建议尽快执行。

---

## 5. 结论

前端结论填写与保存最小闭环**已成立**。表单字段完整、API 接入正确、保存成功/失败反馈均已实现、E2E 全部通过、build 零错误。

阶段 3「结论可保存」里程碑正式验收通过。
