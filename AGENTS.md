# Hypothesis Lab Agent Guide

本项目允许使用高强度 AI 辅助开发，但不接受“越写越乱”的 vibe-coding。

本文件是本仓库内 Agent 的常驻协作规则。任何 Agent 在开始工作前，都应先阅读本文件，再阅读项目当前状态文档。

## 1. 目标
保证以下三件事始终成立：

1. 任何时刻都能快速判断项目当前状态。
2. 任何 Agent 都能在上下文不完整时安全恢复工作。
3. 开发过程始终围绕 MVP 主闭环推进，而不是无边界扩散。

## 2. 项目真相来源顺序
当聊天上下文、记忆、代码现状和文档不一致时，按下面顺序判断：

1. `docs/project/current-status.md`
2. `docs/project/session-handoff.md`
3. `docs/MVP开发计划.md`
4. `docs/architecture/`
5. `docs/contracts/`
6. `docs/project/task-breakdown-and-development-order.md`
7. `docs/acceptance/`

不要只凭会话记忆继续写代码。

## 3. 每次开工前必须做的事
1. 阅读 `AGENTS.md`。
2. 阅读 `docs/project/current-status.md`。
3. 若存在未完成工作，阅读 `docs/project/session-handoff.md`。
4. 阅读本次任务相关的 `contracts/`、`architecture/`、`acceptance/` 文档。
5. 用一句话确认：
   - 当前目标是什么
   - 影响哪个模块
   - 验收标准是什么
6. 如果目标不清晰，先问，不要猜。

## 4. 会话执行规则
1. 一次只推进一个主目标。
2. 优先完成主链路，不要顺手扩展 P1/P2 功能。
3. 跨模块改动前，先确认契约和边界是否需要更新。
4. 变更领域模型时，先更新 `docs/contracts/domain-model.md`。
5. 变更接口时，先更新 `docs/contracts/api-contracts.md`。
6. 变更系统边界或技术路线时，先更新 `docs/architecture/`，必要时新增 ADR。
7. 不允许为了省事，把页面私有结构直接变成系统契约。
8. 不允许在没有记录原因的情况下引入临时绕路实现。

## 5. 最小防乱原则
为避免项目失控，所有 Agent 默认遵守以下原则：

1. One session, one goal：一个会话只解决一个主问题。
2. Contract first：跨边界开发先定契约。
3. Small diff：优先做最小可交付变更。
4. No silent scope expansion：不偷偷扩需求。
5. Docs stay in sync：文档和代码不能长期背离。
6. Stop when uncertain：不确定时停下确认。

## 6. 什么情况下必须先更新文档
遇到以下情况，先更新文档，再继续开发：

1. 新增或修改 API
2. 新增或修改核心领域对象
3. 调整模块边界
4. 改变任务优先级
5. 发现原计划不再成立
6. 引入新的基础设施、部署方式或测试策略

## 7. 如何保持“随时知道当前项目状态”
本项目使用两个运行中的状态文件：

### 7.1 `docs/project/current-status.md`
这是项目当前状态的唯一总入口，用来记录：

1. 当前处于哪个阶段
2. 最近完成了什么
3. 当前最优先任务是什么
4. 下一个安全步骤是什么
5. 当前有哪些阻塞点或未决问题

### 7.2 `docs/project/session-handoff.md`
这是“会话交接文件”，专门处理：

1. 中途中断
2. API 配额耗尽
3. 对话上下文丢失
4. 任务做了一半需要换 Agent

任何未完成任务离开前，都必须更新这份文件。

## 8. 中断恢复协议
如果出现以下情况：

1. 上下文丢失
2. Agent 更换
3. 会话过长
4. API 枯竭
5. 做到一半被打断

恢复步骤固定为：

1. 读 `AGENTS.md`
2. 读 `docs/project/current-status.md`
3. 读 `docs/project/session-handoff.md`
4. 读本次相关文档
5. 再检查实际代码状态
6. 确认“下一步”后才继续改动

## 9. 收尾规则
一个任务只有满足以下条件，才算真正完成：

1. 目标代码或目标文档已完成
2. 相关契约或说明已同步
3. 已运行必要验证，或明确说明未验证原因
4. 已更新 `docs/project/current-status.md`
5. 若不存在中断任务，已清空或更新 `docs/project/session-handoff.md`

## 10. 严禁事项
1. 不要凭印象修改系统边界。
2. 不要一边改接口，一边不更新契约文档。
3. 不要把重构、功能扩展、基础设施升级混在同一轮里。
4. 不要留下“看起来能跑、但没人知道为什么这样写”的临时代码。
5. 不要在未记录上下文的情况下中途离场。

## 11. 当前项目阶段提醒
当前项目所处阶段以 `docs/project/current-status.md` 为准。

若该文件显示仍在“阶段 0：文档冻结与工程底座”，则在 `domain-model` 与 `api-contracts` 没冻结前，不建议大规模并行写前后端业务代码。
