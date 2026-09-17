# 安装 v5.0.1

## 选择包

- GlobalRules Only：不需要状态机。
- Strict Approval：Requirements、Goal、每个 Stage Plan 和 Delivery 都有人类审查点。
- Autonomous：Task 授权后持续推进，只在关键决定、具体授权或用户关卡等待。

## 安装

1. 将 `GlobalRules/` 的完整内容（含 `.agent-rules/`）合并到宿主支持的全局规则位置；已有规则先备份并人工合并。
2. 状态机包还需把 `ProjectRules/AGENTS.md` 与 `ProjectRules/.agent-protocol/` 合并到工作区根，不要保留 `ProjectRules` 外壳层。
3. 工作区 `.gitignore` 最小加入：

```gitignore
.agent-work/
tasks/*/.agent-state/
```

4. 每个 Task 若是独立 Git 仓库，其自己的 `.gitignore` 还要加入 `.agent-state/`。

## 平台工具

- Windows：普通路径可用 `checkpoint.cmd`、`intake.cmd`。CMD 入口优先使用 PowerShell 7，未安装时回退到系统 Windows PowerShell 5.1；两者都以进程级 ExecutionPolicy Bypass 调用随包脚本，不修改机器或用户策略。参数路径含 `%`、`!`、`&`、`^` 等 CMD 元字符时，应由 PowerShell 直接以 `-File checkpoint.ps1` / `-File intake.ps1` 和参数数组调用，避免 `cmd.exe` 在脚本收到参数前改写参数。
- Linux/macOS：`sh checkpoint.sh`、`sh intake.sh`，无需执行位。

安装后先运行空 Task 的 `init` 与 `verify`，再执行 [行为检查](BEHAVIOR_CHECKS.md)。文件存在不能证明宿主已经加载 AGENTS，应让 Agent 复述当前模式、四个严格关卡或自主授权边界。

> **`.agent-state/` 默认不进入 Git。PAPOP 不自动备份；复制或迁移 Task 时必须显式包含隐藏目录。**
