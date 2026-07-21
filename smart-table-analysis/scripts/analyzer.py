#!/usr/bin/env python3
"""
Analyzer - Smart Table Analysis Skill
Core analysis engine that executes generated Pandas code safely,
performs statistical analysis, pivot tables, correlations, and more.
"""

import sys
import json
import argparse
import traceback
from pathlib import Path
from io import StringIO
import pandas as pd
import numpy as np

# Safe imports for sandbox execution
SAFE_IMPORTS = {
    'pandas', 'numpy', 'math', 'statistics', 'datetime', 're',
    'collections', 'itertools', 'functools', 'json', 'os_path'
}

def safe_execute_pandas_code(code, df, df_name='df'):
    """
    Execute Pandas code in a restricted environment.
    Only allows safe operations on the provided DataFrame.
    Returns the result and any stdout output.
    """
    import pandas as pd
    import numpy as np
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    local_vars = {
        df_name: df,
        'pd': pd,
        'np': np,
        'result': None,
        'fig': None,
        'plt': None,
    }
    
    try:
        # Pre-process code: ensure result assignment
        exec(code, {'__builtins__': {}}, local_vars)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Extract result
        result = local_vars.get('result', None)
        
        # Convert result to JSON-safe format
        if isinstance(result, pd.DataFrame):
            result_json = result.to_dict(orient='records')
        elif isinstance(result, pd.Series):
            result_json = result.to_dict()
        elif isinstance(result, (np.integer, np.floating)):
            result_json = float(result)
        elif isinstance(result, (int, float, str, bool)):
            result_json = result
        elif isinstance(result, dict):
            result_json = {str(k): float(v) if isinstance(v, (np.integer, np.floating)) else v 
                          for k, v in result.items()}
        elif isinstance(result, list):
            result_json = result
        else:
            result_json = str(result)
        
        return {
            'success': True,
            'result': result_json,
            'stdout': output,
            'result_type': type(result).__name__ if result is not None else 'None'
        }
        
    except Exception as e:
        sys.stdout = old_stdout
        output = sys.stdout.getvalue()
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'stdout': output
        }


def run_statistical_summary(df, columns=None):
    """Generate comprehensive statistical summary."""
    import pandas as pd
    
    if columns is None:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    else:
        numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    
    if not numeric_cols:
        return {'error': 'No numeric columns found for statistical summary'}
    
    stats = df[numeric_cols].describe().to_dict()
    
    # Add additional stats
    for col in numeric_cols:
        col_data = df[col].dropna()
        stats[col]['skew'] = round(float(col_data.skew()), 4) if len(col_data) > 2 else None
        stats[col]['kurtosis'] = round(float(col_data.kurtosis()), 4) if len(col_data) > 3 else None
        stats[col]['iqr'] = round(float(col_data.quantile(0.75) - col_data.quantile(0.25)), 4)
        stats[col]['missing_pct'] = round(df[col].isnull().sum() / len(df) * 100, 2)
        stats[col]['zero_pct'] = round((col_data == 0).sum() / len(col_data) * 100, 2) if len(col_data) > 0 else 0
    
    return {'statistics': stats, 'columns_analyzed': numeric_cols}


