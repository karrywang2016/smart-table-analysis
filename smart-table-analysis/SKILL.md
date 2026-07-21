---
name: smart-table-analysis
description: 智能表格数据分析 Skill。让非技术同事也能做数据分析——加载 Excel/CSV 文件，通过自然语言驱动 Pandas 分析，自动生成图表和洞察报告，支持追问（按地区拆分、对比上月、筛选条件等）。当用户需要分析 Excel/CSV 数据、做透视表、VLOOKUP 关联、统计汇总、趋势分析、异常检测、生成数据报告、或提到"表格分析""数据分析""数据洞察""透视表""数据报表"时使用此 Skill。
agent_created: true
---

# 智能表格数据分析

## 概述

本 Skill 让非技术同事也能做数据分析：加载 Excel/CSV → 自然语言驱动 Pandas 分析 → 自动生成图表 + 洞察 → 支持追问迭代 → 导出报告。无需写透视表、VLOOKUP 或 SQL，用自然语言即可完成从探查到洞察的全流程。

## 触发条件

当用户表达以下意图时激活此 Skill：

- 提供了 Excel/CSV 文件并希望分析数据
- 说了类似"帮我分析这个表格""看看数据有什么规律""做个透视表""帮我做个报表"
- 说了类似"各地区销售额对比""按月看趋势""找异常值""TOP 10 排名"
- 追问分析结果："再按地区拆一下""对比上月""去掉XX的数据""换个图表"
- 要求导出分析结果："导出这个结果""生成数据报告"

## 工作流程决策树

```
用户提供数据文件？
├─ 是 → Phase 1: 加载与探查
│         → 输出数据概览和质量评估
│         → 💡 给出下一步操作选项（见下方）
│         → 等待用户选择 → 确认后执行
│
├─ 用户提出分析需求？
│   → Phase 2: 分析 + 生成选项
│   → 根据数据特征 + 用户意图，给出 3-5 个可执行操作选项
│   → 用户选择后 → 确认理解 → 开始生成
│
├─ 用户追问？
│   → 保留数据上下文，在现有结果上深化
│   → 支持：维度拆分 / 时间对比 / 条件过滤 / 图表切换 / 新分析
│
└─ 用户要导出？
    → exporter.py 导出 Excel / CSV / HTML 报告
```

## Phase 1: 数据加载与探查

### 步骤

1. 确认文件路径和格式（.xlsx/.xls/.csv/.tsv/.json/.parquet）
2. 运行 `data_loader.py` 加载文件并生成 schema 预览：

```bash
python scripts/data_loader.py <file_path> --action schema
```

可选参数：
- `--sheet <sheet_name>`：指定 Excel 的 sheet
- `--sep <separator>`：指定 CSV 分隔符
- `--encoding <encoding>`：指定编码

3. 向用户呈现数据概览，包含：
   - 文件格式和基本信息
   - 列分类（数值列 / 分类列 / 时间列 / ID列）
   - 数据质量评分（0-100）和问题列表
   - 数值列的基本统计（均值、中位数、范围）
   - 前5行数据预览

4. 如有数据质量问题（高缺失率、重复行、异常值），主动预警并给出处理建议

5. **给出下一步操作选项**（见下方「选项生成规则」），等待用户选择

### 选项生成规则

根据数据特征和用户原始提问，生成 3-5 个可执行操作选项。规则：

- **数据驱动**：选项必须基于实际存在的列和数据分布
- **意图匹配**：优先匹配用户原始提问中的关键词（"对比""趋势""排名"等）
- **多样性**：覆盖不同分析维度（分组/趋势/分布/异常/交叉）
- **具体明确**：每个选项说明"分析什么 + 用什么图表"
- **推荐标记**：最匹配用户意图的选项标记为"推荐"

### 选项格式示例

```
💡 基于你的数据，我建议以下分析方向：

1. 【推荐】按"地区"分组统计"销售额"对比 → 柱状图
2. 按"月份"查看"销售额"趋势 → 折线图
3. 按"产品类别"统计销售额占比 → 饼图
4. 查看销售额与利润的相关性 → 散点图
5. 检测销售额异常值 → 箱线图

你想做哪个？或者有其他想法？
```

### 确认机制

用户选择后，**必须复述确认**：
- 明确分析类型、目标列、分组维度、图表类型
- 例如："好的，我来按地区分组统计销售额对比，生成柱状图。开始生成..."
- 确认无误后再执行脚本

### 输出格式示例

