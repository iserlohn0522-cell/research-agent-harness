# research-agent-harness 接手入口

更新：2026-10-05。变化记录见 [10 月记录](log/2026-10.md)。

## 这是什么

可分享、可安装的 Codex / Claude Code 通用研究配置，采用 MIT 许可。人的使用说明见 `README.md`，执行安装的 agent 读 `INSTALL.md`。

## 当前状态

当前载荷使用工作区规范 v1.4：入口只负责指路，同版规则复用，按实质变化记录，任务简报明确读取与授权边界。简报模板与回复示例已列入安装步骤。通用模板使用安装时替换的路径占位符。

## 下一步

安装或更新按 `INSTALL.md`；维护时按 `AGENTS.md`，检查脱敏边界、模板与工作区，再记录到 `log/`。临时安装验证已覆盖占位符替换和工作区 init/task/check；其他使用者电脑上的实装仍待反馈。

## 东西在哪

- `profile/`、`codex/`、`claude/`、`skills/`：可分发载荷。
- `INSTALL.md`：安装步骤；`README.md`：介绍；`log/`：版本变化。
- 维护者任务目录 `work/` 不发布。
