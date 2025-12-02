"""
Main program for CSV File Analyzer.

Prompts user to upload one or more CSV files and provides
comprehensive analysis including file summaries and statistical analysis.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from csv_analyzer import CSVAnalyzer
from csv_llm_analyzer import CSVLLMAnalyzer


def get_csv_files_from_user() -> List[Path]:
    """
    Prompt user to enter CSV file paths.

    Returns:
        List of Path objects for CSV files.
    """
    print("=" * 80)
    print("CSV FILE ANALYZER")
    print("=" * 80)
    print()
    print("Enter one or more CSV file paths to analyze.")
    print("You can enter multiple files separated by commas, or press Enter after each file.")
    print("Press Enter on an empty line when done.")
    print()
    print("-" * 80)

    files: List[Path] = []
    
    while True:
        user_input = input("\nEnter CSV file path (or press Enter to finish): ").strip()
        
        if not user_input:
            if not files:
                print("No files entered. Exiting.")
                sys.exit(0)
            break

        # Handle comma-separated files
        if "," in user_input:
            file_paths = [f.strip() for f in user_input.split(",")]
        else:
            file_paths = [user_input]

        for file_path_str in file_paths:
            file_path = Path(file_path_str.strip())
            
            if not file_path.exists():
                print(f"⚠️  Warning: File not found: {file_path}")
                response = input("  Continue anyway? (y/n): ").strip().lower()
                if response != "y":
                    continue
            
            if file_path.suffix.lower() != ".csv":
                print(f"⚠️  Warning: File does not have .csv extension: {file_path}")
                response = input("  Continue anyway? (y/n): ").strip().lower()
                if response != "y":
                    continue

            if file_path not in files:
                files.append(file_path)
                print(f"✓ Added: {file_path}")

    return files


def main() -> None:
    """Main program entry point."""
    try:
        # Get files from user
        csv_files = get_csv_files_from_user()

        if not csv_files:
            print("No valid CSV files to analyze.")
            return

        print()
        print("=" * 80)
        print(f"Analyzing {len(csv_files)} file(s)...")
        print("=" * 80)
        print()

        # Initialize analyzer
        analyzer = CSVAnalyzer()

        # Analyze files
        if len(csv_files) == 1:
            # Single file analysis
            try:
                analysis = analyzer.analyze_file(csv_files[0])
                print(analyzer.format_summary(analysis))
                
                # Ask if user wants LLM analysis
                print()
                response = input("Generate AI-powered insights? (yes/no): ").strip().lower()
                if response in ("yes", "y"):
                    print()
                    print("Generating AI insights...")
                    print("-" * 80)
                    try:
                        llm_analyzer = CSVLLMAnalyzer()
                        insights = llm_analyzer.generate_insights(analysis)
                        print(llm_analyzer.format_insights(insights))
                    except Exception as e:
                        print(f"❌ Error generating AI insights: {e}")
                        print("Continuing without AI analysis...")
            except Exception as e:
                print(f"❌ Error analyzing file: {e}")
                sys.exit(1)
        else:
            # Multiple file analysis
            try:
                analyses = analyzer.analyze_multiple_files(csv_files)
                print(analyzer.format_multiple_summaries(analyses))
                
                # Ask if user wants LLM analysis for each file
                print()
                response = input("Generate AI-powered insights for all files? (yes/no): ").strip().lower()
                if response in ("yes", "y"):
                    print()
                    try:
                        llm_analyzer = CSVLLMAnalyzer()
                        for file_name, file_analysis in analyses.items():
                            if "error" not in file_analysis:
                                print(f"\n{'=' * 80}")
                                print(f"AI Insights for: {file_name}")
                                print("=" * 80)
                                insights = llm_analyzer.generate_insights(file_analysis)
                                print(llm_analyzer.format_insights(insights))
                    except Exception as e:
                        print(f"❌ Error generating AI insights: {e}")
                        print("Continuing without AI analysis...")
            except Exception as e:
                print(f"❌ Error analyzing files: {e}")
                sys.exit(1)

        print()
        print("=" * 80)
        print("Analysis complete!")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
