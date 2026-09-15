# legacy/v1 — 旧版规则归档

本目录保存 v0.2.0 及更早版本的项目规则原文，仅供旧版对照与历史追溯。

## 内容

```text
legacy/v1/ProjectRules/
├── OPERATING_RULES.md      # 旧版触发纪律层（WHEN-THEN 条件触发规则）
├── TASK_STATE_MACHINE.md   # 旧版任务状态机（状态、门控、恢复协议）
└── SCHEMA.md               # 旧版数据契约（plan / current_state / history / 索引 / 登记）
```

## 重要说明

- **这些文件不是当前执行入口。** 当前项目规则的唯一入口是仓库根目录的 `ProjectRules/AGENTS.md`，其下 `.agent-protocol/` 保存详细规则、记录契约与模板。
- **不要让两套入口同时生效。** v3 的规则结构与旧版不兼容，同时加载可能产生重复审批、重复写入和状态冲突。
- 旧版的 `ProjectRules/AGENTS.md`（宪法层）与 `GlobalRules/AGENTS.md` 未在此归档：前者已被 v3 入口取代，后者的 v3 版本仍在仓库根目录 `GlobalRules/` 中。

迁移说明见：

- 根目录 `CHANGELOG.md` 的 `3.0.0` 章节（重构目的、新增、破坏性兼容变化、迁移步骤）；
- 根目录 `README.md` 第 17 节“从旧版升级”。
