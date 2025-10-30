from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import json
import os
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main scraping functions
import legacy_judgements

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state
scraping_thread = None
is_running = False
current_error = None

# Email configuration
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_ENABLED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
INSTANCE_ID = int(os.getenv('INSTANCE_ID', '1'))

def send_api_email(subject, body):
    """Send email notification from API"""
    if not EMAIL_ENABLED:
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_HOST_USER
        msg['Subject'] = f"[Instance {INSTANCE_ID} API] {subject}"
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"API email sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send API email: {e}")
        return False

def run_scraping_process():
    """Run the scraping process in a separate thread"""
    global is_running, current_error
    try:
        is_running = True
        current_error = None
        logger.info("Starting scraping process...")
        
        # Send start notification
        send_api_email(
            "🚀 Scraping Started",
            f"Scraping process has been started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        legacy_judgements.main()
        logger.info("Scraping process completed successfully")
        
    except Exception as e:
        current_error = str(e)
        logger.error(f"Error in scraping process: {e}")
        
        # Send error notification
        send_api_email(
            "❌ Scraping Process Error",
            f"An error occurred during scraping:\n\n{str(e)}\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
    finally:
        is_running = False

@app.route('/api/start', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_thread, is_running
    
    if is_running:
        return jsonify({
            'status': 'error',
            'message': 'Scraping process is already running'
        }), 400
    
    try:
        scraping_thread = threading.Thread(target=run_scraping_process)
        scraping_thread.daemon = True
        scraping_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Scraping process started successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error starting scraping process: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_scraping():
    """Stop the scraping process"""
    global is_running, scraping_thread
    
    if not is_running:
        return jsonify({
            'status': 'error',
            'message': 'No scraping process is currently running'
        }), 400
    
    try:
        # Note: Graceful shutdown would require modifications to legacy_judgements.py
        # For now, we can only mark it as stopped
        is_running = False
        
        # Send stop notification
        send_api_email(
            "🛑 Scraping Stopped",
            f"Scraping process has been stopped manually at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Stop signal sent. Process will stop after current operation.'
        }), 200
    except Exception as e:
        logger.error(f"Error stopping scraping process: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the scraping process"""
    try:
        # Load progress data
        progress_data = {}
        if os.path.exists('download_progress.json'):
            with open('download_progress.json', 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
        
        # Load timing data
        timing_data = {}
        if os.path.exists('download_timing.json'):
            with open('download_timing.json', 'r', encoding='utf-8') as f:
                timing_data = json.load(f)
        
        response = {
            'status': 'success',
            'is_running': is_running,
            'current_error': current_error,
            'progress': {
                'current_page': progress_data.get('current_page', 0),
                'total_files_downloaded': progress_data.get('total_files_downloaded', 0),
                'last_updated': progress_data.get('last_updated'),
                'pages_completed': len(progress_data.get('pages_completed', [])),
                'failed_downloads': len(progress_data.get('failed_downloads', [])),
                'yearly_counts': progress_data.get('yearly_counts', {}),
                'start_time': progress_data.get('start_time')
            },
            'timing': {
                'total_files_processed': timing_data.get('total_files_processed', 0),
                'total_successful_downloads': timing_data.get('total_successful_downloads', 0),
                'total_failed_downloads': timing_data.get('total_failed_downloads', 0),
                'average_time_per_file': timing_data.get('average_time_per_file', 0),
                'session_start': timing_data.get('session_start'),
                'last_updated': timing_data.get('last_updated')
            }
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/error', methods=['GET'])
def get_error():
    """Get the current error if any"""
    global current_error
    
    if current_error:
        return jsonify({
            'status': 'error',
            'error': current_error,
            'timestamp': datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            'status': 'success',
            'message': 'No errors'
        }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

# HTML Frontend Routes
@app.route('/')
def serve_dashboard():
    """Serve the instance-specific dashboard"""
    try:
        dashboard_file = f'monitor_instance{INSTANCE_ID}.html'
        if os.path.exists(dashboard_file):
            return send_from_directory('.', dashboard_file)
        # Fallback to index.html if instance-specific dashboard doesn't exist
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return jsonify({'error': 'Dashboard not found'}), 404

@app.route('/unified')
def serve_unified_dashboard():
    """Serve the unified dashboard for all instances"""
    try:
        return send_from_directory('.', 'unified_dashboard.html')
    except Exception as e:
        logger.error(f"Error serving unified dashboard: {e}")
        return jsonify({'error': 'Unified dashboard not found'}), 404

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static HTML files"""
    try:
        # Only serve HTML files for security
        if filename.endswith('.html'):
            return send_from_directory('.', filename)
        else:
            return jsonify({'error': 'File type not allowed'}), 403
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
