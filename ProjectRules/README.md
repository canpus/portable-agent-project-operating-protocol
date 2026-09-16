# 共用项目规则源文件

本目录是 v4 两个状态机包的共用源，不能直接整目录复制安装。

- `AGENTS.template.md`：构建时根据 profiles 配置生成唯一入口 `ProjectRules/AGENTS.md`。
- `.agent-protocol/`：两种模式共用的契约、恢复和执行规则，包含两个按需加载的治理文件。
- `profiles/plan-approval.json` 与 `profiles/task-delegation.json` 位于仓库根，决定各包的模式和记录默认值。

普通用户从三个 ZIP 中选择一个。状态机用户把 ZIP 内 ProjectRules 的内容复制到目标项目根，安装后只能有一个项目入口。不要把未替换的入口模板装进项目。
