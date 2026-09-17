# 独立文件处理流程

本流程随用户明确文件引用触发，不属于任何状态机 Phase。

Windows 参数路径含 `%`、`!`、`&`、`^` 等 CMD 元字符时，直接用 PowerShell 的 `-File intake.ps1` 与参数数组调用，避免 `cmd.exe` 在脚本收到路径前改写参数。

1. 使用真实路径和文件系统边界判断：当前 Task 内原地使用；工作区内但 Task 外需要复制；工作区外只复制；无活动 Task 则等待。
2. 只处理用户明确提到的字面路径，不扫描相邻文件，不展开通配符，不跟随 symlink、junction 或 reparse point。
3. 分配 `INPUT_IMPORT_ID: I-NNNN`，复制到 `<TASK_ROOT>/UserInput/<ID>/`。排除 `.git`、`.agent-state`、`.agent-work`、`.agent-protocol` 和 `tasks` 递归入口并明确报告。
4. 脚本比较相对路径、普通文件数量、字节数和 SHA-256；tree diff 非零不得输出成功。
5. `UserInput` 是只读原件。相同内容可去重；不同内容不得覆盖旧批次。
6. 工作区内、Task 外来源：成功后列出来源和目标，询问是否删除。用户同意后再次比较源/副本，只删除精确来源；变化或不一致即拒绝。
7. 工作区外来源：成功后只提醒已复制，不询问、不移动、不删除原件。

History 可在下一正常检查点引用 `INPUT_IMPORT_ID`，但导入本身不切换 Phase 或触发审批。
