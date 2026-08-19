# Harness 规则文件路径核验证据

核验日期：2026-08-19（README 中所有路径结论均基于以下核验）

## ZCode（官方 zcode-configuration-guide skill）
- 用户级：`~/.zcode/AGENTS.md`（Windows: C:\Users\<用户名>\.zcode\AGENTS.md）
- 工作区级：`<repo>/AGENTS.md`（从当前目录向上查找至项目根）
- 合并顺序：用户级先注入，工作区级后注入（可收窄/覆盖默认）
- VERIFIED（官方 skill 文档）

## OpenAI Codex CLI（官方源码 + 官方文档）
- 用户级：`~/.codex/AGENTS.md`；`~/.codex/AGENTS.override.md` 优先级更高（同层二选一，取第一个非空文件）
- Windows 映射：C:\Users\<用户名>\.codex\AGENTS.md；CODEX_HOME 可整体改写
- 项目级：仓库根 AGENTS.md 被读取，从项目根向当前目录逐层拼接（越靠近当前目录越优先）
- 项目内 `.codex/AGENTS.md` 不生效（第三方说法，官方源码否认）
- config.toml：`~/.codex/config.toml`（project_doc_max_bytes 默认 32KiB 等）
- VERIFIED（github.com/openai/codex 源码 codex-rs/，docs/agents_md.md，developers.openai.com/codex/guides/agents-md）

## Claude Code（官方文档双通道：WebSearch 摘要 + 3 小时同步镜像比对）
- 用户级：`~/.claude/CLAUDE.md`（Windows: %USERPROFILE%\.claude\CLAUDE.md）
- 项目级：<项目根>/CLAUDE.md 或 <项目根>/.claude/CLAUDE.md；从启动目录向上逐级查找
- 优先级：无硬性覆盖，全部拼接；顺序 Managed → User → Project → Local
- 官方建议每文件 <200 行；无硬性截断（完整加载）
- 官方文档域名现为 code.claude.com/docs/en/memory（docs.anthropic.com 旧链 301 跳转）
- VERIFIED

## Cursor（官方帮助 + docs）
- 项目级：`.cursor/rules/*.mdc`（必须 .mdc）；`.cursorrules` 官方口径 "legacy and will be deprecated"
- 用户级主机制：Settings → Rules（云同步，推荐）
- 用户级文件：`~/.cursor/rules/*.mdc`（Windows: %USERPROFILE%\.cursor\rules\*.mdc）——官方文档确认存在，社区报告部分版本自动加载不稳定（PARTIAL）
- 优先级：Team > Project > User
- VERIFIED（PARTIAL 项已标注）

## GitHub Copilot（官方文档）
- 仓库级：`.github/copilot-instructions.md`、`.github/instructions/**/*.instructions.md`、根 AGENTS.md（两者都存在时都使用）
- 用户级 VS Code：`~/.copilot/instructions/**/*.instructions.md`
- 用户级 CLI：`$HOME/.copilot/copilot-instructions.md`（单文件）+ `$HOME/.copilot/instructions/`
- 优先级：用户级 > 仓库级 > 组织级
- VERIFIED（docs.github.com, code.visualstudio.com）

## Windsurf（官方文档，已并入 Devin）
- 项目级现代：`.devin/rules/*.md`（首选）/ `.windsurf/rules/*.md`（回退）；legacy `.windsurfrules` 仍被读取
- 用户级：`~/.codeium/windsurf/memories/global_rules.md`（单文件，上限 6000 字符）
- 根级 AGENTS.md 常驻生效
- 文档域名：docs.windsurf.com → docs.devin.ai（307 重定向）
- VERIFIED

## 撰写原则（README 采用）
- 所有路径写全：Windows 用 C:\Users\Xiaoming\...，macOS 用 /Users/Xiaoming/...，Linux 用 /home/xiaoming/...
- Claude Code 部分不写"谁覆盖谁"，写"顺序后读优先"
- Cursor 用户级推荐 Settings → Rules（云同步），文件路径标注"官方承认但部分版本加载不稳定"
- 附录给出核验日期与官方链接，提示"以官方文档为准"
