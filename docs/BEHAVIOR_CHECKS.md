# v5.0.0 行为检查

1. 新 Task 目录即项目根，并冻结工作区模式；替换工作区 AGENTS 不改变旧 Task。
2. 新对话继续项目时增加 Session，不新建 Task；交付周期增加 Stage。
3. 严格模式不能跳过 Requirements、Goal、Plan、Delivery 四个精确审查点；任一拒绝进入对应返工。
4. Plan R1 批准不能授权 R2；Delivery R1 验收不能关闭返工后的 R2。
5. Stage 只有当前 Delivery 验收后才能 `STAGE_CLOSED`，然后才写下一 Stage Plan。
6. 自主模式能连续执行常规步骤，但不会跨越具体外部授权、用户关卡或 Goal 变化。
7. 两个写入者竞争同一 Task 时只有一个取得锁。
8. 分别在 Current 替换后、Snapshot 追加后中断；同一事务重跑不产生重复块。
9. History 行号精确截取 Snapshot 完整块，块哈希与 State 哈希均匹配。
10. 同一确认根因第三次出现才建议 Case；未获用户批准不创建。升格后原 Case 和 History 引用仍有效。
11. 每步开始和恢复只读三层 Case index；触发匹配才读详情。
12. 工作区内 Task 外输入复制验证后询问删除；工作区外输入只复制并提醒；当前 Task 内不重复复制。
13. intake 拒绝 symlink/junction、状态目录、`.git` 和递归 `tasks`；tree diff 非零不声称成功。
14. PowerShell 5.1、PowerShell 7 与 POSIX Shell 对黄金夹具生成相同账本字节。
15. Markdown/JSON/PS1/SH 为 LF，无 BOM；CMD 为 CRLF；源树和 ZIP 解压后均无混合换行。
