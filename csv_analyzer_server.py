"""
Flask server for CSV Analyzer with web GUI.

Provides a web interface for uploading and analyzing CSV files
with both statistical analysis and AI-powered insights.
"""

import os
import sys
import io
import json
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set console encoding to UTF-8
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Import our CSV analyzer modules
from csv_analyzer import CSVAnalyzer
from csv_llm_analyzer import CSVLLMAnalyzer


def convert_to_native_types(obj):
    """
    Recursively convert numpy/pandas types to native Python types for JSON serialization.
    
    Args:
        obj: Object that may contain numpy/pandas types
        
    Returns:
        Object with all numpy/pandas types converted to native Python types
    """
    # Handle pandas/numpy NaN values first
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    
    # Handle numpy integer types
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    # Handle numpy float types
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    # Handle numpy boolean types
    elif isinstance(obj, np.bool_):
        return bool(obj)
    # Handle numpy arrays
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    # Handle pandas Series
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    # Handle dictionaries
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    # Handle lists and tuples
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    # Handle strings (pandas sometimes returns object types)
    elif isinstance(obj, str):
        return str(obj)
    # Default: return as-is (should be a native Python type)
    else:
        return obj

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_csv_file(file):
    """
    Process uploaded CSV file and return analysis.
    
    Args:
        file: Flask file object
        
    Returns:
        Tuple of (analysis_dict, error_message)
    """
    if not allowed_file(file.filename):
        return None, "File type not allowed. Please upload CSV files only."

    try:
        # Read file into memory
        file_bytes = file.read()
        
        # Create a temporary file-like object
        file_stream = io.BytesIO(file_bytes)
        file_stream.seek(0)
        
        # Save to temporary file for pandas
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Analyze the CSV file
            analyzer = CSVAnalyzer()
            analysis = analyzer.analyze_file(tmp_path)
            return analysis, None
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
                
    except Exception as e:
        return None, f"Error processing CSV file: {str(e)}"

@app.route('/analyze-csv', methods=['POST'])
def analyze_csv():
    """Analyze uploaded CSV file(s) and return results."""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files or not files[0].filename:
            return jsonify({'error': 'No files selected'}), 400
        
        # Get options
        include_ai_insights = request.form.get('include_ai_insights', 'false').lower() == 'true'
        
        results = []
        
        for file in files:
            if file and file.filename:
                analysis, error = process_csv_file(file)
                
                if error:
                    results.append({
                        'filename': file.filename,
                        'error': error
                    })
                else:
                    # Convert numpy/pandas types to native Python types for JSON serialization
                    file_summary = convert_to_native_types(analysis['file_summary'])
                    statistical_summary = convert_to_native_types(analysis['statistical_summary'])
                    
                    # Format as structured JSON
                    analyzer = CSVAnalyzer()
                    json_summary = analyzer.format_as_json(analysis)
                    json_summary = convert_to_native_types(json_summary)
                    
                    result = {
                        'filename': file.filename,
                        'file_summary': file_summary,
                        'statistical_summary': statistical_summary,
                        'formatted_summary': json_summary,  # Now returns structured JSON
                        'ai_insights': None
                    }
                    
                    # Generate AI insights if requested
                    if include_ai_insights:
                        try:
                            llm_analyzer = CSVLLMAnalyzer()
                            insights = llm_analyzer.generate_insights(analysis)
                            result['ai_insights'] = {
                                'high_level_summary': insights.get('high_level_summary', ''),
                                'key_trends': insights.get('key_trends', ''),
                                'anomalies': insights.get('anomalies', ''),
                                'beginner_explanation': insights.get('beginner_explanation', ''),
                                'formatted': llm_analyzer.format_insights(insights)
                            }
                        except Exception as e:
                            result['ai_insights_error'] = str(e)
                    
                    results.append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'files_processed': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'CSV Analyzer API is running'
    })

@app.route('/', methods=['GET'])
def home():
    """Serve the main web interface."""
    return render_template('csv_analyzer.html')

@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        'message': 'CSV Analyzer API',
        'endpoints': {
            'POST /analyze-csv': 'Analyze uploaded CSV file(s)',
            'GET /health': 'Health check',
            'GET /': 'Web interface',
            'GET /api': 'This documentation'
        },
        'parameters': {
            'files': 'Upload CSV file(s) (required)',
            'include_ai_insights': 'Include AI-powered insights (true/false, default: false)'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

