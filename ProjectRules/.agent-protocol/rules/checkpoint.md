# 检查点、锁与机器验证

## 平台入口

- Windows：`.agent-protocol/tools/checkpoint.cmd ...`
- Linux/macOS：`sh .agent-protocol/tools/checkpoint.sh ...`

若 Windows 参数路径含 `%`、`!`、`&`、`^` 等 CMD 元字符，直接用 PowerShell 的 `-File checkpoint.ps1` 和参数数组调用；不要把该路径拼成 `cmd.exe` 命令文本。CMD 可能在批处理收到参数前改写参数。

两个实现必须具有相同命令、退出码、输出标记和账本字节格式。账本统一 UTF-8 无 BOM、LF、一个末尾换行；CMD 只负责调用 PowerShell，绝不处理账本内容。

## 提交顺序

1. 原子取得 `.agent-work/locks/<TASK_ID>.lock/`；失败即停止。
2. 在替换 Current 前校验路径边界、布局、字段、枚举、序号、模式关卡、所有 Ref、Case 次数和 next-state。
3. 预生成 Snapshot 与 History 所需哈希；临时文件与目标位于同一文件系统。
4. 原子替换 `current_state.md`。
5. 向唯一的 `snapshots.md` 追加完整 Current 字节；计算完整快照块实际开始/结束行号及块哈希。
6. 向 `history.md` 追加带 Plan/Decision/Case Ref 与 Snapshot 行号的索引块。
7. 脚本重新读取并验证 Current、Snapshot、History、哈希和行号一致。
8. 删除成功事务文件并释放锁。

提交支持在 Current 替换后或 Snapshot 追加后崩溃的幂等恢复。同一 ID 内容不同必须失败。锁异常时先检查事务状态，不盲目删除。

只有 `CHECKPOINT_COMMITTED` 表示成功；`verify` 必须只读并输出 `TASK_STATE_VALID`。模型不得人工补写三个生成账本。
