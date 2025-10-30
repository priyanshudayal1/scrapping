"""
Enhanced API Server for Multi-Script Orchestration
Manages 66 scripts distributed across instances
"""
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
from pathlib import Path

# Load environment variables
load_dotenv()

# Import orchestrator
from script_orchestrator import get_orchestrator

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
INSTANCE_ID = int(os.getenv('INSTANCE_ID', '1'))
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# Email configuration
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_ENABLED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

# Initialize orchestrator
try:
    orchestrator = get_orchestrator(str(SCRIPTS_DIR), INSTANCE_ID)
    logger.info(f"Orchestrator initialized for Instance {INSTANCE_ID}")
except Exception as e:
    logger.error(f"Failed to initialize orchestrator: {e}")
    orchestrator = None

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

# ==================== Script Management Endpoints ====================

@app.route('/api/scripts/start', methods=['POST'])
def start_scripts():
    """Start N scripts sequentially"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        data = request.get_json()
        num_scripts = data.get('num_scripts', 1)
        delay = data.get('delay', 2)  # Delay between starts in seconds
        
        if num_scripts < 1:
            return jsonify({'status': 'error', 'message': 'num_scripts must be at least 1'}), 400
        
        orchestrator.start_n_scripts(num_scripts, delay)
        
        send_api_email(
            f"🚀 Starting {num_scripts} Scripts",
            f"Started {num_scripts} scripts sequentially at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Starting {num_scripts} scripts sequentially',
            'num_scripts': num_scripts,
            'delay': delay
        }), 200
    except Exception as e:
        logger.error(f"Error starting scripts: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scripts/start/<int:script_id>', methods=['POST'])
def start_single_script(script_id):
    """Start a specific script"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        orchestrator.start_script(script_id)
        return jsonify({
            'status': 'success',
            'message': f'Script {script_id} started successfully',
            'script_id': script_id
        }), 200
    except Exception as e:
        logger.error(f"Error starting script {script_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scripts/stop/<int:script_id>', methods=['POST'])
def stop_single_script(script_id):
    """Stop a specific script"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        orchestrator.stop_script(script_id)
        return jsonify({
            'status': 'success',
            'message': f'Script {script_id} stopped successfully',
            'script_id': script_id
        }), 200
    except Exception as e:
        logger.error(f"Error stopping script {script_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scripts/stop-all', methods=['POST'])
def stop_all_scripts():
    """Stop all running scripts"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        orchestrator.stop_all_scripts()
        
        send_api_email(
            "🛑 All Scripts Stopped",
            f"All running scripts stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return jsonify({
            'status': 'success',
            'message': 'All scripts stopped successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error stopping all scripts: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Status Endpoints ====================

@app.route('/api/status', methods=['GET'])
def get_overall_status():
    """Get overall instance status with all scripts"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        status = orchestrator.get_overall_status()
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scripts/<int:script_id>/status', methods=['GET'])
def get_script_status(script_id):
    """Get status of a specific script"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        status = orchestrator.get_script_status(script_id)
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting script {script_id} status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scripts/<int:script_id>/logs', methods=['GET'])
def get_script_logs(script_id):
    """Get recent logs from a specific script"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    try:
        lines = request.args.get('lines', 50, type=int)
        logs = orchestrator.get_script_logs(script_id, lines)
        return jsonify({
            'status': 'success',
            'script_id': script_id,
            'logs': logs,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting script {script_id} logs: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/instance/info', methods=['GET'])
def get_instance_info():
    """Get instance configuration information"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    return jsonify({
        'status': 'success',
        'instance_id': INSTANCE_ID,
        'assigned_scripts': orchestrator.assigned_scripts,
        'total_scripts': len(orchestrator.assigned_scripts),
        'scripts_dir': str(SCRIPTS_DIR)
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'instance_id': INSTANCE_ID,
        'orchestrator_ready': orchestrator is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== HTML Frontend Routes ====================

@app.route('/')
def serve_dashboard():
    """Serve the instance-specific dashboard"""
    try:
        # Serve multi_script_dashboard.html as the main dashboard
        if os.path.exists('multi_script_dashboard.html'):
            return send_from_directory('.', 'multi_script_dashboard.html')
        # Fallback to instance-specific dashboard
        dashboard_file = f'monitor_instance{INSTANCE_ID}.html'
        if os.path.exists(dashboard_file):
            return send_from_directory('.', dashboard_file)
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

@app.route('/dashboard/<filename>')
def serve_dashboard_files(filename):
    """Serve specific dashboard HTML files"""
    try:
        if filename.endswith('.html') and os.path.exists(filename):
            return send_from_directory('.', filename)
        else:
            return jsonify({'error': 'Dashboard not found'}), 404
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    logger.info(f"Starting API Server for Instance {INSTANCE_ID}")
    logger.info(f"Assigned Scripts: {orchestrator.assigned_scripts if orchestrator else 'N/A'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