```
📊 数据概览：sales_data.xlsx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
格式：Excel (.xlsx) | Sheet：销售明细
数据量：12,345 行 × 8 列
质量评分：87.5/100

列分类：
  数值列：销售额、利润、数量、折扣率
  分类列：地区、产品类别、渠道
  时间列：日期
  ID列：订单号

⚠️ 数据问题：
  - "折扣率"缺失率 15.3%，建议填充为 0 或删除
  - 发现 23 行重复数据，建议检查是否为正常业务数据

💡 建议分析方向：
  1. 各地区销售额对比（柱状图）
  2. 月度销售趋势（折线图）
  3. 产品类别占比（饼图）
  4. 销售额与利润的相关性（散点图）
```

## Phase 2: 自然语言分析

### 意图识别

从用户自然语言中提取四要素：

| 要素 | 说明 | 示例 |
|------|------|------|
| 分析类型 | 对比/趋势/分布/构成/关系/异常/排名 | "对比" → comparison |
| 目标列 | 哪些数值列参与分析 | "销售额" → sales_amount |
| 分组维度 | 按什么分组/拆分 | "按地区" → region |
| 过滤条件 | 是否有筛选要求 | "华东区" → filter |

### 代码生成与执行

**方式一**：使用内置分析动作（推荐，更可靠）

```bash
# 统计汇总
python scripts/analyzer.py <file> --action stats --columns <cols>

# 透视表
python scripts/analyzer.py <file> --action pivot --index <col> --pivot-columns <col> --values <col> --aggfunc mean

# 分组统计
python scripts/analyzer.py <file> --action groupby --group-col <col> --columns <cols>

# 对比分析
python scripts/analyzer.py <file> --action compare --compare-col <col> --compare-values <vals>

# 趋势分析
python scripts/analyzer.py <file> --action time --time-col <col> --value-col <col>

# 相关分析
python scripts/analyzer.py <file> --action correlation --method pearson --columns <cols>

# 异常检测
python scripts/analyzer.py <file> --action outliers --columns <cols> --method iqr

# 交叉分析
python scripts/analyzer.py <file> --action cross --col-a <col> --col-b <col> --cross-type crosstab

# 自定义 Pandas 代码执行
python scripts/analyzer.py <file> --action exec --code "<pandas_code>"
```

**方式二**：生成自定义 Pandas 代码（用于复杂查询）

参照 `references/pandas_patterns.md` 映射表生成代码。代码必须：
- 用 `result = ...` 赋值（analyzer.py 会捕获结果）
- 中文列名用 `df['列名']` 引用
- 日期列先做 `pd.to_datetime()` 转换
- 大数据集优先用 `groupby` + `agg` 避免逐行计算

### 结果解析

将 JSON 结果转为结构化文字描述，提取关键数字和洞察。如发现异常模式或显著差异，主动提示。

## Phase 3: 可视化生成

### 图表类型选择

参照 `references/chart_types.md` 的决策树选择最合适的图表类型。核心映射：

| 分析意图 | 推荐图表 | 参数 |
|---------|---------|------|
| 对比各组数据 | 柱状图 | `--chart-type bar` |
| 排名 TOP N | 水平柱状图 | `--chart-type bar --orientation horizontal --top-n N` |
| 随时间变化 | 折线图（含移动平均） | `--chart-type line` |
| 数据分布 | 直方图 | `--chart-type histogram` |
| 占比/构成 | 饼图 | `--chart-type pie --top-n 8` |
| 两变量关系 | 散点图 | `--chart-type scatter` |
| 多变量相关 | 热力图 | `--chart-type heatmap` |
| 异常值检测 | 箱线图 | `--chart-type box` |
| 多指标对比 | 分组柱状图 | `--chart-type grouped_bar` |

### 生成命令

```bash
python scripts/chart_generator.py <file> --chart-type <type> \
  --x-col <col> --y-col <col> \
  --title "<图表标题>" \
  --output <output_png_path>
```

### 配色规则

