# Smart Table Analysis — Release Notes / 发行说明

> **Version / 版本:** v1.0.0  
> **Release Date / 发布日期:** 2026-07-21  
> **Author / 作者:** 流风
> **License / 许可证:** MIT

---

## 🎉 Overview / 概述

**EN:** **Smart Table Analysis** is a WorkBuddy Skill that enables non-technical users to perform data analysis on Excel/CSV files using natural language. Just describe what you want to analyze, and the Skill handles the rest — from data loading to chart generation to insight reporting.

**ZH:** **智能表格分析** 是一款 WorkBuddy Skill，让非技术用户也能通过自然语言对 Excel/CSV 文件进行数据分析。只需描述你想分析什么，Skill 就会自动完成其余工作 —— 从数据加载到图表生成再到洞察报告。

---

## ✨ Features / 特性

### Core Capabilities / 核心能力

- **EN: Natural Language → Pandas** — Describe your analysis intent in plain Chinese/English; the Skill translates it into Pandas code and executes it
- **ZH: 自然语言 → Pandas** — 用中文/英文描述分析意图，Skill 自动翻译为 Pandas 代码并执行

- **EN: 9 Chart Types** — Bar, Line, Pie, Scatter, Histogram, Heatmap, Box, Area, Stacked Bar
- **ZH: 9 种图表类型** — 柱状图、折线图、饼图、散点图、直方图、热力图、箱线图、面积图、堆叠柱状图

- **EN: Multi-Sheet Excel Export** — Sheet1 = raw data + embedded charts; Sheet2 = statistical analysis (insights, group stats, correlations, outliers, group comparisons)
- **ZH: 多 Sheet Excel 导出** — Sheet1 = 原始数据 + 嵌入图表；Sheet2 = 统计分析（洞察、分组统计、相关性、异常值、组间差异）

- **EN: HTML Report** — Self-contained report with base64-embedded charts (shareable via browser)
- **ZH: HTML 报告** — 自包含报告，图表以 base64 内嵌（可通过浏览器分享）

- **EN: Follow-up Questions** — Drill down by region, compare with last month, filter by conditions — all without re-uploading data
- **ZH: 追问支持** — 按地区拆分、对比上月、筛选条件 — 无需重新上传数据

### Analysis Types / 分析类型

| Type / 类型 | Description / 描述 |
|------|-------------|
| `stats` | EN: Descriptive statistics (mean, median, std, min, max, quartiles) / ZH: 描述性统计（均值、中位数、标准差、最小值、最大值、四分位数） |
| `pivot` | EN: Pivot tables with custom rows/columns/values/aggregations / ZH: 透视表（自定义行/列/值/聚合方式） |
| `correlation` | EN: Correlation matrix with heatmap visualization / ZH: 相关性矩阵 + 热力图可视化 |
| `groupby` | EN: Group-by aggregation with multi-metric summaries / ZH: 分组聚合 + 多指标汇总 |
| `compare` | EN: Cross-group comparison (e.g., A vs B performance) / ZH: 组间对比（如 A vs B 表现） |
| `time` | EN: Time-series trend analysis with line charts / ZH: 时间序列趋势分析 + 折线图 |
| `cross` | EN: Cross-tabulation analysis / ZH: 交叉表分析 |
| `outliers` | EN: Anomaly detection using IQR or Z-score / ZH: 异常值检测（IQR 或 Z-score 方法） |
| `exec` | EN: Direct Pandas code execution (advanced) / ZH: 直接执行 Pandas 代码（高级） |

### Smart Interaction / 智能交互

- **EN: Option Generation** — After data loading, the Skill auto-generates 3-5 analysis options based on data schema, intent matching, and diversity rules
- **ZH: 选项生成** — 数据加载后，Skill 根据数据模式、意图匹配和多样性规则自动生成 3-5 个分析选项

- **EN: Confirmation Mechanism** — Before heavy analysis, the Skill restates the plan for confirmation — avoiding wasted computation on wrong analyses
- **ZH: 确认机制** — 重量级分析前，Skill 复述分析计划供确认 — 避免错误分析浪费资源

