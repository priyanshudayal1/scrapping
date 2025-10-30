"""
Update all 66 scripts with the full scraping logic from legacy_judgements.py
"""
import os
import json

def create_full_script(script_id, start_page, end_page):
    """Generate a complete script with all scraping logic"""
    
    # Read the legacy script
    legacy_file = "legacy_judgements.py"
    
    with open(legacy_file, 'r', encoding='utf-8') as f:
        legacy_content = f.read()
    
    # Extract all function definitions (everything between def and if __name__)
    # Find the start of functions section (after global variables)
    functions_start = legacy_content.find('def load_progress():')
    functions_end = legacy_content.find('if __name__ == "__main__":')
    
    if functions_start < 0 or functions_end < 0:
        raise ValueError("Could not find function definitions in legacy script")
    
    functions_code = legacy_content[functions_start:functions_end].strip()
    
    # Replace legacy variable names with script-specific ones
    # Be more specific with replacements to avoid partial matches
    functions_code = functions_code.replace('os.path.exists(tracking_file)', 'os.path.exists(PROGRESS_FILE)')
    functions_code = functions_code.replace('open(tracking_file,', 'open(PROGRESS_FILE,')
    functions_code = functions_code.replace('f"Progress saved to {tracking_file}"', 'f"Progress saved to {PROGRESS_FILE}"')
    functions_code = functions_code.replace('os.path.exists(timing_file)', 'os.path.exists(TIMING_FILE)')
    functions_code = functions_code.replace('open(timing_file,', 'open(TIMING_FILE,')
    functions_code = functions_code.replace('f"Timing data saved to {timing_file}"', 'f"Timing data saved to {TIMING_FILE}"')
    
    # Replace ALL INSTANCE_ID references with SCRIPT_ID - be very thorough
    functions_code = functions_code.replace("'instance_id'] == INSTANCE_ID", "'instance_id'] == SCRIPT_ID")
    functions_code = functions_code.replace('instance {INSTANCE_ID}', 'script {SCRIPT_ID}')
    functions_code = functions_code.replace('Instance {INSTANCE_ID}', 'Script {SCRIPT_ID}')
    functions_code = functions_code.replace('[Instance {INSTANCE_ID}]', '[Script {SCRIPT_ID}]')
    functions_code = functions_code.replace('Instance ID: {INSTANCE_ID}', 'Script ID: {SCRIPT_ID}')
    functions_code = functions_code.replace('f"Instance {INSTANCE_ID}', 'f"Script {SCRIPT_ID}')
    functions_code = functions_code.replace('"instance_id": INSTANCE_ID', '"script_id": SCRIPT_ID')
    functions_code = functions_code.replace('logger.info(f"Instance ID: {INSTANCE_ID}', 'logger.info(f"Script ID: {SCRIPT_ID}')
    functions_code = functions_code.replace('timing_data["instance_id"] = INSTANCE_ID', 'timing_data["script_id"] = SCRIPT_ID')
    
    # Make Chrome headless
    functions_code = functions_code.replace(
        "# chrome_options.add_argument('--headless')  # Commented out to show browser",
        "chrome_options.add_argument('--headless')  # Run in headless mode"
    )
    
    # Fix any remaining tracking/timing file references in strings
    functions_code = functions_code.replace('f"Progress tracking file: {tracking_file}"', 'f"Progress tracking file: {PROGRESS_FILE}"')
    functions_code = functions_code.replace('f"Timing data file: {timing_file}"', 'f"Timing data file: {TIMING_FILE}"')
    
    # Build the script content
    script_content = f'''"""
Scraping Script {script_id}
Pages: {start_page:,} to {end_page:,}
"""
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import sys
import os

# Load environment variables from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file = os.path.join(parent_dir, 'api+ui', '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

import boto3
import logging
import base64
import json
import time
import requests
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

# Script Configuration
SCRIPT_ID = {script_id}
START_PAGE = {start_page}
END_PAGE = {end_page}
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(SCRIPT_DIR, f"script{script_id}_progress.json")
TIMING_FILE = os.path.join(SCRIPT_DIR, f"script{script_id}_timing.json")

# Configure logging with UTF-8 encoding
log_file = os.path.join(SCRIPT_DIR, f"script{script_id}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Script {script_id}] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize AWS clients
try:
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'ap-south-1')
    )
    bedrock_runtime = session.client("bedrock-runtime")
    s3_client = session.client("s3")
    S3_BUCKET_NAME = "s3-vector-storage"
    logger.info("AWS clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AWS clients: {{str(e)}}")
    bedrock_runtime = None
    s3_client = None
    S3_BUCKET_NAME = None

# Email configuration
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_ENABLED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

# Global variables
driver = None
wait = None
current_page = START_PAGE
total_files_downloaded = 0
start_time = None
batch_size = 25

# All scraping functions from legacy_judgements.py
{functions_code}
'''
    
    # Add the main function
    script_content += f'''

if __name__ == "__main__":
    try:
        logger.info("=" * 80)
        logger.info(f"Starting Script {script_id}")
        logger.info(f"Page Range: {start_page:,} to {end_page:,}")
        logger.info("=" * 80)
        
        # Step 1: Initialize browser and load page
        logger.info("Initializing browser...")
        initialize_browser()

        # Step 2: Solve captcha with retry logic
        logger.info("Solving captcha...")
        if not fill_captcha():
            logger.error("Failed to solve captcha after multiple attempts")
            if driver:
                driver.quit()
            sys.exit(1)
        
        # Step 3: Wait until the loading component is invisible
        logger.info("Waiting for page to load...")
        wait_for_loading_component()
        
        # Step 4: Set table display count to 100
        logger.info("Setting table display count to 100...")
        set_table_display_count()
        
        # Step 5: Start processing all pages
        logger.info("Starting page processing...")
        logger.info("Script execution started successfully")
        process_all_pages()
        
    except KeyboardInterrupt:
        logger.info("\\nScript interrupted by user")
        if driver:
            driver.quit()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main: {{str(e)}}")
        logger.error(traceback.format_exc())
        if EMAIL_ENABLED:
            send_error_notification(
                f"Script {script_id} - Fatal Error",
                f"Error: {{str(e)}}\\n\\nTraceback:\\n{{traceback.format_exc()}}"
            )
        if driver:
            driver.quit()
        sys.exit(1)
'''
    
    return script_content


