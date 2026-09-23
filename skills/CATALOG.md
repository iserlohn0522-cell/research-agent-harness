# 技能清单

技能（skill）是一个文件夹，里面的 `SKILL.md` 告诉 agent 遇到哪类任务、按什么步骤做。装上以后，agent 只在任务对得上时才读它。每装一个技能，每次对话开头都会多加载一段技能说明，所以只装常用的，以后随时可以再加。

这里列的是作者实际在用、对各领域科研都有用的技能。除了本仓库自带的 `drawio`，都从原作者的公开仓库安装，保留原作者的许可文件。来源和插件名核对于 2026-09-23。

## 装在哪里

| 工具 | 所有项目都能用 | 只给某一个项目用 |
|---|---|---|
| Codex | `~/.agents/skills/<名字>/` | `<项目>/.agents/skills/<名字>/` |
| Claude Code | `~/.claude/skills/<名字>/`，或装成插件（见下表最后一列） | `<项目>/.claude/skills/<名字>/` |

两个工具都用时，同一个技能两边各放一份。

## 怎么装（给 agent 看）

- 单个技能：`git clone --depth 1 https://github.com/<仓库>` 到临时目录，把表中列出的文件夹整个复制到目标位置（连同仓库里的 LICENSE），再删掉临时目录。上游仓库自己写了安装说明的，参考它决定复制哪些文件；安装位置一律按上面“装在哪里”的表。有的上游说明让 Codex 装到 `~/.codex/skills/`，那是 Codex 较早版本的位置，现在 Codex 从 `~/.agents/skills/` 读取技能。
- Claude Code 插件：`claude plugin marketplace add <仓库>`，再 `claude plugin install <插件>@<市场>`；在 Claude Code 里也可以用 `/plugin` 命令。一个插件装一组技能，以后更新也方便。
- 本仓库自带的 `drawio`：从本仓库的 `skills/drawio/` 复制。

## 写论文与润色

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| research-paper-writing | ML/CV/NLP 论文各节的写法（摘要、引言、相关工作、方法、实验）和段落衔接 | Master-cai/Research-Paper-Writing-Skills → `research-paper-writing` | MIT | — |
| humanizer | 去掉文字里的“AI 腔” | blader/humanizer → 仓库根目录 | MIT | `humanizer@humanizer` |
| stop-slop | 同上，规则更短 | hardikpandya/stop-slop → 仓库根目录 | MIT | — |
| scientific-writing | 科研论文写作流程：结构、引用、图表说明 | K-Dense-AI/scientific-agent-skills → `skills/scientific-writing` | MIT | — |
| nature-writing、nature-polishing、nature-figure 等 | 按 Nature 系期刊的风格写作、润色、作图；共用的 `nature-shared` 要一起装 | Yuan1z0825/nature-skills → `skills/<名字>` | Apache-2.0 | — |
| doc-coauthoring | 按步骤和人合写文档 | anthropics/skills → `skills/doc-coauthoring` | Apache-2.0 | `example-skills@anthropic-agent-skills` |

## 文献与调研

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| 学术研究套件（ARS） | 深度调研、论文写作流水线、模拟审稿 | Imbad0202/academic-research-skills → `academic-paper`、`academic-paper-reviewer`、`academic-pipeline`、`deep-research` | CC BY-NC 4.0（仅限非商业使用） | `academic-research-skills@academic-research-skills` |
| Deep-Research-skills | 结构化深度调研：先定提纲，再逐项查证，最后写报告；有中文版和 Codex 专用版 | Weizhena/Deep-Research-skills → Claude Code 用 `skills/research-zh`，Codex 用 `skills/research-codex-zh`，按该仓库说明安装 | MIT | — |
| literature-review、paper-lookup、research-lookup | 文献综述、按主题或标识查论文 | K-Dense-AI/scientific-agent-skills → `skills/<名字>` | MIT | — |

