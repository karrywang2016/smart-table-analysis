#!/usr/bin/env python3
"""
Chart Generator - Smart Table Analysis Skill
Generates matplotlib charts from analysis results, saves as PNG files.
Supports: bar, line, pie, scatter, heatmap, histogram, box, area charts.
Follows Chinese stock market convention: red = rise, green = fall.
"""

import sys
import json
import argparse
from pathlib import Path

# Chart type mapping: analysis intent → recommended chart type
CHART_TYPE_MAP = {
    'comparison': 'bar',
    'trend': 'line',
    'distribution': 'histogram',
    'composition': 'pie',
    'correlation': 'heatmap',
    'relationship': 'scatter',
    'outlier': 'box',
    'range': 'area',
    'ranking': 'bar',
    'flow': 'area',
    'proportion': 'pie',
    'spread': 'box',
}


def setup_matplotlib():
    """Configure matplotlib for high-quality output with Chinese font support."""
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    
    # Try to use Chinese-friendly fonts
    font_candidates = [
        'SimHei', 'Microsoft YaHei', 'STSong', 'STXihei',
        'Arial Unicode MS', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei'
    ]
    
    from matplotlib.font_manager import FontManager
    fm = FontManager()
    available_fonts = set(f.name for f in fm.ttflist)
    
    chosen_font = None
    for font in font_candidates:
        if font in available_fonts:
            chosen_font = font
            break
    
    if chosen_font:
        plt.rcParams['font.sans-serif'] = [chosen_font, 'DejaVu Sans']
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['savefig.bbox'] = 'tight'
    plt.rcParams['savefig.pad_inches'] = 0.2
    
    return plt


def apply_chinese_color_convention(series_values, series_index=None):
    """
    Apply Chinese stock market convention:
    positive/change_up → red, negative/change_down → green.
    For non-financial data, use a pleasant color palette.
    """
    import numpy as np
    
    if series_index is not None and '涨' in str(series_index) or '增' in str(series_index):
        return '#E74C3C'  # Red for increase (Chinese convention)
    elif series_index is not None and '跌' in str(series_index) or '减' in str(series_index):
        return '#27AE60'  # Green for decrease (Chinese convention)
    
    # Default pleasant palette
    palette = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6',
               '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#C0392B']
    return palette


def generate_bar_chart(plt, df, x_col, y_col, title=None, orientation='vertical', 
                       top_n=None, color_by_value=False, output_path=None):
    """Generate bar chart with optional ranking and color coding."""
    import pandas as pd
    
    if top_n:
        df = df.nlargest(top_n, y_col) if top_n > 0 else df.nsmallest(abs(top_n), y_col)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = None
    if color_by_value:
        # Chinese convention: positive = red, negative = green
        colors = ['#E74C3C' if v >= 0 else '#27AE60' for v in df[y_col]]
    else:
        palette = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6',
                   '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#C0392B']
        colors = palette[:len(df)]
    
    if orientation == 'horizontal':
        ax.barh(df[x_col], df[y_col], color=colors)
        ax.set_xlabel(y_col)
        ax.set_ylabel(x_col)
    else:
        ax.bar(df[x_col], df[y_col], color=colors)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'bar'}
    else:
        plt.close(fig)
        return {'chart_type': 'bar', 'note': 'No output path specified'}


