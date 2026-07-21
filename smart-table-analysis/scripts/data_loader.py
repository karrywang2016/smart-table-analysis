#!/usr/bin/env python3
"""
Data Loader - Smart Table Analysis Skill
Loads Excel/CSV files, detects data types, generates schema preview,
and provides data quality assessment.
"""

import sys
import json
import argparse
from pathlib import Path
import pandas as pd

def load_file(file_path, **kwargs):
    """Load a data file (Excel or CSV) into a DataFrame-like structure."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext in ('.xlsx', '.xls', '.xlsm'):
        # Try to read all sheets info first
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        if kwargs.get('sheet_name'):
            df = pd.read_excel(file_path, sheet_name=kwargs['sheet_name'])
        else:
            df = pd.read_excel(file_path, sheet_name=0)
        return df, {'format': 'excel', 'sheets': sheets, 'sheet_used': kwargs.get('sheet_name') or sheets[0]}
    elif ext in ('.csv', '.tsv', '.txt'):
        sep = kwargs.get('sep', None)
        encoding = kwargs.get('encoding', 'utf-8')
        if ext == '.tsv':
            sep = sep or '\t'
        elif ext == '.csv':
            sep = sep or ','
        else:
            sep = sep or ','
        df = pd.read_csv(file_path, sep=sep, encoding=encoding)
        return df, {'format': 'csv', 'sep': sep, 'encoding': encoding}
    elif ext == '.json':
        df = pd.read_json(file_path)
        return df, {'format': 'json'}
    elif ext == '.parquet':
        df = pd.read_parquet(file_path)
        return df, {'format': 'parquet'}
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported: .xlsx, .xls, .csv, .tsv, .json, .parquet")


def detect_column_types(df):
    """Detect and classify column data types with semantic meaning."""
    type_map = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample_vals = df[col].dropna().head(5).tolist()
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        total_count = len(df)
        
        # Semantic type detection
        semantic = 'unknown'
        if 'int' in dtype or 'float' in dtype:
            if unique_count <= 10 and total_count > 20:
                semantic = 'category_numeric'
            elif unique_count == total_count:
                semantic = 'id'
            else:
                semantic = 'numeric'
        elif 'datetime' in dtype:
            semantic = 'datetime'
        elif dtype == 'object' or dtype == 'string':
            # Check if it might be a date column
            try:
                pd.to_datetime(df[col].dropna().head(20))
                semantic = 'datetime_candidate'
            except:
                pass
            # Check cardinality for category vs text
            if unique_count <= 20 and total_count > 50:
                semantic = 'category'
            elif unique_count > total_count * 0.8:
                semantic = 'id'
            else:
                semantic = 'text'
        elif dtype == 'bool':
            semantic = 'boolean'
        
        type_map[col] = {
            'dtype': dtype,
            'semantic_type': semantic,
            'null_count': int(null_count),
            'null_pct': round(null_count / total_count * 100, 2) if total_count > 0 else 0,
            'unique_count': int(unique_count),
            'sample_values': [str(v) for v in sample_vals[:3]]
        }
    return type_map


def assess_data_quality(df):
    """Assess overall data quality and flag potential issues."""
    issues = []
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Missing values assessment
    null_pct = df.isnull().sum().sum() / (total_rows * total_cols) * 100
    if null_pct > 20:
        issues.append({
            'type': 'high_missing',
            'severity': 'high',
            'message': f'数据缺失率 {null_pct:.1f}%，超过20%阈值，建议先处理缺失值'
        })
    elif null_pct > 5:
        issues.append({
            'type': 'moderate_missing',
            'severity': 'medium',
            'message': f'数据缺失率 {null_pct:.1f}%，部分字段需要关注'
        })
    
    # Per-column missing value issues
    for col in df.columns:
        col_null_pct = df[col].isnull().sum() / total_rows * 100
        if col_null_pct > 30:
            issues.append({
                'type': 'column_missing',
                'severity': 'high',
                'column': col,
                'message': f'字段 "{col}" 缺失率 {col_null_pct:.1f}%，可能需要删除或填充'
            })
    
    # Duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        dup_pct = dup_count / total_rows * 100
        issues.append({
            'type': 'duplicates',
            'severity': 'medium' if dup_pct < 5 else 'high',
            'message': f'发现 {dup_count} 行重复数据 ({dup_pct:.1f}%)，建议检查是否为正常业务数据'
        })
    
    # Check for potential outlier columns
    for col in df.select_dtypes(include=['number']).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outlier_count = ((df[col] < q1 - 3*iqr) | (df[col] > q3 + 3*iqr)).sum()
            if outlier_count > total_rows * 0.05:
                issues.append({
                    'type': 'outliers',
                    'severity': 'medium',
                    'column': col,
                    'message': f'字段 "{col}" 可能存在 {int(outlier_count)} 个异常值，建议进一步检查'
                })
    
    quality_score = max(0, 100 - null_pct - (dup_count/total_rows*100 if total_rows > 0 else 0))
    
    return {
        'quality_score': round(quality_score, 1),
        'total_rows': total_rows,
        'total_columns': total_cols,
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        'issues': issues
    }


def generate_schema_preview(df, file_info):
    """Generate a comprehensive schema preview for the loaded data."""
    col_types = detect_column_types(df)
    quality = assess_data_quality(df)
    
    # Numeric column stats
    numeric_stats = {}
    for col in df.select_dtypes(include=['number']).columns:
        numeric_stats[col] = {
            'min': round(df[col].min(), 4) if pd.notna(df[col].min()) else None,
            'max': round(df[col].max(), 4) if pd.notna(df[col].max()) else None,
            'mean': round(df[col].mean(), 4) if pd.notna(df[col].mean()) else None,
            'median': round(df[col].median(), 4) if pd.notna(df[col].median()) else None,
            'std': round(df[col].std(), 4) if pd.notna(df[col].std()) else None,
        }
    
    schema = {
        'file_info': file_info,
        'quality': quality,
        'columns': col_types,
        'numeric_summary': numeric_stats,
        'shape': {'rows': len(df), 'columns': len(df.columns)},
        'head': df.head(5).to_dict(orient='records'),
        'index_range': {'start': str(df.index[0]) if len(df) > 0 else None, 
                        'end': str(df.index[-1]) if len(df) > 0 else None}
    }
    return schema


def main():
    parser = argparse.ArgumentParser(description='Load and inspect a data file')
    parser.add_argument('file', help='Path to the data file')
    parser.add_argument('--sheet', help='Excel sheet name (optional)', default=None)
    parser.add_argument('--sep', help='CSV separator (optional)', default=None)
    parser.add_argument('--encoding', help='File encoding (optional)', default='utf-8')
    parser.add_argument('--action', choices=['schema', 'head', 'quality', 'columns'], 
                        default='schema', help='What to output')
    
    args = parser.parse_args()
    
    try:
        kwargs = {}
        if args.sheet:
            kwargs['sheet_name'] = args.sheet
        if args.sep:
            kwargs['sep'] = args.sep
        kwargs['encoding'] = args.encoding
        
        df, file_info = load_file(args.file, **kwargs)
        
        if args.action == 'schema':
            result = generate_schema_preview(df, file_info)
        elif args.action == 'head':
            result = {'data': df.head(10).to_dict(orient='records')}
        elif args.action == 'quality':
            result = assess_data_quality(df)
        elif args.action == 'columns':
            result = detect_column_types(df)
        
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
    except Exception as e:
        error_result = {'error': str(e), 'type': type(e).__name__}
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
