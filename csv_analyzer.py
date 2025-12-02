"""
CSV File Analyzer - Basic file and statistical analysis without LLM.

This module provides functionality to analyze CSV files and generate
comprehensive summaries including file metadata and statistical analysis.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class CSVAnalyzer:
    """
    Analyzer for CSV files that provides basic file summaries and statistical analysis.
    """

    def __init__(self):
        """Initialize the CSV analyzer."""
        pass

    def analyze_file(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Analyze a single CSV file and return comprehensive information.

        Args:
            file_path: Path to the CSV file to analyze.

        Returns:
            Dictionary containing file summary and statistical analysis.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        
        if not path.suffix.lower() == ".csv":
            raise ValueError(f"File is not a CSV: {path}")

        # Read the CSV file
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise RuntimeError(f"Error reading CSV file: {e}")

        # Generate basic file summary
        file_summary = self._generate_file_summary(path, df)
        
        # Generate statistical summary
        statistical_summary = self._generate_statistical_summary(df)

        return {
            "file_summary": file_summary,
            "statistical_summary": statistical_summary,
        }

    def _generate_file_summary(
        self, file_path: Path, df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate basic file summary information.

        Args:
            file_path: Path to the CSV file.
            df: Pandas DataFrame containing the CSV data.

        Returns:
            Dictionary with file summary information.
        """
        return {
            "file_name": file_path.name,
            "file_path": str(file_path.resolve()),
            "number_of_rows": len(df),
            "number_of_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {
                col: str(dtype) for col, dtype in df.dtypes.items()
            },
            "memory_usage_bytes": df.memory_usage(deep=True).sum(),
        }

    def _generate_statistical_summary(
        self, df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate statistical summary for numerical columns.

        Args:
            df: Pandas DataFrame containing the CSV data.

        Returns:
            Dictionary with statistical information.
        """
        # Identify numerical columns
        numerical_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        
        stats = {}
        
        if numerical_cols:
            # Basic statistics for each numerical column
            for col in numerical_cols:
                stats[col] = {
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "median": float(df[col].median()) if not df[col].isna().all() else None,
                    "std": float(df[col].std()) if not df[col].isna().all() else None,
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "count": int(df[col].count()),  # Non-null count
                    "null_count": int(df[col].isna().sum()),
                    "null_percentage": float((df[col].isna().sum() / len(df)) * 100),
                }

            # Correlation matrix for numerical columns
            if len(numerical_cols) > 1:
                correlation_matrix = df[numerical_cols].corr()
                stats["correlations"] = {
                    col: {
                        other_col: float(correlation_matrix.loc[col, other_col])
                        for other_col in numerical_cols
                        if col != other_col
                    }
                    for col in numerical_cols
                }
            else:
                stats["correlations"] = {}
        else:
            stats["correlations"] = {}

        # Summary of non-numerical columns
        non_numerical_cols = df.select_dtypes(
            exclude=["int64", "float64"]
        ).columns.tolist()
        
        if non_numerical_cols:
            stats["non_numerical_columns"] = {}
            for col in non_numerical_cols:
                stats["non_numerical_columns"][col] = {
                    "unique_count": int(df[col].nunique()),
                    "null_count": int(df[col].isna().sum()),
                    "null_percentage": float((df[col].isna().sum() / len(df)) * 100),
                    "most_frequent": df[col].mode().tolist() if not df[col].mode().empty else [],
                }

        return {
            "numerical_columns": numerical_cols,
            "statistics": stats,
        }

    def format_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Format the analysis results into a human-readable string.

        Args:
            analysis: Dictionary returned from analyze_file().

        Returns:
            Formatted string summary.
        """
        file_summary = analysis["file_summary"]
        stat_summary = analysis["statistical_summary"]

        output = []
        output.append("=" * 80)
        output.append("CSV FILE ANALYSIS SUMMARY")
        output.append("=" * 80)
        output.append("")

        # File Summary
        output.append("📄 FILE SUMMARY")
        output.append("-" * 80)
        output.append(f"File Name: {file_summary['file_name']}")
        output.append(f"File Path: {file_summary['file_path']}")
        output.append(f"Number of Rows: {file_summary['number_of_rows']:,}")
        output.append(f"Number of Columns: {file_summary['number_of_columns']}")
        output.append(f"Memory Usage: {file_summary['memory_usage_bytes']:,} bytes")
        output.append("")

        # Column Information
        output.append("📊 COLUMN INFORMATION")
        output.append("-" * 80)
        for col_name, dtype in file_summary["data_types"].items():
            output.append(f"  • {col_name}: {dtype}")
        output.append("")

        # Statistical Summary
        output.append("📈 STATISTICAL SUMMARY")
        output.append("-" * 80)
        
        numerical_cols = stat_summary["numerical_columns"]
        if numerical_cols:
            output.append(f"Numerical Columns: {', '.join(numerical_cols)}")
            output.append("")
            
            stats = stat_summary["statistics"]
            for col in numerical_cols:
                if col in stats:
                    col_stats = stats[col]
                    output.append(f"  Column: {col}")
                    if col_stats["mean"] is not None:
                        output.append(f"    Mean: {col_stats['mean']:.4f}")
                        output.append(f"    Median: {col_stats['median']:.4f}")
                        output.append(f"    Std Dev: {col_stats['std']:.4f}")
                        output.append(f"    Min: {col_stats['min']:.4f}")
                        output.append(f"    Max: {col_stats['max']:.4f}")
                    output.append(f"    Count (non-null): {col_stats['count']:,}")
                    output.append(f"    Null Count: {col_stats['null_count']:,} ({col_stats['null_percentage']:.2f}%)")
                    output.append("")
        else:
            output.append("No numerical columns found in this dataset.")
            output.append("")

        # Correlations
        if "correlations" in stat_summary["statistics"] and stat_summary["statistics"]["correlations"]:
            output.append("🔗 CORRELATIONS (Numerical Columns)")
            output.append("-" * 80)
            correlations = stat_summary["statistics"]["correlations"]
            for col1, corr_dict in correlations.items():
                if corr_dict:  # Only show if there are correlations
                    output.append(f"  {col1}:")
                    for col2, corr_value in corr_dict.items():
                        output.append(f"    ↔ {col2}: {corr_value:.4f}")
            output.append("")

        # Non-numerical columns summary
        if "non_numerical_columns" in stat_summary["statistics"]:
            non_num = stat_summary["statistics"]["non_numerical_columns"]
            if non_num:
                output.append("📝 NON-NUMERICAL COLUMNS SUMMARY")
                output.append("-" * 80)
                for col, info in non_num.items():
                    output.append(f"  Column: {col}")
                    output.append(f"    Unique Values: {info['unique_count']:,}")
                    output.append(f"    Null Count: {info['null_count']:,} ({info['null_percentage']:.2f}%)")
                    if info["most_frequent"]:
                        output.append(f"    Most Frequent: {', '.join(map(str, info['most_frequent'][:5]))}")
                    output.append("")

        output.append("=" * 80)
        return "\n".join(output)

    def analyze_multiple_files(
        self, file_paths: List[str | Path]
    ) -> Dict[str, Any]:
        """
        Analyze multiple CSV files and return combined results.

        Args:
            file_paths: List of paths to CSV files to analyze.

        Returns:
            Dictionary containing analysis for each file.
        """
        results = {}
        for file_path in file_paths:
            try:
                analysis = self.analyze_file(file_path)
                results[str(Path(file_path).name)] = analysis
            except Exception as e:
                results[str(Path(file_path).name)] = {
                    "error": str(e),
                }
        return results

    def format_multiple_summaries(self, analyses: Dict[str, Any]) -> str:
        """
        Format multiple file analyses into a human-readable string.

        Args:
            analyses: Dictionary returned from analyze_multiple_files().

        Returns:
            Formatted string summary.
        """
        output = []
        output.append("=" * 80)
        output.append("MULTIPLE CSV FILES ANALYSIS")
        output.append("=" * 80)
        output.append("")

        for file_name, analysis in analyses.items():
            if "error" in analysis:
                output.append(f"❌ Error analyzing {file_name}: {analysis['error']}")
                output.append("")
            else:
                output.append(self.format_summary(analysis))
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Simple test/demo
    import sys

    if len(sys.argv) < 2:
        print("Usage: python csv_analyzer.py <csv_file1> [csv_file2] ...")
        sys.exit(1)

    analyzer = CSVAnalyzer()
    files = sys.argv[1:]

    if len(files) == 1:
        analysis = analyzer.analyze_file(files[0])
        print(analyzer.format_summary(analysis))
    else:
        analyses = analyzer.analyze_multiple_files(files)
        print(analyzer.format_multiple_summaries(analyses))