def generate_line_chart(plt, df, x_col, y_cols, title=None, add_ma=False, output_path=None):
    """Generate line chart with optional moving average lines."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
    
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]
        ax.plot(df[x_col], df[y_col], label=y_col, color=color, linewidth=2)
        
        if add_ma and len(df) >= 7:
            ma = df[y_col].rolling(7, min_periods=1).mean()
            ax.plot(df[x_col], ma, label=f'{y_col} 7日均线', 
                   color=color, linewidth=1, linestyle='--', alpha=0.6)
    
    ax.set_xlabel(x_col)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'line'}
    else:
        plt.close(fig)
        return {'chart_type': 'line', 'note': 'No output path specified'}


def generate_pie_chart(plt, df, label_col, value_col, title=None, top_n=8, output_path=None):
    """Generate pie chart for proportion/composition analysis."""
    import pandas as pd
    
    if top_n and len(df) > top_n:
        top = df.nlargest(top_n, value_col)
        others_sum = df[~df[label_col].isin(top[label_col])][value_col].sum()
        
        labels = list(top[label_col]) + ['其他']
        values = list(top[value_col]) + [others_sum]
    else:
        labels = list(df[label_col])
        values = list(df[value_col])
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6',
              '#1ABC9C', '#E67E22', '#34495E', '#95A5A6']
    
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors[:len(labels)],
        autopct='%1.1f%%', startangle=90,
        pctdistance=0.85
    )
    
    for text in autotexts:
        text.set_fontsize(9)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'pie'}
    else:
        plt.close(fig)
        return {'chart_type': 'pie', 'note': 'No output path specified'}


def generate_scatter_chart(plt, df, x_col, y_col, size_col=None, color_col=None,
                           title=None, output_path=None):
    """Generate scatter plot for relationship analysis."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    s = df[size_col] * 50 if size_col else 30
    c = df[color_col] if color_col else '#3498DB'
    
    scatter = ax.scatter(df[x_col], df[y_col], s=s, c=c, alpha=0.6, edgecolors='white')
    
    if color_col:
        plt.colorbar(scatter, label=color_col)
    
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'scatter'}
    else:
        plt.close(fig)
        return {'chart_type': 'scatter', 'note': 'No output path specified'}


def generate_heatmap_chart(plt, corr_data, title=None, output_path=None):
    """Generate heatmap for correlation matrix visualization."""
    import numpy as np
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    cols = list(corr_data.keys())
    matrix = np.array([[corr_data[r][c] for c in cols] for r in cols])
    
    im = ax.imshow(matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
    
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(cols, fontsize=9)
    
    # Add correlation values as text
    for i in range(len(cols)):
        for j in range(len(cols)):
            val = matrix[i, j]
            color = 'white' if abs(val) > 0.6 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=8)
    
    plt.colorbar(im, label='相关系数')
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'heatmap'}
    else:
        plt.close(fig)
        return {'chart_type': 'heatmap', 'note': 'No output path specified'}


def generate_histogram_chart(plt, df, col, bins=30, title=None, output_path=None):
    """Generate histogram for distribution analysis."""
    import numpy as np
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = df[col].dropna()
    ax.hist(data, bins=bins, color='#3498DB', edgecolor='white', alpha=0.7)
    
    # Add mean and median lines
    mean_val = data.mean()
    median_val = data.median()
    ax.axvline(mean_val, color='#E74C3C', linewidth=2, linestyle='--', label=f'均值: {mean_val:.2f}')
    ax.axvline(median_val, color='#2ECC71', linewidth=2, linestyle='--', label=f'中位数: {median_val:.2f}')
    
    ax.set_xlabel(col)
    ax.set_ylabel('频次')
    ax.legend()
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'histogram'}
    else:
        plt.close(fig)
        return {'chart_type': 'histogram', 'note': 'No output path specified'}


