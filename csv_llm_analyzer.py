"""
LLM-powered analysis for CSV files.

This module uses OpenAI to generate insights, trends, and explanations
from the statistical analysis of CSV data.
"""

from __future__ import annotations

import os
import json
from typing import Dict, Any, Optional

try:
    import openai
except ImportError:
    openai = None

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manual load if python-dotenv not available
    def load_env_manually():
        from pathlib import Path
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip().lstrip("\ufeff")
                            os.environ[key] = value.strip()
            except Exception:
                pass
    load_env_manually()


class CSVLLMAnalyzer:
    """
    LLM-powered analyzer that generates insights from CSV statistical analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer.

        Args:
            api_key: OpenAI API key. If not provided, will try to load from environment.
        """
        if openai is None:
            raise ImportError(
                "The 'openai' package is required. Install it with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_insights(
        self, csv_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate AI-powered insights from CSV analysis.

        Args:
            csv_analysis: Dictionary from CSVAnalyzer.analyze_file()

        Returns:
            Dictionary with generated insights sections.
        """
        # Prepare the data for the LLM
        prompt = self._build_prompt(csv_analysis)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst expert. Analyze CSV data and provide clear, insightful explanations. Focus on practical insights that help users understand their data.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            insights_text = response.choices[0].message.content.strip()

            # Parse the response into sections
            insights = self._parse_insights(insights_text)

            return insights

        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {e}")

    def _build_prompt(self, csv_analysis: Dict[str, Any]) -> str:
        """
        Build the prompt for the LLM based on CSV analysis.

        Args:
            csv_analysis: Dictionary from CSVAnalyzer.analyze_file()

        Returns:
            Formatted prompt string.
        """
        file_summary = csv_analysis["file_summary"]
        stat_summary = csv_analysis["statistical_summary"]

        prompt = f"""Analyze the following CSV dataset and provide comprehensive insights.

DATASET OVERVIEW:
- File Name: {file_summary['file_name']}
- Number of Rows: {file_summary['number_of_rows']:,}
- Number of Columns: {file_summary['number_of_columns']}
- Column Names: {', '.join(file_summary['column_names'])}

DATA TYPES:
{json.dumps(file_summary['data_types'], indent=2)}

STATISTICAL SUMMARY:
"""

        # Add numerical column statistics
        if stat_summary["numerical_columns"]:
            prompt += "\nNUMERICAL COLUMNS:\n"
            stats = stat_summary["statistics"]
            for col in stat_summary["numerical_columns"]:
                if col in stats:
                    col_stats = stats[col]
                    prompt += f"\n{col}:\n"
                    if col_stats["mean"] is not None:
                        prompt += f"  - Mean: {col_stats['mean']:.4f}\n"
                        prompt += f"  - Median: {col_stats['median']:.4f}\n"
                        prompt += f"  - Std Dev: {col_stats['std']:.4f}\n"
                        prompt += f"  - Min: {col_stats['min']:.4f}\n"
                        prompt += f"  - Max: {col_stats['max']:.4f}\n"
                    prompt += f"  - Null Count: {col_stats['null_count']:,} ({col_stats['null_percentage']:.2f}%)\n"

            # Add correlations
            if "correlations" in stats and stats["correlations"]:
                prompt += "\nCORRELATIONS:\n"
                for col1, corr_dict in stats["correlations"].items():
                    for col2, corr_value in corr_dict.items():
                        prompt += f"  - {col1} ↔ {col2}: {corr_value:.4f}\n"

        # Add non-numerical column info
        if "non_numerical_columns" in stat_summary["statistics"]:
            non_num = stat_summary["statistics"]["non_numerical_columns"]
            if non_num:
                prompt += "\nNON-NUMERICAL COLUMNS:\n"
                for col, info in non_num.items():
                    prompt += f"\n{col}:\n"
                    prompt += f"  - Unique Values: {info['unique_count']:,}\n"
                    prompt += f"  - Null Count: {info['null_count']:,} ({info['null_percentage']:.2f}%)\n"
                    if info["most_frequent"]:
                        prompt += f"  - Most Frequent: {', '.join(map(str, info['most_frequent'][:5]))}\n"

        prompt += """

Please provide a comprehensive analysis in the following format:

1. HIGH-LEVEL SUMMARY:
   - What the dataset appears to represent
   - What the key variables might mean
   - Any notable observations at first glance

2. KEY TRENDS:
   - Major patterns in the data (increasing/decreasing trends, distributions)
   - Notable correlations and what they might indicate
   - Any seasonal or cyclical patterns if applicable

3. ANOMALIES OR DATA ISSUES:
   - Unexpected missing values
   - Outlier values that stand out
   - Strange categories or values
   - Possible data entry errors

4. NATURAL-LANGUAGE EXPLANATION FOR BEGINNERS:
   - Explain the key findings in simple, accessible language
   - Use analogies or examples where helpful
   - Focus on what the data means in practical terms

Be specific, insightful, and practical. Use the actual numbers and statistics from the data."""

        return prompt

    def _parse_insights(self, insights_text: str) -> Dict[str, str]:
        """
        Parse the LLM response into structured sections.

        Args:
            insights_text: Raw text response from LLM.

        Returns:
            Dictionary with parsed sections.
        """
        insights = {
            "high_level_summary": "",
            "key_trends": "",
            "anomalies": "",
            "beginner_explanation": "",
        }

        # Try to parse structured sections
        sections = {
            "HIGH-LEVEL SUMMARY": "high_level_summary",
            "1. HIGH-LEVEL SUMMARY": "high_level_summary",
            "High-Level Summary": "high_level_summary",
            "KEY TRENDS": "key_trends",
            "2. KEY TRENDS": "key_trends",
            "Key Trends": "key_trends",
            "ANOMALIES": "anomalies",
            "3. ANOMALIES": "anomalies",
            "Anomalies": "anomalies",
            "ANOMALIES OR DATA ISSUES": "anomalies",
            "NATURAL-LANGUAGE": "beginner_explanation",
            "4. NATURAL-LANGUAGE": "beginner_explanation",
            "Natural-Language": "beginner_explanation",
            "BEGINNER": "beginner_explanation",
        }

        lines = insights_text.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            line_upper = line.strip().upper()
            
            # Check if this line starts a new section
            found_section = False
            for section_key, section_name in sections.items():
                if line_upper.startswith(section_key) or line_upper.startswith(section_key.replace("-", " ")):
                    # Save previous section
                    if current_section:
                        insights[current_section] = "\n".join(current_content).strip()
                    # Start new section
                    current_section = section_name
                    current_content = []
                    found_section = True
                    break
            
            if not found_section and current_section:
                # Add line to current section (skip section headers)
                if line.strip() and not line.strip().startswith("---"):
                    current_content.append(line)

        # Save last section
        if current_section:
            insights[current_section] = "\n".join(current_content).strip()

        # If parsing failed, put everything in high_level_summary
        if not any(insights.values()):
            insights["high_level_summary"] = insights_text

        return insights

    def format_insights(self, insights: Dict[str, str]) -> str:
        """
        Format insights into a human-readable string.

        Args:
            insights: Dictionary from generate_insights().

        Returns:
            Formatted string.
        """
        output = []
        output.append("=" * 80)
        output.append("🤖 AI-GENERATED INSIGHTS")
        output.append("=" * 80)
        output.append("")

        if insights.get("high_level_summary"):
            output.append("📊 HIGH-LEVEL SUMMARY")
            output.append("-" * 80)
            output.append(insights["high_level_summary"])
            output.append("")

        if insights.get("key_trends"):
            output.append("📈 KEY TRENDS")
            output.append("-" * 80)
            output.append(insights["key_trends"])
            output.append("")

        if insights.get("anomalies"):
            output.append("⚠️  ANOMALIES OR DATA ISSUES")
            output.append("-" * 80)
            output.append(insights["anomalies"])
            output.append("")

        if insights.get("beginner_explanation"):
            output.append("💡 EXPLANATION FOR BEGINNERS")
            output.append("-" * 80)
            output.append(insights["beginner_explanation"])
            output.append("")

        output.append("=" * 80)
        return "\n".join(output)