- **EN: Data-Driven Suggestions** — Options are grounded in actual column names and data types, not generic templates
- **ZH: 数据驱动建议** — 选项基于实际列名和数据类型，非通用模板

---

## 📦 Installation / 安装

### Method 1: Zip Import / 方式一：Zip 导入

1. EN: Download `smart-table-analysis.zip` / ZH: 下载 `smart-table-analysis.zip`
2. EN: In WorkBuddy, go to **Skills** → **Import Skill** / ZH: 在 WorkBuddy 中，进入 **技能** → **导入技能**
3. EN: Select the zip file / ZH: 选择 zip 文件
4. EN: The Skill appears in your skill list / ZH: Skill 出现在技能列表中

### Method 2: Manual Install / 方式二：手动安装

1. EN: Extract `smart-table-analysis.zip` to `~/.workbuddy/skills/` / ZH: 解压 `smart-table-analysis.zip` 到 `~/.workbuddy/skills/`
2. EN: Restart WorkBuddy or refresh skills / ZH: 重启 WorkBuddy 或刷新技能
3. EN: The Skill is available immediately / ZH: Skill 立即可用

### Dependencies / 依赖

```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
openpyxl>=3.1
```

EN: Install via / ZH: 安装命令：
```bash
pip install pandas numpy matplotlib openpyxl
```

---

## 🚀 Quick Start / 快速开始

### Example 1: Basic Analysis / 示例一：基础分析

```
User: 帮我分析这个销售数据表 @sales_data.xlsx
Skill: [Loads data, shows schema, generates options]
       1. 📊 按产品类别统计销售额和利润
       2. 📈 月度销售趋势分析
       3. 🔗 各数值指标相关性分析
       4. 📋 描述性统计摘要
       5. 🔍 异常值检测
User: 选1和2
Skill: [Generates pivot table, creates charts, exports to Excel]
```

### Example 2: Follow-up Drill-down / 示例二：追问下钻

```
User: 按地区拆分看看华东区的数据
Skill: [Filters data by region, re-runs analysis]
```

### Example 3: Comparison / 示例三：对比

```
User: 对比Q1和Q2的销售表现
Skill: [Groups by quarter, generates comparison charts]
```

---

## 📁 Package Structure / 包结构

```
smart-table-analysis/
├── SKILL.md                    # EN: Skill entry point & workflow definition / ZH: 技能入口与工作流定义
├── README.md                   # EN: Quick reference guide / ZH: 速查手册
├── RELEASE.md                  # EN: This file / ZH: 本文件
├── scripts/
│   ├── data_loader.py           # EN: Data loading & schema exploration / ZH: 数据加载与模式探查
│   ├── analyzer.py              # EN: Core analysis engine (9 action types) / ZH: 核心分析引擎（9种操作类型）
│   ├── chart_generator.py       # EN: Chart generation (9 chart types) / ZH: 图表生成（9种图表类型）
│   └── exporter.py              # EN: Excel/HTML export with multi-sheet support / ZH: Excel/HTML 导出（多Sheet支持）
├── references/
│   ├── analysis_workflow.md     # EN: 6-phase workflow documentation / ZH: 6阶段工作流文档
│   ├── chart_types.md           # EN: Chart type selection guide / ZH: 图表类型选择指南
│   ├── option_generation.md     # EN: Option generation rules & confirmation / ZH: 选项生成规则与确认机制
│   └── pandas_patterns.md       # EN: Common Pandas patterns reference / ZH: 常用 Pandas 模式参考
└── assets/
    └── report_template.html     # EN: HTML report template / ZH: HTML 报告模板
```

---

## 🆕 What's New in v1.0.0 / v1.0.0 新特性

### Added / 新增

