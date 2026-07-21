# 智能表格数据分析 Skill

> 让非技术同事也能做数据分析——加载 Excel/CSV → 自然语言驱动 Pandas 分析 → 自动生成图表 + 洞察 → 支持追问迭代 → 导出报告。

## 📁 目录结构

```
smart-table-analysis/
├── SKILL.md                          # 完整指令文件（AI 执行入口）
├── README.md                         # 本文件（功能速查）
├── assets/
│   └── report_template.html           # HTML 报告模板
├── references/
│   ├── pandas_patterns.md             # 自然语言 → Pandas 代码映射表
│   ├── chart_types.md                 # 图表类型选择决策树
│   ├── analysis_workflow.md           # 6阶段分析流程参考
│   └── option_generation.md           # 选项生成规则与确认机制
└── scripts/
    ├── data_loader.py                 # 数据加载与探查
    ├── analyzer.py                    # 核心分析引擎
    ├── chart_generator.py             # 图表生成器
    └── exporter.py                    # 导出工具（Excel/CSV/HTML）
```

## 🎯 核心功能

| 功能 | 说明 |
|------|------|
| **数据加载** | 支持 Excel/CSV/TSV/JSON/Parquet，自动检测编码和分隔符 |
| **数据探查** | 列分类（数值/分类/时间/ID）、数据质量评分、缺失率统计 |
| **自然语言分析** | 用户说人话，AI 自动生成 Pandas 代码执行 |
| **统计分析** | 描述性统计、分组聚合、透视表、相关性、异常检测 |
| **可视化** | 9种图表类型，遵循中国涨红跌绿配色惯例 |
| **追问迭代** | 支持连续对话，保留数据上下文 |
| **报告导出** | Excel（多Sheet+嵌入图表）、CSV、HTML（base64内嵌图表） |

## 🚀 触发条件

当用户表达以下意图时激活：

- 提供了 Excel/CSV 文件并希望分析数据
- 说了类似"帮我分析这个表格""做个透视表""帮我做个报表"
- 说了类似"各地区销售额对比""按月看趋势""找异常值""TOP 10 排名"
- 追问分析结果："再按地区拆一下""对比上月""去掉XX的数据"
- 要求导出分析结果："导出这个结果""生成数据报告"

## 🔄 工作流程（6阶段）

```
用户提供数据文件
    ↓
Phase 1: 加载与探查
    → 展示数据概览 + 质量评估
    → 💡 给出 3-5 个分析选项（基于数据特征）
    → 用户选择 → 复述确认
    ↓
Phase 2: 自然语言分析
    → 意图识别（分析类型/目标列/分组维度/图表类型）
    → 生成 Pandas 代码 → 沙箱执行
    ↓
Phase 3: 可视化生成
    → 自动选择图表类型 → 生成 PNG
    ↓
Phase 4: 洞察提炼
    → P0/P1/P2 分级洞察
    → 数据支撑 + 业务含义 + 建议
    ↓
Phase 5: 追问处理
    → 保留上下文，支持维度拆分/时间对比/条件过滤/图表切换
    ↓
Phase 6: 结果导出
    → Excel（多Sheet+嵌入图表）/ CSV / HTML
```

## 📜 脚本说明

### `data_loader.py` — 数据加载与探查

```bash
python scripts/data_loader.py <file> --action schema
```

| 参数 | 说明 |
|------|------|
| `--action schema` | 完整概览（列信息+质量+统计+预览） |
| `--action head` | 前10行数据 |
| `--action quality` | 仅数据质量 |
| `--action columns` | 仅列类型 |
| `--sheet <name>` | 指定 Excel sheet |
| `--sep <sep>` | CSV 分隔符 |
| `--encoding <enc>` | 文件编码 |

### `analyzer.py` — 核心分析引擎

```bash
# 统计汇总
python scripts/analyzer.py <file> --action stats --columns <cols>

# 透视表
python scripts/analyzer.py <file> --action pivot --index <idx> --pivot-columns <col> --values <val> --aggfunc mean

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

# 自定义 Pandas 代码
python scripts/analyzer.py <file> --action exec --code "<pandas_code>"
```

### `chart_generator.py` — 图表生成器

```bash
python scripts/chart_generator.py <file> --chart-type <type> \
  --x-col <col> --y-col <col> \
  --title "<图表标题>" --output <path.png>
```

