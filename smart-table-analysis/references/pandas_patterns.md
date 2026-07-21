# Pandas 操作模式参考

## 自然语言 → Pandas 映射表

### 基础查询

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "看看数据长什么样" | `df.head()` / `df.info()` | 预览数据和结构 |
| "有多少行/多少列" | `df.shape` | 返回 (行数, 列数) |
| "各列的数据类型" | `df.dtypes` | 列类型信息 |
| "有没有缺失值" | `df.isnull().sum()` | 各列缺失统计 |
| "显示所有列名" | `df.columns.tolist()` | 列名列表 |

### 聚合统计

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "各列的平均值" | `df.mean()` | 全列均值 |
| "某列的均值/中位数/最大值" | `df[col].agg(['mean','median','max'])` | 多指标聚合 |
| "按XX分组统计均值" | `df.groupby(col).mean()` | 分组聚合 |
| "按XX分组，统计YY的总量/均值/数量" | `df.groupby(col)[val].agg(['sum','mean','count'])` | 多函数聚合 |
| "各地区的总销售额排名" | `df.groupby('地区')['销售额'].sum().sort_values(ascending=False)` | 分组+排序 |

### 透视表

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "做一个透视表，行是地区，列是产品，值是销售额" | `pd.pivot_table(df, index='地区', columns='产品', values='销售额', aggfunc='sum')` | 标准透视表 |
| "按地区和年份交叉统计" | `pd.pivot_table(df, index='地区', columns='年份', aggfunc='count')` | 计数透视 |
| "多指标透视表" | `pd.pivot_table(df, index='地区', values=['销售额','利润'], aggfunc={'销售额':'sum','利润':'mean'})` | 不同聚合函数 |

### VLOOKUP 类操作

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "把两个表按ID关联" | `pd.merge(df1, df2, on='ID', how='left')` | 类似 VLOOKUP |
| "左连接/右连接/全连接" | `how='left'/'right'/'outer'/'inner'` | 不同连接方式 |
| "用多列做关联" | `pd.merge(df1, df2, on=['地区','月份'], how='left')` | 多列关联 |

### 筛选过滤

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "销售额大于1000的记录" | `df[df['销售额'] > 1000]` | 数值条件 |
| "北京地区的数据" | `df[df['地区'] == '北京']` | 文本条件 |
| "销售额前10名" | `df.nlargest(10, '销售额')` | TOP N |
| "最近7天的数据" | `df[df['日期'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]` | 时间条件 |
| "多条件筛选" | `df[(df['地区']=='北京') & (df['销售额']>1000)]` | 组合条件 |

### 排序

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "按销售额从高到低排" | `df.sort_values('销售额', ascending=False)` | 降序 |
| "按地区和销售额排序" | `df.sort_values(['地区','销售额'], ascending=[True, False])` | 多级排序 |

### 时间分析

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "按月汇总销售额" | `df.groupby(df['日期'].dt.month)['销售额'].sum()` | 月度汇总 |
| "同比增长率" | `(current - last_year) / last_year * 100` | 同比 |
| "环比增长率" | `(current - last_month) / last_month * 100` | 环比 |
| "7日移动平均" | `df['销售额'].rolling(7).mean()` | 移动平均 |
| "季度汇总" | `df.groupby(df['日期'].dt.quarter).sum()` | 季度汇总 |

### 数据清洗

| 用户意图 | Pandas 代码模式 | 说明 |
|---------|----------------|------|
| "去掉重复行" | `df.drop_duplicates()` | 去重 |
| "填充缺失值为0" | `df.fillna(0)` | 缺失填充 |
| "删除缺失超过30%的列" | `df.dropna(axis=1, thresh=int(len(df)*0.7))` | 阈值删除 |
| "替换异常值为中位数" | `df[col] = df[col].clip(lower, upper)` | 截断 |
| "字符串列去空格" | `df[col] = df[col].str.strip()` | 清理字符串 |

### 生成代码时的注意事项

1. **始终用 `result = ...` 赋值**，让 analyzer.py 的 `safe_execute_pandas_code` 能捕获结果
2. **中文列名**需要用反引号或直接引用：`df['销售额']` 而非 `df.销售额`
3. **日期列**需先转换：`df['日期'] = pd.to_datetime(df['日期'])`
4. **大文件**注意性能：避免全表操作，优先用 `groupby` + `agg` 代替逐行计算
5. **结果类型**：DataFrame → `result = df[...]`；Series → `result = df.groupby(...)`；标量 → `result = df[col].mean()`