- ✅ EN: Initial release with full analysis pipeline / ZH: 初始版本，完整分析流水线
- ✅ EN: 9 chart types with Chinese market conventions (red=up, green=down) / ZH: 9种图表类型，符合中国股市涨跌配色惯例（红涨绿跌）
- ✅ EN: Multi-sheet Excel export (原始数据 + 统计分析) / ZH: 多Sheet Excel导出（原始数据 + 统计分析）
- ✅ EN: Chart embedding in Excel via openpyxl / ZH: 通过 openpyxl 在 Excel 中嵌入图表
- ✅ EN: Self-contained HTML report with base64 charts / ZH: 自包含 HTML 报告，base64 内嵌图表
- ✅ EN: Natural language → Pandas code mapping / ZH: 自然语言 → Pandas 代码映射
- ✅ EN: Option generation engine (data-driven, intent-matched) / ZH: 选项生成引擎（数据驱动、意图匹配）
- ✅ EN: Confirmation mechanism before heavy analysis / ZH: 重量级分析前的确认机制
- ✅ EN: Follow-up question support (drill-down, comparison, filtering) / ZH: 追问支持（下钻、对比、筛选）
- ✅ EN: Anomaly detection (IQR and Z-score methods) / ZH: 异常值检测（IQR 和 Z-score 方法）
- ✅ EN: Correlation analysis with heatmap / ZH: 相关性分析 + 热力图
- ✅ EN: Time-series trend analysis / ZH: 时间序列趋势分析
- ✅ EN: Cross-tabulation analysis / ZH: 交叉表分析

---

## 🐛 Known Limitations / 已知限制

- EN: Files > 50MB may cause memory issues (streaming not yet implemented) / ZH: 大于 50MB 的文件可能导致内存问题（流式处理尚未实现）
- EN: Time-series analysis requires a recognizable date/datetime column / ZH: 时间序列分析需要可识别的日期/时间列
- EN: Chart embedding in Excel requires openpyxl >= 3.1 / ZH: Excel 图表嵌入需要 openpyxl >= 3.1
- EN: Chinese filename support requires UTF-8 encoding on Windows / ZH: Windows 上中文文件名需要 UTF-8 编码

---

## 📋 Roadmap / 路线图

### v1.1.0 (Planned / 计划中)

- [ ] EN: Streaming support for large files (> 100MB) / ZH: 大文件流式支持（> 100MB）
- [ ] EN: Auto date column detection & parsing / ZH: 自动日期列检测与解析
- [ ] EN: Interactive chart selection preview / ZH: 交互式图表选择预览
- [ ] EN: Export to PowerPoint with embedded charts / ZH: 导出到 PowerPoint 并嵌入图表
- [ ] EN: Statistical significance testing (t-test, chi-square) / ZH: 统计显著性检验（t检验、卡方检验）

### v2.0.0 (Planned / 计划中)

- [ ] EN: Multi-file join/merge analysis / ZH: 多文件关联/合并分析
- [ ] EN: SQL-like query interface / ZH: 类 SQL 查询接口
- [ ] EN: Custom chart template support / ZH: 自定义图表模板支持
- [ ] EN: Scheduled/automated analysis / ZH: 定时/自动化分析
- [ ] EN: Collaborative annotation & sharing / ZH: 协作标注与分享

---

## 🤝 Contributing / 贡献

EN: This Skill is built with WorkBuddy's agent-skill architecture. To contribute: / ZH: 本 Skill 基于 WorkBuddy 的 agent-skill 架构构建。贡献方式：

1. EN: Fork the Skill directory / ZH: Fork Skill 目录
2. EN: Modify scripts in `scripts/` / ZH: 修改 `scripts/` 中的脚本
3. EN: Update references in `references/` / ZH: 更新 `references/` 中的参考文档
4. EN: Test with sample data / ZH: 使用样本数据测试
5. EN: Submit changes via zip import / ZH: 通过 zip 导入提交更改

---

## 📄 License / 许可证

EN: MIT License — free to use, modify, and distribute. / ZH: MIT 许可证 — 可自由使用、修改和分发。

---

## 🔗 Links / 链接

- [WorkBuddy Documentation](https://www.codebuddy.cn/docs/workbuddy/Overview)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

---

*EN: Built with ❤️ by WorkBuddy AI — Making data analysis accessible to everyone.*  
*ZH: 由 WorkBuddy AI 用心打造 —— 让数据分析触手可及。*