def generate_box_chart(plt, df, col, group_col=None, title=None, output_path=None):
    """Generate box plot for outlier/range analysis."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if group_col:
        groups = df[group_col].unique()[:10]  # Limit to 10 groups
        data_groups = [df[df[group_col] == g][col].dropna().values for g in groups]
        bp = ax.boxplot(data_groups, labels=[str(g) for g in groups], patch_artist=True)
        
        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6',
                  '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#C0392B']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    else:
        data = df[col].dropna().values
        bp = ax.boxplot(data, patch_artist=True)
        bp['boxes'][0].set_facecolor('#3498DB')
        bp['boxes'][0].set_alpha(0.7)
    
    ax.set_ylabel(col)
    if group_col:
        ax.set_xlabel(group_col)
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'box'}
    else:
        plt.close(fig)
        return {'chart_type': 'box', 'note': 'No output path specified'}


def generate_grouped_bar_chart(plt, df, group_col, value_cols, title=None, output_path=None):
    """Generate grouped bar chart for multi-metric comparison."""
    import numpy as np
    
    groups = df[group_col].tolist()
    n_groups = len(groups)
    n_metrics = len(value_cols)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(n_groups)
    width = 0.8 / n_metrics
    
    colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
    
    for i, col in enumerate(value_cols):
        offset = width * (i - n_metrics/2 + 0.5)
        ax.bar(x + offset, df[col], width, label=col, color=colors[i % len(colors)])
    
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45 if n_groups > 6 else 0, ha='right')
    ax.set_xlabel(group_col)
    ax.legend()
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return {'chart_path': str(output_path), 'chart_type': 'grouped_bar'}
    else:
        plt.close(fig)
        return {'chart_type': 'grouped_bar', 'note': 'No output path specified'}


def main():
    parser = argparse.ArgumentParser(description='Generate charts from data')
    parser.add_argument('file', help='Path to the data file')
    parser.add_argument('--chart-type', required=True,
                        choices=['bar', 'line', 'pie', 'scatter', 'heatmap',
                                 'histogram', 'box', 'grouped_bar', 'area'],
                        help='Chart type to generate')
    parser.add_argument('--x-col', help='X-axis column')
    parser.add_argument('--y-col', help='Y-axis column (single)')
    parser.add_argument('--y-cols', help='Comma-separated Y-axis columns')
    parser.add_argument('--label-col', help='Label column (for pie)')
    parser.add_argument('--value-col', help='Value column (for pie)')
    parser.add_argument('--group-col', help='Group/category column')
    parser.add_argument('--size-col', help='Size column (for scatter)')
    parser.add_argument('--color-col', help='Color column (for scatter)')
    parser.add_argument('--bins', help='Number of bins (for histogram)', type=int, default=30)
    parser.add_argument('--corr-data', help='JSON correlation data (for heatmap)')
    parser.add_argument('--title', help='Chart title')
    parser.add_argument('--output', help='Output PNG file path', required=True)
    parser.add_argument('--top-n', help='Show top N items', type=int)
    parser.add_argument('--orientation', choices=['vertical', 'horizontal'], default='vertical')
    parser.add_argument('--sheet', help='Excel sheet name', default=None)
    
    args = parser.parse_args()
    
    try:
        import pandas as pd
        from data_loader import load_file
        
        plt = setup_matplotlib()
        
        kwargs = {}
        if args.sheet:
            kwargs['sheet_name'] = args.sheet
        
        df, _ = load_file(args.file, **kwargs)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        y_cols = args.y_cols.split(',') if args.y_cols else [args.y_col] if args.y_col else None
        
        result = {}
        
        if args.chart_type == 'bar':
            result = generate_bar_chart(plt, df, args.x_col, args.y_col, args.title,
                                       args.orientation, args.top_n, output_path=str(output_path))
        elif args.chart_type == 'line':
            result = generate_line_chart(plt, df, args.x_col, y_cols, args.title,
                                        add_ma=True, output_path=str(output_path))
        elif args.chart_type == 'pie':
            result = generate_pie_chart(plt, df, args.label_col, args.value_col, args.title,
                                       top_n=args.top_n or 8, output_path=str(output_path))
        elif args.chart_type == 'scatter':
            result = generate_scatter_chart(plt, df, args.x_col, args.y_col, 
                                           args.size_col, args.color_col, args.title,
                                           output_path=str(output_path))
        elif args.chart_type == 'heatmap':
            corr_data = json.loads(args.corr_data) if args.corr_data else None
            result = generate_heatmap_chart(plt, corr_data, args.title, 
                                           output_path=str(output_path))
        elif args.chart_type == 'histogram':
            result = generate_histogram_chart(plt, df, args.x_col or args.y_col,
                                            args.bins, args.title, output_path=str(output_path))
        elif args.chart_type == 'box':
            result = generate_box_chart(plt, df, args.y_col, args.group_col, 
                                       args.title, output_path=str(output_path))
        elif args.chart_type == 'grouped_bar':
            result = generate_grouped_bar_chart(plt, df, args.group_col, y_cols,
                                               args.title, output_path=str(output_path))
        elif args.chart_type == 'area':
            fig, ax = plt.subplots(figsize=(12, 6))
            for y_col in y_cols:
                ax.fill_between(df[args.x_col], df[y_col], alpha=0.3, label=y_col)
            ax.set_xlabel(args.x_col)
            ax.legend()
            if args.title:
                ax.set_title(args.title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            fig.savefig(str(output_path), dpi=150, bbox_inches='tight')
            plt.close(fig)
            result = {'chart_path': str(output_path), 'chart_type': 'area'}
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {'error': str(e), 'type': type(e).__name__}
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
