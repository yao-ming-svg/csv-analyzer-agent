"""
Flask server for CSV Analyzer with web GUI.

Provides a web interface for uploading and analyzing CSV files
with both statistical analysis and AI-powered insights.
"""

import os
import sys
import io
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
                    result = {
                        'filename': file.filename,
                        'file_summary': analysis['file_summary'],
                        'statistical_summary': analysis['statistical_summary'],
                        'formatted_summary': None,
                        'ai_insights': None
                    }
                    
                    # Format the summary
                    analyzer = CSVAnalyzer()
                    result['formatted_summary'] = analyzer.format_summary(analysis)
                    
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