遵循中国股票市场惯例：
- 数值增加/上涨 → **红色** (#E74C3C)
- 数值减少/下跌 → **绿色** (#27AE60)
- 金融数据对比必须遵守此规则
- 非金融数据使用蓝绿色系默认配色

### 图表标题命名

格式：`[分析维度] × [指标] — [分析类型]`
示例：`地区 × 销售额 — 对比分析`、`时间 × 订单量 — 趋势走势`

## Phase 4: 洞察提炼

每项分析完成后，自动提炼关键洞察。格式：

```
📊 [洞察标题]
   数据支撑：[具体数字，含百分比/对比值]
   业务含义：[解读这个数字意味着什么]
   建议：[下一步行动或深入方向]
```

洞察优先级：
- **P0**：强异常（数据缺失>30%、完全偏斜、矛盾数据）
- **P1**：显著差异（组间差异>50%、强相关性>0.7、趋势拐点）
- **P2**：一般发现（趋势方向、分布特征、占比情况）

## Phase 5: 追问处理

支持迭代追问，保留数据上下文（已加载文件、已分析列、已生成图表）。

| 追问示例 | 处理方式 |
|---------|---------|
| "再按地区拆一下" | 在现有 groupby 结果上添加维度，或重新 groupby |
| "对比上月" | 计算环比（与前一月对比），生成对比柱状图 |
| "对比去年同月" | 计算同比（与去年同月对比） |
| "去掉XX的数据" | 添加过滤条件后重新执行 |
| "只看华东区" | 添加 df[df['地区']=='华东'] 筛选 |
| "换个图表类型" | 切换 chart_type 重新生成 |
| "导出这个结果" | 调用 exporter.py 导出 |
| "TOP 10 是什么" | 添加 `.nlargest(10, col)` 或 `--top-n 10` |
| "加一个移动平均" | 添加 `.rolling(7).mean()` 计算 |
| "两个表关联一下" | pd.merge 操作（VLOOKUP类） |
| "这个异常值怎么回事" | 用 outliers 动作详细检测 |

追问时无需重新加载文件，直接在已加载的 DataFrame 上操作。

## Phase 6: 结果导出

支持三种导出格式：Excel（多 Sheet + 嵌入图表）、CSV、HTML 报告。

#### Excel 导出（推荐）

多 Sheet 结构：
- **Sheet1「原始数据」**：完整数据表 + 嵌入的可视化图表
- **Sheet2「统计分析」**：自动生成的统计汇总（含数据洞察、分组统计、相关性分析、异常值检测等）

```bash
# 导出为 Excel（含统计汇总 + 嵌入图表）
python scripts/exporter.py <file> --action excel --output <path> \
  --analysis-data '<analysis_json>' \
  --insights '<insights_json>' \
  --charts '<charts_json>'
```

`--charts` 参数格式（JSON 数组）：
```json
[
  {"path": "chart1.png", "title": "图表标题1", "description": "图表说明1"},
  {"path": "chart2.png", "title": "图表标题2", "description": "图表说明2"}
]
```

Excel 导出时，图表会直接嵌入到 Sheet1 数据表下方，Sheet2 自动包含统计分析结果。

HTML 报告模板位于 `assets/report_template.html`，使用 `scripts/exporter.py` 的 `generate_html_report()` 函数生成完整报告。

## 资源说明

### scripts/

- **data_loader.py** — 加载 Excel/CSV/JSON/Parquet 文件，检测列类型，评估数据质量，生成 schema 预览
- **analyzer.py** — 核心分析引擎：统计汇总、透视表、分组统计、对比分析、趋势分析、相关分析、异常检测、交叉分析，以及自定义 Pandas 代码安全执行
- **chart_generator.py** — 图表生成器：支持柱状图、折线图、饼图、散点图、热力图、直方图、箱线图、分组柱状图、面积图，遵循中国涨红跌绿配色惯例
- **exporter.py** — 导出工具：Excel（多Sheet：原始数据+统计分析，自动嵌入图表）、CSV（带BOM）、HTML 报告（含图表+洞察+统计+预览）

### references/

- **pandas_patterns.md** — 自然语言 → Pandas 代码映射表，覆盖查询、聚合、透视、VLOOKUP、筛选、排序、时间、清洗等场景
- **chart_types.md** — 分析意图 → 图表类型选择指南，含决策树和配置最佳实践
- **analysis_workflow.md** — 完整分析流程参考，6个阶段的详细步骤和错误处理
- **option_generation.md** — 选项生成规则与确认机制，确保分析前与用户对齐

### assets/

- **report_template.html** — HTML 报告模板，美观的数据分析报告布局

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件格式不支持 | 提示支持的格式列表（xlsx/xls/csv/tsv/json/parquet），建议转换 |
| 列名不存在 | 显示实际列名列表，让用户选择正确列名 |
| Pandas 代码执行报错 | 捕获错误信息，自动修正后重试（最多3次） |
| 内存不足 | 建议先筛选/采样再分析，或减少分析列数 |
| 中文编码问题 | 自动尝试 utf-8-sig / gbk / gb18030 |
| 图表生成失败 | 降级为纯文字描述，提示可能原因 |

## 执行环境要求

- Python 3.11+ 及以下包：pandas, numpy, matplotlib, openpyxl
- 所有脚本使用 WorkBuddy managed Python 环境执行
- 图表输出为 PNG，通过 present_files 展示给用户
- HTML 报告输出为 .html，通过 present_files 展示并自动预览
