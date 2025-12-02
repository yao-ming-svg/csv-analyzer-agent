# CSV Analyzer Agent

A Python-based CSV file analyzer that provides comprehensive file summaries and statistical analysis. This is the foundation for an AI-powered data analysis agent.

## Features

### Basic File Summary (Non-LLM)
- File name and path
- Number of rows and columns
- Column names
- Data types for each column
- Memory usage

### Statistical Summary (Non-LLM)
For numerical columns:
- Mean, median, standard deviation
- Min/max values
- Null counts and percentages
- Correlation matrix between numerical columns

For non-numerical columns:
- Unique value counts
- Null counts and percentages
- Most frequent values

### AI-Generated Insights (LLM-Powered)
After the statistical analysis, the agent uses OpenAI to generate:
- **High-Level Summary**: What the dataset represents and key variables
- **Key Trends**: Major patterns, correlations, and what they indicate
- **Anomalies & Data Issues**: Missing values, outliers, data entry errors
- **Beginner-Friendly Explanations**: Natural language explanations of findings

## Installation

1. Install required dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add: `OPENAI_API_KEY=your_api_key_here`
   - Or set it as an environment variable

## Usage

### Web GUI (Recommended)
```bash
python csv_analyzer_server.py
```

Then open your browser and navigate to `http://localhost:5001`

The web interface allows you to:
- Upload one or more CSV files via drag-and-drop or file picker
- View statistical summaries in a formatted display
- Optionally generate AI-powered insights
- See results in a clean, organized interface

### Command Line (Single File)
```bash
python csv_analyzer.py <csv_file>
```

### Command Line (Multiple Files)
```bash
python csv_analyzer.py <csv_file1> <csv_file2> ...
```

### Interactive Mode
```bash
python csv_analyzer_main.py
```

The interactive mode will prompt you to enter one or more CSV file paths.

## Example Output

```
================================================================================
CSV FILE ANALYSIS SUMMARY
================================================================================

📄 FILE SUMMARY
--------------------------------------------------------------------------------
File Name: data.csv
File Path: /path/to/data.csv
Number of Rows: 1,000
Number of Columns: 5
Memory Usage: 40,000 bytes

📊 COLUMN INFORMATION
--------------------------------------------------------------------------------
  • id: int64
  • name: object
  • age: int64
  • salary: float64
  • department: object

📈 STATISTICAL SUMMARY
--------------------------------------------------------------------------------
Numerical Columns: id, age, salary

  Column: age
    Mean: 35.5000
    Median: 35.0000
    Std Dev: 10.2500
    Min: 22.0000
    Max: 65.0000
    Count (non-null): 1,000
    Null Count: 0 (0.00%)

🔗 CORRELATIONS (Numerical Columns)
--------------------------------------------------------------------------------
  age:
    ↔ salary: 0.7500
```

## Project Structure

- `csv_analyzer.py` - Core analyzer module with analysis functions
- `csv_analyzer_main.py` - Interactive command-line program
- `csv_analyzer_server.py` - Flask web server for GUI interface
- `csv_llm_analyzer.py` - LLM-powered insights generator
- `templates/csv_analyzer.html` - Web interface template
- `requirements.txt` - Python dependencies

## Example AI Output

```
🤖 AI-GENERATED INSIGHTS
================================================================================

📊 HIGH-LEVEL SUMMARY
--------------------------------------------------------------------------------
This dataset appears to track employee information across different departments.
There are 10 rows and 5 columns, with a mix of numerical (id, age, salary) and
categorical (name, department) data. The dataset shows a small sample of
employees with their basic demographic and compensation information.

📈 KEY TRENDS
--------------------------------------------------------------------------------
The data reveals a strong positive correlation (0.98) between age and salary,
indicating that older employees tend to earn more. The salary distribution shows
moderate variability with a standard deviation of approximately $13,888...

⚠️  ANOMALIES OR DATA ISSUES
--------------------------------------------------------------------------------
No significant data quality issues detected. All columns have complete data with
no missing values. The age range (27-45) and salary range ($52,000-$92,000)
appear reasonable for an employee dataset.

💡 EXPLANATION FOR BEGINNERS
--------------------------------------------------------------------------------
In simple terms: as employees get older, they tend to earn higher salaries.
This makes sense because more experienced workers typically command higher pay.
The data shows a clear pattern where age and salary move together - when one
increases, the other tends to increase as well.
```

## Future Enhancements

- Data visualization recommendations
- Export insights to reports
- Batch processing for large datasets
- Custom analysis prompts