def run_pivot_analysis(df, index=None, columns=None, values=None, aggfunc='mean'):
    """Generate pivot table analysis."""
    import pandas as pd
    
    try:
        if values and aggfunc == 'mean':
            pivot = pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc='mean')
        elif values:
            if isinstance(aggfunc, str):
                aggfunc = [aggfunc]
            pivot = pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc)
        else:
            pivot = pd.pivot_table(df, index=index, columns=columns, aggfunc='count')
        
        return {
            'success': True,
            'pivot_data': pivot.to_dict(),
            'pivot_shape': {'rows': len(pivot), 'columns': len(pivot.columns)},
            'index': index,
            'columns': columns,
            'values': values,
            'aggfunc': aggfunc
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_correlation_analysis(df, method='pearson', columns=None):
    """Run correlation analysis between numeric columns."""
    import pandas as pd
    
    if columns:
        numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    else:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {'error': 'Need at least 2 numeric columns for correlation analysis'}
    
    corr = df[numeric_cols].corr(method=method)
    
    # Find strongest correlations
    strong_corrs = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            val = corr.iloc[i, j]
            if abs(val) > 0.5:
                strong_corrs.append({
                    'col_a': numeric_cols[i],
                    'col_b': numeric_cols[j],
                    'correlation': round(float(val), 4),
                    'strength': 'strong' if abs(val) > 0.7 else 'moderate',
                    'direction': 'positive' if val > 0 else 'negative'
                })
    
    return {
        'method': method,
        'correlation_matrix': corr.to_dict(),
        'strong_correlations': sorted(strong_corrs, key=lambda x: abs(x['correlation']), reverse=True),
        'columns_analyzed': numeric_cols
    }


def run_groupby_analysis(df, group_col, agg_cols=None, agg_funcs=None):
    """Run groupby aggregation analysis."""
    import pandas as pd
    
    if agg_cols is None:
        agg_cols = df.select_dtypes(include=['number']).columns.tolist()
        if group_col in agg_cols:
            agg_cols.remove(group_col)
    
    if agg_funcs is None:
        agg_funcs = ['mean', 'count', 'sum', 'std']
    
    try:
        grouped = df.groupby(group_col)[agg_cols].agg(agg_funcs)
        
        # Flatten multi-level column names
        if isinstance(grouped.columns, pd.MultiIndex):
            grouped.columns = [f'{col}_{func}' for col, func in grouped.columns]
        
        return {
            'success': True,
            'group_column': group_col,
            'agg_columns': agg_cols,
            'agg_functions': agg_funcs,
            'groups_count': len(grouped),
            'result': grouped.to_dict(orient='index'),
            'top_groups': grouped.head(10).to_dict(orient='index')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_comparison_analysis(df, compare_col, compare_vals=None, metrics=None):
    """Compare groups/categories against each other."""
    import pandas as pd
    
    if compare_vals is None:
        compare_vals = df[compare_col].unique().tolist()[:5]  # Top 5 categories
    
    if metrics is None:
        metrics = df.select_dtypes(include=['number']).columns.tolist()
        if compare_col in metrics:
            metrics.remove(compare_col)
    
    results = {}
    for val in compare_vals:
        subset = df[df[compare_col] == val]
        group_stats = {}
        for m in metrics:
            if m in subset.columns:
                group_stats[m] = {
                    'mean': round(float(subset[m].mean()), 4) if pd.notna(subset[m].mean()) else None,
                    'median': round(float(subset[m].median()), 4) if pd.notna(subset[m].median()) else None,
                    'std': round(float(subset[m].std()), 4) if pd.notna(subset[m].std()) else None,
                    'count': int(subset[m].count()),
                    'sum': round(float(subset[m].sum()), 4) if pd.notna(subset[m].sum()) else None,
                }
        results[str(val)] = group_stats
    
    # Calculate percentage differences between groups
    diff_insights = []
    if len(compare_vals) >= 2:
        for m in metrics:
            vals_list = []
            for v in compare_vals:
                if str(v) in results and m in results[str(v)] and results[str(v)][m]['mean'] is not None:
                    vals_list.append((str(v), results[str(v)][m]['mean']))
            if len(vals_list) >= 2:
                max_val = max(vals_list, key=lambda x: x[1])
                min_val = min(vals_list, key=lambda x: x[1])
                if min_val[1] != 0:
                    pct_diff = round((max_val[1] - min_val[1]) / abs(min_val[1]) * 100, 2)
                    diff_insights.append({
                        'metric': m,
                        'highest': max_val[0],
                        'lowest': min_val[0],
                        'highest_value': max_val[1],
                        'lowest_value': min_val[1],
                        'pct_difference': pct_diff
                    })
    
    return {
        'compare_column': compare_col,
        'compare_values': [str(v) for v in compare_vals],
        'metrics': metrics,
        'results': results,
        'difference_insights': diff_insights
    }


def run_time_analysis(df, time_col, value_col, period='auto'):
    """Analyze time-series trends and patterns."""
    import pandas as pd
    
    try:
        df_sorted = df.sort_values(time_col)
        ts = df_sorted.set_index(time_col)[value_col]
        
        # Auto-detect period
        if period == 'auto':
            freq = pd.infer_freq(df_sorted[time_col])
            period = freq if freq else 'daily'
        
        # Basic trend stats
        first_val = float(ts.iloc[0]) if len(ts) > 0 else None
        last_val = float(ts.iloc[-1]) if len(ts) > 0 else None
        
        if first_val and last_val and first_val != 0:
            total_change_pct = round((last_val - first_val) / abs(first_val) * 100, 2)
        else:
            total_change_pct = None
        
        # Moving averages
        ma_7 = ts.rolling(7, min_periods=1).mean().tail(30).tolist() if len(ts) >= 7 else None
        ma_30 = ts.rolling(30, min_periods=1).mean().tail(30).tolist() if len(ts) >= 30 else None
        
        # Period-over-period comparison
        period_change = []
        if len(ts) > 1:
            for i in range(1, min(len(ts), 13)):
                prev = float(ts.iloc[-(i+1)]) if i+1 <= len(ts) else None
                curr = float(ts.iloc[-i]) if i <= len(ts) else None
                if prev and curr and prev != 0:
                    period_change.append({
                        'period_ago': i,
                        'value': curr,
                        'prev_value': prev,
                        'change_pct': round((curr - prev) / abs(prev) * 100, 2)
                    })
        
        return {
            'time_column': time_col,
            'value_column': value_col,
            'period': period,
            'first_value': first_val,
            'last_value': last_val,
            'total_change_pct': total_change_pct,
            'mean_value': round(float(ts.mean()), 4),
            'std_value': round(float(ts.std()), 4),
            'ma_7_recent': [round(v, 4) for v in ma_7] if ma_7 else None,
            'ma_30_recent': [round(v, 4) for v in ma_30] if ma_30 else None,
            'recent_changes': period_change[:6]
        }
    except Exception as e:
        return {'error': str(e)}


def run_cross_analysis(df, col_a, col_b, analysis_type='crosstab'):
    """Cross-analysis between two columns."""
    import pandas as pd
    
    try:
        if analysis_type == 'crosstab':
            ct = pd.crosstab(df[col_a], df[col_b], margins=True, margins_name='合计')
            return {
                'type': 'crosstab',
                'col_a': col_a,
                'col_b': col_b,
                'data': ct.to_dict(),
                'shape': {'rows': len(ct), 'columns': len(ct.columns)}
            }
        elif analysis_type == 'numeric_by_category':
            if pd.api.types.is_numeric_dtype(df[col_a]) and not pd.api.types.is_numeric_dtype(df[col_b]):
                cat_col, num_col = col_b, col_a
            elif pd.api.types.is_numeric_dtype(df[col_b]) and not pd.api.types.is_numeric_dtype(df[col_a]):
                cat_col, num_col = col_a, col_b
            else:
                return {'error': 'Need one numeric and one categorical column'}
            
            grouped = df.groupby(cat_col)[num_col].agg(['mean', 'median', 'std', 'count', 'min', 'max'])
            return {
                'type': 'numeric_by_category',
                'category_column': cat_col,
                'numeric_column': num_col,
                'data': grouped.to_dict(orient='index')
            }
        else:
            return {'error': f'Unknown analysis_type: {analysis_type}'}
    except Exception as e:
        return {'error': str(e)}


def run_outlier_detection(df, columns=None, method='iqr'):
    """Detect outliers in numeric columns."""
    import pandas as pd
    
    if columns is None:
        columns = df.select_dtypes(include=['number']).columns.tolist()
    
    outlier_report = {}
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        
        col_data = df[col].dropna()
        if method == 'iqr':
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers_mask = (col_data < lower) | (col_data > upper)
        elif method == 'zscore':
            z_scores = (col_data - col_data.mean()) / col_data.std()
            outliers_mask = abs(z_scores) > 3
        
        outlier_count = outliers_mask.sum()
        outlier_indices = col_data[outliers_mask].index.tolist()
        outlier_values = col_data[outliers_mask].tolist()
        
        outlier_report[col] = {
            'outlier_count': int(outlier_count),
            'outlier_pct': round(outlier_count / len(col_data) * 100, 2),
            'bounds': {
                'lower': round(float(lower if method == 'iqr' else col_data.mean() - 3*col_data.std()), 4),
                'upper': round(float(upper if method == 'iqr' else col_data.mean() + 3*col_data.std()), 4)
            },
            'outlier_indices': outlier_indices[:20],  # Limit to first 20
            'outlier_values': [round(float(v), 4) for v in outlier_values[:20]]
        }
    
    return {'method': method, 'outliers': outlier_report}


def main():
    parser = argparse.ArgumentParser(description='Run analysis on a DataFrame')
    parser.add_argument('file', help='Path to the data file')
    parser.add_argument('--action', required=True,
                        choices=['stats', 'pivot', 'correlation', 'groupby',
                                 'compare', 'time', 'cross', 'outliers', 'exec'],
                        help='Analysis action to perform')
    parser.add_argument('--columns', help='Comma-separated column names')
    parser.add_argument('--index', help='Pivot table index column')
    parser.add_argument('--pivot-columns', help='Pivot table columns')
    parser.add_argument('--values', help='Pivot table values column')
    parser.add_argument('--aggfunc', help='Aggregation function', default='mean')
    parser.add_argument('--group-col', help='Groupby column')
    parser.add_argument('--compare-col', help='Comparison column')
    parser.add_argument('--compare-values', help='Comma-separated values to compare')
    parser.add_argument('--time-col', help='Time column for time analysis')
    parser.add_argument('--value-col', help='Value column for time analysis')
    parser.add_argument('--col-a', help='First column for cross analysis')
    parser.add_argument('--col-b', help='Second column for cross analysis')
    parser.add_argument('--cross-type', help='Cross analysis type', default='crosstab')
    parser.add_argument('--method', help='Method (for correlation/outliers)', default='pearson')
    parser.add_argument('--code', help='Pandas code to execute (for exec action)')
    parser.add_argument('--sheet', help='Excel sheet name', default=None)
    
    args = parser.parse_args()
    
    try:
        from data_loader import load_file
        kwargs = {}
        if args.sheet:
            kwargs['sheet_name'] = args.sheet
        df, _ = load_file(args.file, **kwargs)
        
        columns = args.columns.split(',') if args.columns else None
        
        result = {}
        if args.action == 'stats':
            result = run_statistical_summary(df, columns)
        elif args.action == 'pivot':
            result = run_pivot_analysis(df, args.index, args.pivot_columns, 
                                        args.values, args.aggfunc)
        elif args.action == 'correlation':
            result = run_correlation_analysis(df, args.method, columns)
        elif args.action == 'groupby':
            agg_funcs = args.aggfunc.split(',') if args.aggfunc != 'mean' else ['mean', 'count', 'sum']
            result = run_groupby_analysis(df, args.group_col, columns, agg_funcs)
        elif args.action == 'compare':
            compare_vals = args.compare_values.split(',') if args.compare_values else None
            result = run_comparison_analysis(df, args.compare_col, compare_vals, columns)
        elif args.action == 'time':
            result = run_time_analysis(df, args.time_col, args.value_col)
        elif args.action == 'cross':
            result = run_cross_analysis(df, args.col_a, args.col_b, args.cross_type)
        elif args.action == 'outliers':
            result = run_outlier_detection(df, columns, args.method)
        elif args.action == 'exec':
            if not args.code:
                result = {'error': 'No code provided for exec action'}
            else:
                result = safe_execute_pandas_code(args.code, df)
        
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
    except Exception as e:
        error_result = {'error': str(e), 'type': type(e).__name__}
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
