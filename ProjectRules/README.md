# ProjectRules v5

发布脚本将 `AGENTS.template.md` 渲染为 Strict Approval 与 Autonomous 两个工作区入口。把所选包的 `ProjectRules/AGENTS.md` 和隐藏 `.agent-protocol/` 合并到工作区根。

用户工具位于 `.agent-protocol/tools/`：Windows 使用 `.cmd` 入口调用 PowerShell，Linux/macOS 使用 `sh`。Python 仅用于本仓库的维护者构建和测试，不进入用户运行链路。