| 图表类型 | 参数 | 适用场景 |
|---------|------|---------|
| 柱状图 | `--chart-type bar` | 对比各组数据 |
| 水平柱状图 | `--chart-type bar --orientation horizontal --top-n N` | 排名 TOP N |
| 折线图 | `--chart-type line` | 随时间趋势 |
| 饼图 | `--chart-type pie --top-n 8` | 占比/构成 |
| 散点图 | `--chart-type scatter` | 两变量关系 |
| 热力图 | `--chart-type heatmap --corr-data JSON` | 多变量相关矩阵 |
| 直方图 | `--chart-type histogram --bins 30` | 数据分布 |
| 箱线图 | `--chart-type box` | 异常值检测 |
| 分组柱状图 | `--chart-type grouped_bar` | 多指标对比 |
| 面积图 | `--chart-type area` | 趋势+范围 |

### `exporter.py` — 导出工具

```bash
# Excel（多Sheet + 嵌入图表）
python scripts/exporter.py <file> --action excel --output <path> \
  --analysis-data '<json>' --insights '<json>' --charts '<json>'

# CSV（带BOM）
python scripts/exporter.py <file> --action csv --output <path>

# HTML（base64内嵌图表）
python scripts/exporter.py <file> --action html --output <path> \
  --analysis-data '<json>' --insights '<json>' --charts '<json>'
```

`--charts` 参数格式：
```json
[
  {"path": "chart1.png", "title": "图表标题1", "description": "说明1"},
  {"path": "chart2.png", "title": "图表标题2", "description": "说明2"}
]
```

Excel 输出结构：
- **Sheet1「原始数据」**：完整数据表 + 嵌入的图表
- **Sheet2「统计分析」**：数据洞察 + 分组统计 + 相关性 + 异常值 + 组间差异

## 📚 参考文档

| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `pandas_patterns.md` | 自然语言→Pandas 映射表（查询/聚合/透视/VLOOKUP/筛选/排序/时间/清洗） | 生成自定义分析代码时 |
| `chart_types.md` | 分析意图→图表类型决策树 + 配置最佳实践 | 选择图表类型时 |
| `analysis_workflow.md` | 6阶段完整流程 + 错误处理 | 执行完整分析流程时 |
| `option_generation.md` | 选项生成规则 + 确认机制 | Phase 1 完成后生成选项时 |

## 💡 使用示例

### 示例 1：基础分析

```
用户：帮我分析 sales_data.xlsx
AI：[加载数据] → 展示数据概览 → 给出选项
用户：第1个，按地区对比销售额
AI：[确认] → 执行分组统计 → 生成柱状图 → 展示洞察
```

### 示例 2：透视表

```
用户：帮我做个透视表，行是地区，列是产品，值是销售额
AI：[确认] → 执行 pivot → 生成图表 → 展示结果
```

### 示例 3：追问迭代

```
用户：再按月份拆一下
AI：[保留上下文] → 添加月份维度 → 重新执行 → 展示新图表
```

### 示例 4：导出报告

```
用户：导出成 Excel，要有图表
AI：[生成图表] → 导出 Excel（Sheet1 数据+图表，Sheet2 统计）
```

## ⚠️ 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件格式不支持 | 提示支持的格式列表，建议转换 |
| 列名不存在 | 显示实际列名，让用户选择 |
| Pandas 代码执行报错 | 捕获错误信息，自动修正后重试（最多3次） |
| 内存不足 | 建议先筛选/采样再分析 |
| 中文编码问题 | 自动尝试 utf-8-sig / gbk / gb18030 |
| 图表生成失败 | 降级为纯文字描述 |

## 🔧 执行环境

- **Python**：3.11+（推荐 WorkBuddy managed 3.13.12）
- **依赖包**：pandas, numpy, matplotlib, openpyxl
- **执行路径**：`C:\Users\wangsen\.workbuddy\binaries\python\envs\default\Scripts\python.exe`

## 📝 注意事项

1. **沙箱执行**：所有 Pandas 代码在受限环境中执行，仅允许安全操作
2. **中文列名**：生成代码时用 `df['列名']` 而非 `df.列名`
3. **日期列**：分析前先做 `pd.to_datetime()` 转换
4. **大数据集**：优先用 `groupby` + `agg` 避免逐行计算
5. **图表配色**：金融数据遵循中国惯例（涨红跌绿），非金融数据用蓝绿色系
