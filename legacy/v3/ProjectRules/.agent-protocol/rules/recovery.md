# 压缩、中断与记录修复

## 正常恢复

1. 优先使用用户提供的 `TASK_ID` 或 current_state 路径。否则完整读取 `.agent-work/active.md`；缺失或不匹配时再搜索 task_index 的 `SUBJECT`、`STATUS` 和 `TASK_ID`。
2. 完整读取目标任务的 `current_state.md`。确认 Schema、TASK_ID、STATUS、PLAN_REF、ACTIVE_STEP、LAST_EVENT_ID、LAST_SNAPSHOT 和 RESUME_MODE。
3. 检查 LAST_SNAPSHOT 存在；在 history 中精确搜索 `^EVENT_ID: <LAST_EVENT_ID>$`，只读取对应 BEGIN/END 块。三者不一致时先执行“记录修复”。
4. `PLAN_REF` 不为 NONE 时，在 plan.md 精确搜索该 PLAN_REF，只读取对应 PLAN_REVISION 块。不要全文读取 plan.md。
5. 从 current_state 的“下一步与验收条件”“关键路径”确定相关实际文件、后台任务或远端状态，进行低成本核对。状态与实际结果冲突时，以新证据修正并保存 `RECOVERY_REPAIR`。
6. 读取项目入口路由中下一动作所需、且当前上下文缺失的规则。不要全量加载规则目录、历史、旧快照、旧计划或长日志。
7. 外部动作处于 UNKNOWN/执行中时先查询结果，不重复执行。用户明确说继续且没有新的授权缺口时直接恢复工作，不再次确认。
8. 恢复后的下一个正常检查点将 `RESUME_MODE` 更新为 NORMAL；无需仅为改字段创建空事件。可在开始实质工作时保存 `RESUMED`，只有它对交接确有价值时才记录。

## Search First / Read Narrow

- 搜索稳定字段，不只搜索自然语言：`EVENT_ID`、`PLAN_REF`、`STEP_ID`、`EVENT_TYPE`、`STATUS`、`TASK_ID`、`TAGS`。
- 使用行号定位后，从最近对应 BEGIN 读到 END。多个命中必须分别检查块头，不能拼接。
- 历史只在需要解释某个决定、失败路线、验收证据或修复记录时读取对应事件；正常恢复不读取全部 history。
- 快照只在 current_state 损坏、记录不一致、用户要求审计或需要还原某时点事实时读取。
- 搜索失败先检查路径、大小写、Schema 版本和转义；不要立即得出“记录不存在”。

## 记录修复

只修复能由现有文件和实际证据确认的记录，不补造历史：

- **current_state 有效，快照缺失**：核对状态引用及项目结果后，以当前状态补同 ID 快照；如 history 已存在，确认其字段一致；保存新 `RECOVERY_REPAIR` 事件说明修复。
- **current_state 与快照有效，history 缺事件**：按两者和实际证据补原 EVENT_ID 事件，防止重复后再追加一个后续 `RECOVERY_REPAIR`；不重执行业务步骤。
- **current_state 损坏或缺失**：依次检查 current_state.prev、history 中最后一个结构完整事件所指快照和 plan。选择最近可验证状态恢复，再核对该时点之后的实际文件和外部结果。
- **存在 current_state.next**：它表示可能未提交的写入，只能作为调查线索。检查字段、EVENT_ID、快照/history 以及实际证据后决定完成提交或保留旧状态；不能直接覆盖更新的用户修改。
- **同一 ID 对应不同内容**：暂停该任务的冲突写入，列出文件和差异。继续不受影响的只读调查；无法确定归属时请用户裁决。
- **索引过时**：active 和 task_index 是指针，不覆盖任务状态。根据有效 current_state 追加修正索引事件，不修改旧索引块。

## 事实与授权恢复

- 旧状态中的授权只适用于当时记录的对象、动作和范围。新成本、新接收者、新数据类别或破坏性影响需要重新判断。
- 计划中写了某动作不代表动作已经发生；history 写了 INTENT 也不代表成功。使用 EXTERNAL_RESULT、收据或远端状态确认。
- 用户最新明确指令优先于旧计划普通约束；发生实质目标变化时按 lifecycle.md 创建计划修订，不静默改写历史。