## 数据分析与批判性思考

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| exploratory-data-analysis | 拿到新数据先做探索性分析：分布、缺失、异常、相关性 | K-Dense-AI/scientific-agent-skills → `skills/exploratory-data-analysis` | MIT | — |
| scientific-critical-thinking | 评估一个结论的论证和证据强不强 | K-Dense-AI/scientific-agent-skills → `skills/scientific-critical-thinking` | MIT | — |
| jupyter-notebook（Codex） | 创建和编辑 notebook | openai/skills → `skills/.curated/jupyter-notebook` | Apache-2.0 | — |

## 计划与讨论

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| grill-me、grilling | 让 agent 连续追问，把一个计划或设计想清楚 | mattpocock/skills → `skills/productivity/grill-me`、`skills/productivity/grilling` | MIT | `mattpocock-skills@mattpocock`（整套，含其他工程类技能） |

## 文档、表格、幻灯片、PDF

| 技能 | 做什么 | 来源 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| docx、xlsx、pptx、pdf（Claude Code） | 读写 Word、Excel、PowerPoint、PDF | anthropics/skills。Anthropic 专有许可：只通过插件安装，不要从别处复制这几个文件夹 | Anthropic 专有 | `document-skills@anthropic-agent-skills` |
| Documents、Spreadsheets、Presentations、PDF（Codex） | 同上 | Codex 应用自带的插件，在应用的插件页打开即可，不用装技能 | — | — |

## 画图与网页

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| drawio | 画可编辑的 draw.io 图：流程图、架构图、时序图等 | 本仓库 `skills/drawio` | 本仓库作者所写，没有单独的许可文件 | — |
| frontend-design、web-artifacts-builder、webapp-testing | 做网页界面；用 Playwright 测试本地网页 | anthropics/skills → `skills/<名字>` | Apache-2.0 | `example-skills@anthropic-agent-skills` |
| ui-ux-pro-max | 界面设计参考：配色、字体、组件风格 | nextlevelbuilder/ui-ux-pro-max-skill → `.claude/skills/ui-ux-pro-max` | MIT | `ui-ux-pro-max@ui-ux-pro-max-skill` |
| canvas-design、algorithmic-art、theme-factory | 海报和示意图、生成式图案、统一配色主题 | anthropics/skills → `skills/<名字>` | Apache-2.0 | `example-skills@anthropic-agent-skills` |
| playwright（Codex） | 浏览器自动化 | openai/skills → `skills/.curated/playwright` | Apache-2.0 | — |

## 开发与工具

| 技能 | 做什么 | 来源：仓库 → 文件夹 | 许可 | Claude Code 插件 |
|---|---|---|---|---|
| mcp-builder、skill-creator | 写 MCP 服务器；写新技能 | anthropics/skills → `skills/<名字>` | Apache-2.0 | `example-skills@anthropic-agent-skills` |
| claude-api | 用 Claude API 和 Anthropic SDK 写程序 | anthropics/skills → `skills/claude-api` | 见该文件夹 | `claude-api@anthropic-agent-skills` |
| tmux | 通过 tmux 操作交互式命令行，例如盯集群上的长任务 | openclaw/openclaw → `skills/tmux` | 见该仓库 | — |
| find-skills | 按需求搜索、发现更多技能 | vercel-labs/skills → `skills/find-skills` | MIT | — |
| web-access（Claude Code） | 让 Claude Code 联网搜索、抓网页、操作浏览器 | eze-is/web-access → 仓库根目录 | MIT（技能文件内注明） | `web-access@web-access` |

Codex 自带 openai-docs、imagegen 等几个系统技能，不用另装。

## Codex 应用插件

不用装技能，在 Codex 应用的插件页打开即可：GitHub、Documents、Spreadsheets、Presentations、PDF、Hugging Face、Browser、Computer Use；需要时再开 Gmail、Google Drive 这类连接账号的插件。

## 没有收录的

作者还有几个材料化学计算方向（VASP、DFT、催化分析）和个人写作、幻灯片风格的技能，含个人资料或与计算机科学无关，没有放进来。