def update_all_scripts():
    """Update all 66 scripts with full scraping logic"""
    
    # Load configuration
    with open("scripts_distribution_config.json", 'r') as f:
        config = json.load(f)
    
    print("\n🔄 Updating all scripts with full scraping logic...")
    print("=" * 80)
    
    success_count = 0
    error_count = 0
    
    # Process each script from the config
    for script_info in config['scripts']:
        script_id = script_info['script_id']
        start_page = script_info['start_page']
        end_page = script_info['end_page']
        
        try:
            # Generate the full script
            content = create_full_script(script_id, start_page, end_page)
            
            # Write to file
            script_path = f"scrapping-app/scripts/script{script_id}/script{script_id}.py"
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Updated script{script_id} (Pages {start_page:,}-{end_page:,})")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Error updating script{script_id}: {str(e)}")
            error_count += 1
    
    print("=" * 80)
    print(f"✅ Successfully updated {success_count} scripts")
    if error_count > 0:
        print(f"❌ Failed to update {error_count} scripts")
    else:
        print("\n✅ All scripts updated successfully!")
        print("\nScripts now include:")
        print("  • Full scraping logic from legacy_judgements.py")
        print("  • AWS S3 upload functionality")
        print("  • Progress tracking")
        print("  • Error handling and recovery")
        print("  • Email notifications")


if __name__ == "__main__":
    update_all_scripts()
