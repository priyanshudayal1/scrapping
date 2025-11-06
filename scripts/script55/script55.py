"""
Scraping Script 55
Pages: 138,187 to 140,745
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
import random
import tempfile
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

logger = logging.getLogger(__name__)

# Import for process management and cleanup
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - process cleanup will be limited")

try:
    import shutil
    SHUTIL_AVAILABLE = True
except ImportError:
    SHUTIL_AVAILABLE = False

# Script Configuration
SCRIPT_ID = 55
START_PAGE = 138187
END_PAGE = 140745
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(SCRIPT_DIR, f"script55_progress.json")
TIMING_FILE = os.path.join(SCRIPT_DIR, f"script55_timing.json")

# Configure logging with UTF-8 encoding
log_file = os.path.join(SCRIPT_DIR, f"script55.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Script 55] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


# Initialize Google Cloud Vision API credentials
try:
    from google.cloud import vision_v1
    from google.oauth2 import service_account
    
    credentials = service_account.Credentials.from_service_account_info({
        "type": "service_account",
        "project_id": os.getenv('GCP_PROJECT_ID'),
        "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID'),
        "private_key": os.getenv('GCP_PRIVATE_KEY', '').replace('\\\\n', '\\n'),
        "client_email": os.getenv('GCP_CLIENT_EMAIL'),
        "client_id": os.getenv('GCP_CLIENT_ID'),
        "auth_uri": os.getenv('GCP_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
        "token_uri": os.getenv('GCP_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
        "auth_provider_x509_cert_url": os.getenv('GCP_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
        "client_x509_cert_url": os.getenv('GCP_CLIENT_CERT_URL'),
    })
    vision_client = vision_v1.ImageAnnotatorClient(credentials=credentials)
    logger.info("Google Cloud Vision API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud Vision API: {str(e)}")
    vision_client = None

# Initialize AWS S3 client for file uploads
try:
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'ap-south-1')
    )
    s3_client = session.client("s3")
    S3_BUCKET_NAME = "s3-vector-storage"
    logger.info("AWS S3 client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AWS S3 client: {str(e)}")
    s3_client = None
    S3_BUCKET_NAME = None

# Email configuration - DISABLED FOR TESTING
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_ENABLED = False  # Disabled to prevent email spam during testing

# Global variables
driver = None
wait = None
current_page = START_PAGE
total_files_downloaded = 0
start_time = None


def cleanup_resources():
    """Clean up browser resources for this script instance ONLY"""
    global driver
    try:
        if driver:
            logger.info(f"Cleaning up browser resources for Script {SCRIPT_ID}")
            
            # Quit the driver gracefully - this will close only this script's Chrome instance
            try:
                driver.quit()
                logger.debug("WebDriver quit successfully")
            except Exception as quit_error:
                logger.warning(f"Error quitting WebDriver: {quit_error}")
            
            driver = None
            
            # Only clean up Chrome processes that specifically belong to THIS script's profile
            # This ensures we don't touch any other Chrome windows or instances
            if PSUTIL_AVAILABLE:
                try:
                    # Only terminate Chrome processes with OUR SPECIFIC profile in the command line
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                                if proc.info['cmdline']:
                                    cmdline = ' '.join(proc.info['cmdline'])
                                    # CRITICAL: Only match Chrome processes with this exact profile
                                    if f'chrome_profile_script_{SCRIPT_ID}_' in cmdline:
                                        logger.debug(f"Terminating Chrome process {proc.info['pid']} for Script {SCRIPT_ID}")
                                        proc.terminate()
                                        proc.wait(timeout=3)
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                            pass
                except Exception as proc_error:
                    logger.warning(f"Error during process cleanup: {proc_error}")
                
            # Clean up only THIS script's profile and cache directories
            if SHUTIL_AVAILABLE:
                try:
                    import tempfile
                    temp_dir = tempfile.gettempdir()  # Cross-platform temp directory
                    if os.path.exists(temp_dir):
                        for item in os.listdir(temp_dir):
                            # Only delete profiles/caches that start with our script ID
                            if (item.startswith(f'chrome_profile_script_{SCRIPT_ID}_') or 
                                item.startswith(f'chrome_cache_script_{SCRIPT_ID}_') or
                                item.startswith(f'chrome_crashes_script_{SCRIPT_ID}_')):
                                dir_path = os.path.join(temp_dir, item)
                                if os.path.isdir(dir_path):
                                    try:
                                        shutil.rmtree(dir_path, ignore_errors=True)
                                        logger.debug(f"Cleaned up directory: {dir_path}")
                                    except Exception as cleanup_error:
                                        logger.debug(f"Could not clean up {dir_path}: {cleanup_error}")
                except Exception as dir_cleanup_error:
                    logger.debug(f"Error during directory cleanup: {dir_cleanup_error}")
                
            logger.info(f"Cleanup completed for Script {SCRIPT_ID}")
            
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")


def force_cleanup_chrome_processes():
    """Force cleanup of any hanging Chrome processes for this script ONLY"""
    try:
        if not PSUTIL_AVAILABLE:
            logger.debug("psutil not available for force cleanup")
            return
            
        logger.info(f"Force cleaning Chrome processes for Script {SCRIPT_ID}")
        
        terminated_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        # CRITICAL: Only terminate Chrome with THIS script's unique profile (with timestamp)
                        # This prevents killing other Chrome instances including user's personal browser
                        if f'chrome_profile_script_{SCRIPT_ID}_' in cmdline:
                            logger.debug(f"Force terminating Chrome process {proc.info['pid']} for Script {SCRIPT_ID}")
                            proc.kill()
                            terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        if terminated_count > 0:
            logger.info(f"Force terminated {terminated_count} Chrome processes for Script {SCRIPT_ID}")
        else:
            logger.debug(f"No hanging Chrome processes found for Script {SCRIPT_ID}")
            
    except Exception as e:
        logger.warning(f"Error during force cleanup: {e}")


def check_port_availability():
    """Check if the debugging port for this script is available"""
    try:
        import socket
        
        debug_port = 9222 + SCRIPT_ID
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', debug_port))
        sock.close()
        
        if result == 0:
            logger.warning(f"Port {debug_port} is already in use by another process")
            
            # Try to find and terminate the conflicting process ONLY if it's our script's Chrome
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            # Only terminate if BOTH the port AND our profile are in the command line
                            # This prevents terminating other Chrome instances that happen to use the same port
                            if f'remote-debugging-port={debug_port}' in cmdline and f'chrome_profile_script_{SCRIPT_ID}_' in cmdline:
                                logger.info(f"Terminating conflicting process {proc.info['pid']} using port {debug_port}")
                                proc.terminate()
                                proc.wait(timeout=5)
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
            
            return False
        else:
            logger.debug(f"Port {debug_port} is available for Script {SCRIPT_ID}")
            return True
            
    except Exception as e:
        logger.warning(f"Error checking port availability: {e}")
        return True  # Assume available if we can't check


def pre_launch_cleanup():
    """Cleanup any existing resources before launching new browser instance"""
    logger.info(f"Performing pre-launch cleanup for Script {SCRIPT_ID}")
    
    # Check and cleanup port conflicts
    if not check_port_availability():
        logger.info("Waiting for port to become available...")
        time.sleep(5)
        
        # Check again after cleanup
        if not check_port_availability():
            logger.warning(f"Port {9222 + SCRIPT_ID} still in use, but proceeding anyway")
    
    # Cleanup any existing profile, cache, and crash directories
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()  # Cross-platform temp directory
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                # Clean up all Chrome-related directories for this script
                if (item.startswith(f'chrome_profile_script_{SCRIPT_ID}_') or 
                    item.startswith(f'chrome_cache_script_{SCRIPT_ID}_') or
                    item.startswith(f'chrome_crashes_script_{SCRIPT_ID}_')):
                    dir_path = os.path.join(temp_dir, item)
                    if os.path.isdir(dir_path):
                        try:
                            if SHUTIL_AVAILABLE:
                                shutil.rmtree(dir_path, ignore_errors=True)
                                logger.debug(f"Cleaned up existing directory: {dir_path}")
                        except Exception as cleanup_error:
                            logger.debug(f"Could not clean up {dir_path}: {cleanup_error}")
    except Exception as e:
        logger.debug(f"Error during pre-launch directory cleanup: {e}")
    
    # Force cleanup any hanging Chrome processes for this script
    force_cleanup_chrome_processes()
    
    logger.info(f"Pre-launch cleanup completed for Script {SCRIPT_ID}")

# All scraping functions from legacy_judgements.py
def load_progress():
    """Load progress from JSON file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading progress file: {e}")
    
    return {
        "current_page": 1,
        "total_files_downloaded": 0,
        "start_time": None,
        "downloaded_files": [],
        "last_updated": None,
        "pages_completed": [],
        "current_batch_on_page": 0,
        "yearly_counts": {},
        "failed_downloads": []
    }


def save_progress(progress_data):
    """Save progress to JSON file"""
    try:
        progress_data["last_updated"] = datetime.now().isoformat()
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Progress saved to {PROGRESS_FILE}")
    except Exception as e:
        logger.error(f"Error saving progress: {e}")


def load_timing_data():
    """Load timing data from JSON file"""
    try:
        if os.path.exists(TIMING_FILE):
            with open(TIMING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading timing file: {e}")
    
    return {
        "session_start": None,
        "session_end": None,
        "total_files_processed": 0,
        "total_successful_downloads": 0,
        "total_failed_downloads": 0,
        "total_time_seconds": 0,
        "average_time_per_file": 0,
        "individual_file_times": [],
        "session_statistics": [],
        "fastest_download": None,
        "slowest_download": None,
        "last_updated": None
    }


def save_timing_data(timing_data):
    """Save timing data to JSON file"""
    try:
        timing_data["last_updated"] = datetime.now().isoformat()
        with open(TIMING_FILE, 'w', encoding='utf-8') as f:
            json.dump(timing_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Timing data saved to {TIMING_FILE}")
    except Exception as e:
        logger.error(f"Error saving timing data: {e}")


def update_timing_stats(timing_data, file_info, download_time_seconds, success=True):
    """Update timing statistics with new download data"""
    try:
        # Individual file timing
        file_timing = {
            "filename": file_info.get('filename', 'unknown'),
            "case_title": file_info.get('case_title', 'unknown')[:50],
            "download_time_seconds": round(download_time_seconds, 2),
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "cnr": file_info.get('cnr', ''),
            "decision_year": file_info.get('decision_year')
        }
        
        timing_data["individual_file_times"].append(file_timing)
        
        # Update overall statistics
        timing_data["total_files_processed"] += 1
        if success:
            timing_data["total_successful_downloads"] += 1
            
            # Update fastest/slowest records
            if not timing_data["fastest_download"] or download_time_seconds < timing_data["fastest_download"]["time"]:
                timing_data["fastest_download"] = {
                    "filename": file_info.get('filename', 'unknown'),
                    "time": round(download_time_seconds, 2),
                    "case_title": file_info.get('case_title', 'unknown')[:50]
                }
            
            if not timing_data["slowest_download"] or download_time_seconds > timing_data["slowest_download"]["time"]:
                timing_data["slowest_download"] = {
                    "filename": file_info.get('filename', 'unknown'),
                    "time": round(download_time_seconds, 2),
                    "case_title": file_info.get('case_title', 'unknown')[:50]
                }
        else:
            timing_data["total_failed_downloads"] += 1
        
        # Calculate running averages (only for successful downloads)
        successful_times = [f["download_time_seconds"] for f in timing_data["individual_file_times"] if f["success"]]
        if successful_times:
            timing_data["average_time_per_file"] = round(sum(successful_times) / len(successful_times), 2)
        
        return timing_data
        
    except Exception as e:
        logger.error(f"Error updating timing stats: {e}")
        return timing_data


def sanitize_filename(filename):
    """Sanitize filename by removing/replacing invalid characters"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces with single underscore
    filename = ' '.join(filename.split())
    filename = filename.replace(' ', '_')
    
    # Limit length to avoid filesystem issues
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def upload_to_s3(file_path, s3_key):
    """Upload file to S3 bucket"""
    try:
        if s3_client is None:
            logger.error("S3 client is not initialized")
            return False
        
        logger.info(f"Uploading {file_path} to S3 bucket {S3_BUCKET_NAME}...")
        
        with open(file_path, 'rb') as file_data:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_data,
                ContentType='application/pdf'
            )
        
        logger.info(f"Successfully uploaded to S3: {s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return False


def delete_local_file(file_path):
    """Delete local file after successful upload"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted local file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting local file {file_path}: {e}")
        return False


def send_email(subject, body, is_html=False):
    """Send email notification - DISABLED FOR TESTING"""
    logger.info(f"EMAIL DISABLED - Would send: {subject}")
    return False  # Emails disabled
    if not EMAIL_ENABLED:
        logger.warning("Email notifications disabled - missing credentials")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_HOST_USER  # Sending to same email
        msg['Subject'] = f"[Script {SCRIPT_ID}] {subject}"
        
        # Attach body
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_error_notification(error_message, error_details=""):
    """Send error notification email - DISABLED FOR TESTING"""
    logger.warning(f"EMAIL DISABLED - Error notification: {error_message}")
    return False  # Emails disabled
    subject = "[WARNING] Scraping Error Occurred"
    
    body = f"""
Judgement Scraping Error Alert

Script ID: {SCRIPT_ID}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error Message:
{error_message}

Error Details:
{error_details}

Please check the logs and take necessary action.

---
Automated notification from Judgement Scraping System
"""
    
    send_email(subject, body)


def send_completion_notification(stats):
    """Send completion notification email - DISABLED FOR TESTING"""
    logger.info("EMAIL DISABLED - Completion notification suppressed")
    return False  # Emails disabled
    subject = "[SUCCESS] Scraping Completed Successfully"
    
    body = f"""
Judgement Scraping Completion Report

Script ID: {SCRIPT_ID}
Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTICS:
-----------
Total Files Downloaded: {stats.get('total_downloaded', 0):,}
Total Pages Processed: {stats.get('total_pages', 0):,}
Failed Downloads: {stats.get('failed_count', 0):,}
Success Rate: {stats.get('success_rate', 0):.1f}%

TIMING:
-------
Total Time: {stats.get('total_time_minutes', 0):.1f} minutes ({stats.get('total_time_hours', 0):.1f} hours)
Average Time per File: {stats.get('avg_time_per_file', 0):.2f} seconds

PAGE RANGE:
-----------
Start Page: {stats.get('start_page', 'N/A')}
End Page: {stats.get('end_page', 'N/A')}
Pages Completed: {stats.get('pages_completed', 0)}

YEARLY DISTRIBUTION:
{stats.get('yearly_summary', 'N/A')}

All PDFs have been uploaded to S3 bucket: s3-vector-storage

---
Automated notification from Judgement Scraping System
"""
    
    send_email(subject, body)


def send_shutdown_notification(reason="Unknown"):
    """Send notification when script stops unexpectedly - DISABLED FOR TESTING"""
    logger.warning(f"EMAIL DISABLED - Shutdown notification: {reason}")
    return False  # Emails disabled
    subject = "🛑 Scraping Process Stopped"
    
    body = f"""
Judgement Scraping Process Stopped

Script ID: {SCRIPT_ID}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reason: {reason}

The scraping process has stopped. Please investigate and restart if necessary.

---
Automated notification from Judgement Scraping System
"""
    
    send_email(subject, body)


def load_distributed_config():
    """Load distributed configuration for this instance"""
    global START_PAGE, END_PAGE, TOTAL_RESULTS
    
    try:
        # Look for config file in the project root (3 levels up from script directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        config_file = os.path.join(project_root, "distributed_config.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            TOTAL_RESULTS = config.get('total_results', 16886658)
            
            # Find configuration for this instance
            for instance in config.get('instances', []):
                if instance['instance_id'] == SCRIPT_ID:
                    START_PAGE = instance['start_page']
                    END_PAGE = instance['end_page']
                    logger.info(f"Script {SCRIPT_ID} configured: Pages {START_PAGE} to {END_PAGE}")
                    logger.info(f"Description: {instance.get('description', 'N/A')}")
                    return True
            
            logger.warning(f"No configuration found for script {SCRIPT_ID}, using defaults")
            return False
        else:
            logger.warning(f"Distributed config file not found: {config_file}")
            return False
            
    except Exception as e:
        logger.error(f"Error loading distributed config: {e}")
        return False


def extract_total_results():
    """Extract total number of results from the page"""
    try:
        search_timer = wait.until(EC.presence_of_element_located((By.ID, "search_timer")))
        text = search_timer.text
        
        # Extract number from text like "About 1,68,86,658 results (0 seconds)"
        import re
        match = re.search(r'About\s+([\d,]+)\s+results', text)
        if match:
            total_str = match.group(1).replace(',', '')
            total = int(total_str)
            logger.info(f"Total results found: {total:,}")
            return total
        else:
            logger.warning("Could not extract total results from page")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting total results: {e}")
        return None


def navigate_to_specific_page(target_page, max_retries=3):
    """Navigate to a specific page number by clicking 'Next' button repeatedly"""
    global current_page, driver, wait
    
    for retry in range(max_retries):
        try:
            if driver is None:
                logger.error("Driver is None, cannot navigate")
                return False
            
            try:
                driver.current_url
            except Exception as e:
                logger.error(f"Driver is not responsive: {e}")
                if retry < max_retries - 1:
                    logger.info("Attempting to recover browser session...")
                    if recover_browser_session():
                        continue
                return False
            
            # CRITICAL FIX: Always start from page 1 when we need to navigate
            # The website pagination works by clicking Next from page 1
            actual_current = 1  # We always assume we're starting from page 1 after captcha
            
            logger.info(f"Navigating from page {actual_current} to page {target_page}...")
            logger.info(f"This will require clicking 'Next' {target_page - actual_current} times")
            
            if target_page == 1:
                logger.info("Already on page 1, no navigation needed")
                current_page = 1
                return True
            
            # Click Next button (target_page - 1) times to reach the target page
            clicks_needed = target_page - actual_current
            
            for click_num in range(clicks_needed):
                try:
                    logger.info(f"Navigation progress: {click_num + 1}/{clicks_needed} (Current page: {actual_current + click_num}, Target: {target_page})")
                    
                    # Find and verify Next button
                    next_button = wait.until(EC.element_to_be_clickable((By.ID, "example_pdf_next")))
                    
                    # Check if button is disabled
                    button_class = next_button.get_attribute("class") or ""
                    if "disabled" in button_class:
                        logger.error(f"Cannot navigate further. 'Next' button is disabled after {click_num} clicks.")
                        logger.error(f"Reached page {actual_current + click_num}, but target was {target_page}")
                        return False
                    
                    # Click the Next button
                    next_button.click()
                    
                    # Wait for page transition
                    time.sleep(2)
                    
                    # Wait for new table data to load
                    wait.until(EC.presence_of_element_located((By.ID, "report_body")))
                    
                    # Add extra wait for table to fully render
                    time.sleep(1)
                    
                    # Log progress every 100 pages
                    if (click_num + 1) % 100 == 0:
                        logger.info(f"✓ Navigated through {click_num + 1} pages...")
                    
                except Exception as click_error:
                    logger.error(f"Error clicking Next button at iteration {click_num + 1}: {click_error}")
                    
                    # Try to recover and continue
                    if click_num > 0 and retry < max_retries - 1:
                        logger.warning(f"Navigation interrupted at page {actual_current + click_num}. Retrying entire navigation...")
                        time.sleep(5)
                        break
                    else:
                        raise click_error
            
            else:
                # Successfully completed all clicks
                current_page = target_page
                logger.info(f"✓ Successfully navigated to page {target_page}")
                return True
            
        except Exception as e:
            logger.error(f"Error navigating to page {target_page} (attempt {retry + 1}/{max_retries}): {e}")
            logger.error(traceback.format_exc())
            
            if retry < max_retries - 1:
                logger.info(f"Retrying navigation after {10 * (retry + 1)} seconds...")
                time.sleep(10 * (retry + 1))
                
                # Try to reinitialize session before retry
                if retry == max_retries - 2:
                    logger.info("Last retry - attempting full session recovery...")
                    if not recover_browser_session():
                        logger.error("Session recovery failed")
                        return False
            else:
                logger.error(f"Failed to navigate to page {target_page} after {max_retries} attempts")
                return False
    
    return False


def close_any_open_modal():
    """Close any open modal if it exists"""
    try:
        # Check if modal exists and is visible
        modal_elements = driver.find_elements(By.ID, "viewFiles")
        
        for modal in modal_elements:
            if modal.is_displayed():
                logger.info("Found open modal, attempting to close...")
                
                # Try to find and click close button
                try:
                    close_button = modal.find_element(By.ID, "modal_close")
                    if close_button.is_displayed():
                        close_button.click()
                        logger.info("Modal close button clicked")
                        
                        # Wait for modal to disappear
                        wait.until(EC.invisibility_of_element_located((By.ID, "viewFiles")))
                        logger.info("Modal closed successfully")
                        return True
                        
                except Exception as close_error:
                    logger.warning(f"Failed to close modal with close button: {close_error}")
                    
                    # Try JavaScript approach
                    try:
                        driver.execute_script("document.getElementById('viewFiles').style.display = 'none';")
                        logger.info("Modal closed using JavaScript")
                        return True
                    except Exception as js_error:
                        logger.warning(f"Failed to close modal with JavaScript: {js_error}")
                        
                    # Try pressing Escape key
                    try:
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        logger.info("Sent Escape key to close modal")
                        time.sleep(1)
                        return True
                    except Exception as esc_error:
                        logger.warning(f"Failed to close modal with Escape key: {esc_error}")
        
        return False
        
    except Exception as e:
        logger.debug(f"No modal found or error checking for modal: {e}")
        return False

def initialize_browser():
    global driver, wait
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # CRITICAL: Multi-instance isolation - each script gets unique resources
    import random
    instance_random = random.randint(1000, 9999)
    
    # Multi-instance isolation options
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    
    # Process isolation and stability - CRITICAL for concurrent execution
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI,BlinkGenPropertyTrees')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    chrome_options.add_argument('--disable-hang-monitor')
    chrome_options.add_argument('--disable-prompt-on-repost')
    chrome_options.add_argument('--disable-domain-reliability')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    
    # Shared memory isolation - prevents scripts from interfering with each other
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--force-device-scale-factor=1')
    
    # Memory and performance optimization
    chrome_options.add_argument('--max_old_space_size=4096')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max-unused-resource-memory-usage-percentage=5')
    chrome_options.add_argument('--aggressive-cache-discard')
    chrome_options.add_argument('--disable-background-timer-throttling')
    
    # Unique profile and debugging port for each script instance
    # CRITICAL: timestamp + random ensures no collision even if scripts start simultaneously
    import tempfile
    profile_timestamp = int(time.time() * 1000)  # milliseconds for higher precision
    temp_base = tempfile.gettempdir()  # Cross-platform temp directory
    profile_dir = os.path.join(temp_base, f'chrome_profile_script_{SCRIPT_ID}_{profile_timestamp}_{instance_random}')
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument(f'--remote-debugging-port={9222 + SCRIPT_ID}')
    
    # Disk cache isolation - each script gets its own cache
    disk_cache_dir = os.path.join(temp_base, f'chrome_cache_script_{SCRIPT_ID}_{profile_timestamp}')
    chrome_options.add_argument(f'--disk-cache-dir={disk_cache_dir}')
    chrome_options.add_argument('--disk-cache-size=104857600')  # 100MB
    
    # Additional isolation options
    chrome_options.add_argument(f'--crash-dumps-dir={os.path.join(temp_base, f"chrome_crashes_script_{SCRIPT_ID}_{profile_timestamp}")}')
    chrome_options.add_argument('--enable-crash-reporter=false')
    chrome_options.add_argument('--disable-crash-reporter')
    
    # Process per site to prevent tab/window sharing
    chrome_options.add_argument('--process-per-site')
    chrome_options.add_argument('--disable-site-isolation-trials')
    
    # Automation detection prevention
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('prefs', {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': False,
        'profile.managed_default_content_settings.images': 1
    })
    
    # Set custom user agent to avoid detection
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Create new Chrome instance with enhanced isolation and retry logic
    max_init_attempts = 5
    
    for attempt in range(max_init_attempts):
        try:
            logger.info(f"Attempting to create Chrome instance (attempt {attempt + 1}/{max_init_attempts}) for Script {SCRIPT_ID}")
            logger.info(f"Profile directory: {profile_dir}")
            logger.info(f"Debugging port: {9222 + SCRIPT_ID}")
            
            # Add random delay to prevent simultaneous starts
            if attempt == 0:
                startup_delay = random.uniform(0.5, 3.0) * SCRIPT_ID * 0.1
                logger.info(f"Adding startup delay: {startup_delay:.2f} seconds")
                time.sleep(startup_delay)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Verify driver is working
            driver.get("data:text/html,<html><body><h1>Browser Initialized - Script {SCRIPT_ID}</h1></body></html>")
            
            # Set timeouts
            driver.set_page_load_timeout(60)
            driver.set_script_timeout(60)
            
            # Additional post-initialization isolation
            try:
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                logger.debug(f"Applied stealth settings for Script {SCRIPT_ID}")
            except Exception as stealth_error:
                logger.warning(f"Could not apply stealth settings: {stealth_error}")
            
            logger.info(f"Chrome instance created successfully for Script {SCRIPT_ID}")
            break
            
        except Exception as init_error:
            logger.warning(f"Chrome initialization attempt {attempt + 1} failed: {init_error}")
            
            # Cleanup failed attempt
            try:
                if 'driver' in locals():
                    driver.quit()
            except Exception:
                pass
                
            if attempt < max_init_attempts - 1:
                retry_delay = 5 + (attempt * 3) + random.uniform(0, 2)
                logger.info(f"Waiting {retry_delay:.2f} seconds before retry...")
                time.sleep(retry_delay)
                
                # Try cleanup before retry
                force_cleanup_chrome_processes()
            else:
                logger.error(f"Failed to initialize Chrome after {max_init_attempts} attempts")
                raise init_error
       
    try:
        # Navigate to the webpage
        url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        logger.info("Page loaded successfully.")
        
        # Capture screenshot of the captcha
        captcha_img = wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        captcha_img.screenshot(f"captcha_script_{SCRIPT_ID}.png")
        # save this image in the same directory as the script
        logger.info(f"Captcha image saved as captcha_script_{SCRIPT_ID}.png")
        # driver.save_screenshot(f"initial_page_script_{SCRIPT_ID}.png")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    
       
def check_captcha_error():
    """Check if captcha error modal is present"""
    try:
        error_modal = driver.find_elements(By.ID, "validateError")
        if error_modal and error_modal[0].is_displayed():
            logger.warning("Captcha validation error detected!")
            return True
        return False
    except Exception as e:
        logger.debug(f"Error checking for captcha modal: {e}")
        return False


def close_captcha_error_modal():
    """Close the captcha error modal if it exists"""
    try:
        error_modal = driver.find_elements(By.ID, "validateError")
        if error_modal and error_modal[0].is_displayed():
            # Try to find and click close button
            close_button = error_modal[0].find_element(By.CSS_SELECTOR, "button.btn-close")
            close_button.click()
            logger.info("Captcha error modal closed")
            time.sleep(1)
            return True
    except Exception as e:
        logger.debug(f"Error closing captcha modal: {e}")
        try:
            # Try JavaScript approach as fallback
            driver.execute_script("document.getElementById('validateError').style.display = 'none';")
            logger.info("Captcha error modal closed using JavaScript")
            return True
        except:
            pass
    return False


def fill_captcha():
    global driver
    if driver is None:
        logger.error("Driver not initialized.")
        return False
    
    if vision_client is None:
        logger.error("Google Cloud Vision API client is not initialized.")
        return False

    attempt = 0
    max_attempts = 15
    while attempt < max_attempts:
        attempt += 1
        try:
            logger.info(f"Attempting to solve captcha (attempt {attempt}/{max_attempts})...")
            
            # Ensure we have a fresh captcha image
            try:
                captcha_img = wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                captcha_img.screenshot(f"captcha_script_{SCRIPT_ID}.png")
                logger.info("Captcha image captured")
            except Exception as img_error:
                logger.error(f"Failed to capture captcha image: {img_error}")
                driver.refresh()
                time.sleep(3)
                continue
            
            # Use Google Cloud Vision API to solve captcha
            with open(f"captcha_script_{SCRIPT_ID}.png", "rb") as image_file:
                image_content = image_file.read()
            
            # Create image object for Vision API
            image = vision_v1.Image(content=image_content)
            
            # Set up image context for better OCR results
            ctx = vision_v1.ImageContext(language_hints=["en"])
            
            # Perform text detection
            response = vision_client.text_detection(image=image, image_context=ctx)
            
            # Check for errors
            if response.error.message:
                logger.error(f"Vision API error: {response.error.message}")
                driver.refresh()
                time.sleep(3)
                continue
            
            # Extract text from response
            if response.text_annotations:
                # First annotation contains the full detected text
                result = response.text_annotations[0].description.strip()
                # Remove any newlines or spaces
                result = result.replace('\n', '').replace(' ', '')
                logger.info(f"Vision API Prediction: {result}")
            else:
                logger.warning("No text detected in captcha image")
                driver.refresh()
                time.sleep(3)
                continue
            
            # Fill the captcha input field
            logger.info("Filling captcha input field...")
            captcha_input = driver.find_element(By.ID, "captcha")
            captcha_input.clear()
            captcha_input.send_keys(result)
            
            # Submit the captcha
            submit_button = wait.until(EC.presence_of_element_located((By.ID, "main_search")))
            logger.info("Submitting the captcha...")
            submit_button.click()
            
            # Wait a moment for potential error modal
            time.sleep(2)
            
            # Check if captcha error occurred
            if check_captcha_error():
                logger.warning(f"Captcha validation failed on attempt {attempt}")
                close_captcha_error_modal()
                
                logger.info("Refreshing page and retrying captcha...")
                driver.refresh()
                time.sleep(3)
                # Wait for page to reload
                wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                continue
            else:
                # Captcha seems to be successful
                logger.info("Captcha submitted successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to solve captcha on attempt {attempt}: {str(e)}")
            logger.info("Refreshing page and retrying...")
            driver.refresh()
            time.sleep(3)
            try:
                wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
            except:
                pass
            continue
    

def wait_for_loading_component():
    try:
        # First, wait a moment for the loading to potentially start
        time.sleep(1)
        
        # Check if loading modal appears and wait for it to disappear
        try:
            # Wait for loading modal to appear first (with shorter timeout)
            logger.info("Waiting for loading modal to appear...")
            wait.until(EC.visibility_of_element_located((By.ID, "loadMe")))
            logger.info("Loading modal appeared, waiting for it to disappear...")
            
            # Then wait for it to disappear
            wait.until(EC.invisibility_of_element_located((By.ID, "loadMe")))
            logger.info("Loading modal disappeared.")
            
        except Exception as e:
            logger.info(f"Loading modal might not have appeared or was too quick: {e}")
            # Continue anyway as the page might have loaded quickly
        
        # Additional wait to ensure page is fully loaded
        wait.until(EC.presence_of_element_located((By.ID, "div_container")))
        logger.info("Page processing completed.")
        time.sleep(2)
        
    except Exception as e:
        logger.error(f"Error waiting for loading component: {e}")
    
    driver.save_screenshot(f"after_loading_script_{SCRIPT_ID}.png")


def set_table_display_count():
    """Set the table to display 100 entries instead of default 10"""
    try:
        logger.info("Setting table display count to 100...")
        
        # Find the dropdown select element
        select_element = wait.until(EC.presence_of_element_located((By.NAME, "example_pdf_length")))
        
        # Click on the select element to open dropdown
        select_element.click()
        time.sleep(1)
        
        # Find and click the option with value "100"
        option_100 = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='example_pdf_length']/option[@value='100']")))
        option_100.click()
        
        logger.info("Successfully set table display count to 100")
        
        # Wait for the table to reload with new data
        time.sleep(3)
        
    except Exception as e:
        logger.error(f"Error setting table display count: {e}")


def extract_table_data():
    """Extract all judgment data from the table"""
    try:
        logger.info("Extracting table data...")
        
        # Wait for table body to be present
        table_body = wait.until(EC.presence_of_element_located((By.ID, "report_body")))
        
        # Get all rows in the table body
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        
        judgments_data = []
        
        for i, row in enumerate(rows):
            try:
                # Get the button element with case information
                button_element = row.find_element(By.CSS_SELECTOR, "button.btn-link")
                
                # Extract case title from button text
                case_title = button_element.find_element(By.TAG_NAME, "font").text.strip()
                
                # Extract judge information
                judge_element = row.find_element(By.XPATH, ".//strong[contains(text(), 'Judge :')]")
                judge = judge_element.text.replace("Judge :", "").strip()
                
                # Extract CNR and other case details
                case_details_element = row.find_element(By.CLASS_NAME, "caseDetailsTD")
                case_details_text = case_details_element.text
                
                # Parse CNR number
                cnr_start = case_details_text.find("CNR :") + 6
                cnr_end = case_details_text.find("|", cnr_start)
                cnr = case_details_text[cnr_start:cnr_end].strip() if cnr_end != -1 else ""
                
                # Parse Decision Date
                decision_date = ""
                decision_year = None
                try:
                    decision_start = case_details_text.find("Decision Date :") + 16
                    decision_end = case_details_text.find("|", decision_start)
                    if decision_end == -1:
                        decision_end = case_details_text.find("Disposal Nature", decision_start)
                    
                    if decision_start > 15 and decision_end > decision_start:
                        decision_date = case_details_text[decision_start:decision_end].strip()
                        # Extract year from decision date (format: DD-MM-YYYY)
                        if len(decision_date) >= 4 and decision_date[-4:].isdigit():
                            decision_year = int(decision_date[-4:])
                except Exception as date_error:
                    logger.debug(f"Error parsing decision date: {date_error}")
                
                # Get the onclick attribute to extract PDF path
                onclick_attr = button_element.get_attribute("onclick")
                pdf_path = ""
                if "open_pdf" in onclick_attr:
                    # Extract PDF path from onclick function
                    start_idx = onclick_attr.find("'court/")
                    end_idx = onclick_attr.find("'", start_idx + 1)
                    if start_idx != -1 and end_idx != -1:
                        pdf_path = onclick_attr[start_idx+1:end_idx]
                
                # Create filename with CNR number
                base_filename = sanitize_filename(case_title)
                if cnr:
                    filename = f"{base_filename}_CNR_{sanitize_filename(cnr)}.pdf"
                else:
                    filename = f"{base_filename}.pdf"
                
                judgment_data = {
                    "row_number": i + 1,
                    "case_title": case_title,
                    "judge": judge,
                    "cnr": cnr,
                    "pdf_path": pdf_path,
                    "button_id": button_element.get_attribute("id"),
                    "filename": filename,
                    "decision_date": decision_date,
                    "decision_year": decision_year
                }
                
                judgments_data.append(judgment_data)
                logger.info(f"Extracted data for row {i+1}: {case_title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error extracting data from row {i+1}: {e}")
                continue
        
        logger.info(f"Successfully extracted data for {len(judgments_data)} judgments")
        return judgments_data
        
    except Exception as e:
        logger.error(f"Error extracting table data: {e}")
        return []


def download_pdf(judgment_data):
    """Download PDF for a specific judgment"""
    download_start_time = time.time()
    
    try:
        logger.info(f"Downloading PDF for: {judgment_data['case_title'][:50]}...")
        
        # First, ensure any existing modal is closed
        close_any_open_modal()
        
        # Wait a moment for any modal to fully close
        time.sleep(1)
        
        # Find and click the judgment link with retry logic
        button_element = driver.find_element(By.ID, judgment_data["button_id"])
        
        # Try regular click first
        try:
            # Scroll to element to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_element)
            time.sleep(0.5)
            
            # Wait for element to be clickable
            wait.until(EC.element_to_be_clickable((By.ID, judgment_data["button_id"])))
            button_element.click()
            
        except Exception as click_error:
            logger.warning(f"Regular click failed, trying JavaScript click: {click_error}")
            # Fallback to JavaScript click
            driver.execute_script("arguments[0].click();", button_element)
        
        # Wait for modal to appear
        modal = wait.until(EC.visibility_of_element_located((By.ID, "viewFiles")))
        logger.info("Modal appeared, waiting for PDF to load...")
        
        # Wait for PDF object to load
        time.sleep(3)
        
        # New approach: Look for object/embed tags with multiple selectors
        pdf_downloaded_success = False
        response = None
        
        try:
            pdf_selectors = [
                "object[data*='.pdf']",
                "object[type='application/pdf']", 
                "embed[src*='.pdf']",
                "embed[type='application/pdf']",
                "#viewFiles-body object",
                "#viewFiles-body embed",
                "object",
                "embed"
            ]
            
            for selector in pdf_selectors:
                try:
                    pdf_objects = driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Found {len(pdf_objects)} objects with selector: {selector}")
                    
                    for obj in pdf_objects:
                        if obj.is_displayed():
                            # Check both 'data' and 'src' attributes
                            pdf_url = obj.get_attribute("data") or obj.get_attribute("src")
                            
                            if not pdf_url:
                                logger.warning(f"No URL found for displayed object with selector: {selector}")
                                continue
                            
                            logger.info(f"Object URL: {pdf_url}")
                            
                            if pdf_url and (".pdf" in pdf_url.lower() or "pdfsearch/tmp/" in pdf_url.lower()):
                                # Get cookies and headers
                                cookies = driver.get_cookies()
                                session = requests.Session()
                                for cookie in cookies:
                                    session.cookies.set(cookie['name'], cookie['value'])
                                
                                headers = {
                                    'User-Agent': driver.execute_script("return navigator.userAgent;"),
                                    'Referer': driver.current_url
                                }
                                
                                try:
                                    # Construct full URL if needed
                                    if pdf_url.startswith('/'):
                                        base_url = "https://services.ecourts.gov.in"
                                        pdf_url = base_url + pdf_url
                                    elif not pdf_url.startswith('http'):
                                        # Handle relative URLs
                                        base_url = "https://services.ecourts.gov.in"
                                        pdf_url = base_url + "/" + pdf_url
                                    
                                    logger.info(f"Attempting to download from: {pdf_url}")
                                    response = session.get(pdf_url, timeout=30, headers=headers)
                                    
                                    if response.status_code == 200:
                                        # Check if response is actually a PDF
                                        content_type = response.headers.get('content-type', '').lower()
                                        is_pdf_content = content_type.startswith('application/pdf')
                                        has_pdf_signature = response.content[:4] == b'%PDF'
                                        
                                        if is_pdf_content or has_pdf_signature:
                                            logger.info(f"Successfully fetched PDF content ({len(response.content)} bytes)")
                                            pdf_downloaded_success = True
                                            break
                                        else:
                                            logger.error(f" Invalid PDF content - Content-Type: {content_type}, Size: {len(response.content)} bytes")
                                            logger.error(f" URL: {pdf_url}")
                                            if len(response.content) < 1000:
                                                logger.error(f" Response preview: {response.text[:500]}")
                                    else:
                                        logger.error(f" HTTP {response.status_code} for URL: {pdf_url}")
                                        logger.error(f" Response headers: {dict(response.headers)}")
                                        
                                except Exception as obj_download_error:
                                    logger.error(f"Error downloading from object: {str(obj_download_error)}")
                                    continue
                    
                    if pdf_downloaded_success:
                        break
                except Exception as selector_error:
                    logger.debug(f"Selector {selector} failed: {str(selector_error)}")
                    continue
            
            if not pdf_downloaded_success:
                logger.error(f" FAILED: Could not download PDF using any selector")
                logger.error(f" Tried {len(pdf_selectors)} different selectors")
                logger.error(f" Case: {judgment_data.get('case_title', 'Unknown')[:100]}")
                raise Exception("Could not download PDF using any selector")
                
        except Exception as e:
            logger.error(f" Error in PDF download approach: {e}")
            logger.error(f" Case: {judgment_data.get('case_title', 'Unknown')[:100]}")
            raise
        
        if response and response.status_code == 200:
            # Use the sanitized case title as filename
            safe_filename = judgment_data['filename']
            
            # Save the PDF locally first
            with open(safe_filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded: {safe_filename}")
            
            # Upload to S3
            s3_key = f"judgements-test-final/{safe_filename}"
            upload_success = upload_to_s3(safe_filename, s3_key)
            
            # Delete local file after successful upload
            if upload_success:
                delete_local_file(safe_filename)
            else:
                logger.warning(f"Failed to upload to S3, keeping local file: {safe_filename}")
            
            # Calculate download time
            download_end_time = time.time()
            download_duration = download_end_time - download_start_time
            
            # Close the modal
            if not close_any_open_modal():
                logger.warning("Failed to close modal properly")
            
            # Additional wait to ensure modal is fully closed
            time.sleep(1)
            
            # Return success info for tracking
            return {
                "success": True,
                "filename": safe_filename,
                "s3_key": s3_key if upload_success else None,
                "uploaded_to_s3": upload_success,
                "cnr": judgment_data['cnr'],
                "case_title": judgment_data['case_title'],
                "decision_date": judgment_data.get('decision_date', ''),
                "decision_year": judgment_data.get('decision_year'),
                "download_time": datetime.now().isoformat(),
                "download_duration_seconds": round(download_duration, 2)
            }
        else:
            logger.error(f" DOWNLOAD FAILED for: {judgment_data['case_title'][:50]}")
            logger.error(f" Status code: {response.status_code if response else 'No response'}")
            logger.error(f" CNR: {judgment_data.get('cnr', 'N/A')}")
            if response:
                logger.error(f" Response size: {len(response.content)} bytes")
                logger.error(f" Content-Type: {response.headers.get('content-type', 'Unknown')}")
            download_end_time = time.time()
            download_duration = download_end_time - download_start_time
            
            # Close the modal
            close_any_open_modal()
            time.sleep(1)
            
            return {
                "success": False,
                "error": f"HTTP {response.status_code}" if response else "No response",
                "case_title": judgment_data['case_title'],
                "download_duration_seconds": round(download_duration, 2)
            }
        
    except Exception as e:
        logger.error(f" EXCEPTION during PDF download")
        logger.error(f" Case: {judgment_data['case_title'][:50]}")
        logger.error(f" CNR: {judgment_data.get('cnr', 'N/A')}")
        logger.error(f" Error: {str(e)}")
        logger.error(f" Error type: {type(e).__name__}")
        
        # Try to close modal if it's still open
        close_any_open_modal()
        
        download_end_time = time.time()
        download_duration = download_end_time - download_start_time
        
        return {
            "success": False,
            "error": str(e),
            "case_title": judgment_data['case_title'],
            "download_duration_seconds": round(download_duration, 2)
        }


def download_pdfs_in_batches(judgments_data, start_index=0):
    """Download PDFs in batches of 25"""
    global total_files_downloaded
    
    total_judgments = len(judgments_data)
    end_index = min(start_index + 25, total_judgments)
    
    logger.info(f"Starting batch download: files {start_index+1} to {end_index} of {total_judgments}")
    
    for i in range(start_index, end_index):
        judgment = judgments_data[i]
        logger.info(f"Processing {i+1}/{total_judgments}: {judgment['case_title'][:50]}...")
        download_pdf(judgment)
        total_files_downloaded += 1
        
        # Log progress
        elapsed_time = time.time() - start_time
        logger.info(f"Progress: {total_files_downloaded} files downloaded in {elapsed_time:.2f} seconds")
        
        # Add delay between downloads
        time.sleep(2)
    
    logger.info(f"Completed batch: downloaded files {start_index+1} to {end_index}")
    return end_index


def check_if_next_page_available():
    """Check if next page button is available and not disabled"""
    try:
        next_button = driver.find_element(By.ID, "example_pdf_next")
        classes = next_button.get_attribute("class")
        return "disabled" not in classes
    except Exception as e:
        logger.error(f"Error checking next page availability: {e}")
        return False


def navigate_to_next_page():
    """Navigate to the next page"""
    global current_page
    
    try:
        if not check_if_next_page_available():
            logger.info("No more pages available")
            return False
        
        logger.info(f"Navigating to page {current_page + 1}...")
        
        next_button = wait.until(EC.element_to_be_clickable((By.ID, "example_pdf_next")))
        driver.execute_script("arguments[0].click();", next_button)
        
        # Wait for page to load
        time.sleep(3)
        
        # Wait for table to reload
        wait.until(EC.presence_of_element_located((By.ID, "report_body")))
        
        current_page += 1
        logger.info(f"Successfully navigated to page {current_page}")
        return True
        
    except Exception as e:
        logger.error(f"Error navigating to next page: {e}")
        return False


def recover_browser_session():
    """Recover from browser crashes by completely reinitializing everything"""
    global driver, wait
    
    try:
        logger.warning(f"Browser session crashed or became unresponsive for Script {{SCRIPT_ID}}. Attempting recovery...")
        
        # Force cleanup any hanging processes
        force_cleanup_chrome_processes()
        
        # Set driver to None to ensure clean state
        driver = None
        wait = None
        
        # Wait before reinitialization to allow system cleanup
        logger.info("Waiting for system cleanup before recovery...")
        time.sleep(10)
        
        # Reinitialize browser completely
        logger.info("Reinitializing browser with new profile...")
        initialize_browser()
        
        # Navigate to the main URL with retries
        url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to {{url}} (attempt {{attempt + 1}}/{{max_retries}})")
                driver.get(url)
                
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                logger.info("Page loaded successfully after recovery")
                break
                
            except Exception as nav_error:
                logger.warning(f"Navigation attempt {{attempt + 1}} failed: {{nav_error}}")
                if attempt == max_retries - 1:
                    raise nav_error
                time.sleep(5)
        
        # Solve captcha with retry logic
        captcha_attempts = 0
        max_captcha_attempts = 50
        
        while captcha_attempts < max_captcha_attempts:
            try:
                if fill_captcha():
                    logger.info("Captcha solved successfully during recovery")
                    break
                else:
                    captcha_attempts += 1
                    logger.warning(f"Captcha attempt {{captcha_attempts}} failed during recovery")
                    if captcha_attempts < max_captcha_attempts:
                        time.sleep(3)
            except Exception as captcha_error:
                captcha_attempts += 1
                logger.warning(f"Captcha error during recovery: {{captcha_error}}")
                if captcha_attempts < max_captcha_attempts:
                    time.sleep(3)
        
        if captcha_attempts >= max_captcha_attempts:
            logger.error("Failed to solve captcha during recovery after multiple attempts")
            return False
        
        # Wait for loading to complete
        wait_for_loading_component()
        
        # Set table display count to 100
        set_table_display_count()
        
        logger.info(f"Browser session recovered successfully for Script {{SCRIPT_ID}}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to recover browser session for Script {{SCRIPT_ID}}: {{e}}")
        # Final cleanup attempt
        try:
            force_cleanup_chrome_processes()
        except Exception:
            pass
        return False


def reinitialize_session():
    """Reinitialize the browser session by going back to the main URL"""
    global driver, wait
    
    try:
        logger.info("Reinitializing session...")
        
        # Check if driver is still valid, if not, recreate it
        driver_valid = False
        if driver is not None:
            try:
                driver.current_url
                driver_valid = True
            except Exception as e:
                logger.warning(f"Driver is not responsive: {e}. Will recreate.")
                try:
                    driver.quit()
                except:
                    pass
                driver = None
        
        # If driver is invalid, reinitialize completely
        if not driver_valid:
            logger.info("Recreating browser instance...")
            initialize_browser()
            if not fill_captcha():
                logger.error("Failed to solve captcha after browser recreation")
                return False
            wait_for_loading_component()
            set_table_display_count()
            logger.info("Browser recreated and initialized successfully")
            return True
        
        logger.info("Going back to main URL...")
        
        # Navigate back to the main URL
        url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
        driver.get(url)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        logger.info("Main page loaded successfully")
        
        # Solve captcha again with retry logic
        if not fill_captcha():
            logger.error("Failed to solve captcha during session reinitialization")
            return False
        
        # Wait for loading to complete
        wait_for_loading_component()
        
        # Set table display count to 100
        set_table_display_count()
        
        logger.info("Session reinitialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error reinitializing session: {e}")
        return False


def process_all_pages():
    """Process all pages with batch downloading"""
    global current_page, total_files_downloaded, start_time
    
    # Load distributed configuration
    load_distributed_config()
    
    # Load existing progress and timing data
    progress = load_progress()
    timing_data = load_timing_data()
    
    # Determine starting page for this instance
    if START_PAGE and END_PAGE:
        # Use distributed configuration
        if progress.get("current_page", 1) < START_PAGE:
            current_page = START_PAGE
            logger.info(f"Script {SCRIPT_ID}: Starting from configured page {START_PAGE}")
        else:
            current_page = progress.get("current_page", START_PAGE)
            logger.info(f"Script {SCRIPT_ID}: Resuming from page {current_page}")
        
        max_page = END_PAGE
        logger.info(f"Script {SCRIPT_ID} will process pages {START_PAGE} to {END_PAGE}")
    else:
        # No distributed config, process normally
        current_page = progress.get("current_page", 1)
        max_page = None
        logger.info("No distributed configuration found, processing all pages")
    
    total_files_downloaded = progress.get("total_files_downloaded", 0)
    
    # Ensure all required keys exist in progress
    if 'downloaded_files' not in progress:
        progress['downloaded_files'] = []
    if 'failed_downloads' not in progress:
        progress['failed_downloads'] = []
    if 'pages_completed' not in progress:
        progress['pages_completed'] = []
    if 'yearly_counts' not in progress:
        progress['yearly_counts'] = {}
    
    if progress.get("start_time"):
        start_time = datetime.fromisoformat(progress["start_time"]).timestamp()
        logger.info(f"Resuming from previous session. Current page: {current_page}, Files downloaded: {total_files_downloaded}")
    else:
        start_time = time.time()
        progress["start_time"] = datetime.now().isoformat()
        timing_data["session_start"] = datetime.now().isoformat()
        timing_data["script_id"] = SCRIPT_ID
        logger.info("Starting new comprehensive PDF download process...")
    
    save_progress(progress)
    save_timing_data(timing_data)
    
    # If starting from a page other than 1, navigate to it with multiple attempts
    if current_page > 1:
        logger.info(f"Navigating to starting page {current_page}...")
        navigation_success = False
        
        for nav_attempt in range(3):
            if navigate_to_specific_page(current_page, max_retries=2):
                navigation_success = True
                break
            else:
                logger.warning(f"Navigation attempt {nav_attempt + 1} failed")
                if nav_attempt < 2:
                    logger.info("Attempting full browser recovery before next navigation attempt...")
                    if not recover_browser_session():
                        logger.error("Browser recovery failed")
                        continue
                    time.sleep(10)  # Additional wait after recovery
        
        if not navigation_success:
            logger.error(f"Failed to navigate to starting page {current_page} after multiple attempts")
            send_error_notification(
                f"Failed to navigate to starting page {current_page}",
                "Navigation failed after multiple recovery attempts. Script may need manual intervention."
            )
            return
    
    while True:
        try:
            # Check if we've reached the max page for this instance
            if max_page and current_page > max_page:
                logger.info(f"Script {SCRIPT_ID} has reached its maximum page ({max_page}). Stopping.")
                break
            
            logger.info(f"\n=== Processing Page {current_page} ===")
            if max_page:
                logger.info(f"Progress: Page {current_page} of {max_page} (Script {SCRIPT_ID})")
            
            # Extract table data for current page
            judgments_data = extract_table_data()
            
            if not judgments_data:
                logger.warning(f"No judgment data found on page {current_page}")
                break
            
            logger.info(f"Found {len(judgments_data)} judgments on page {current_page}")
            
            # Process in batches of 25
            files_processed_on_page = 0
            
            while files_processed_on_page < len(judgments_data):
                batch_start = files_processed_on_page
                batch_end = min(files_processed_on_page + 25, len(judgments_data))
                
                logger.info(f"\n--- Processing batch {batch_start+1}-{batch_end} on page {current_page} (Total on page: {len(judgments_data)}) ---")
                
                # Ensure clean state before starting batch
                close_any_open_modal()
                time.sleep(1)
                
                # Download current batch
                for i in range(batch_start, batch_end):
                    judgment = judgments_data[i]
                    logger.info(f"Processing file {i+1}/{len(judgments_data)} on page {current_page}: {judgment['case_title'][:50]}...")
                    
                    # Check if file already downloaded
                    if judgment['filename'] in [f.get('filename', '') for f in progress.get('downloaded_files', [])]:
                        logger.info(f"File already downloaded, skipping: {judgment['filename']}")
                        continue
                    
                    # Retry mechanism for downloads
                    max_retries = 2
                    download_result = None
                    
                    for retry in range(max_retries):
                        try:
                            download_result = download_pdf(judgment)
                            if download_result and download_result.get('success'):
                                break
                            else:
                                logger.warning(f"Download failed, retry {retry + 1}/{max_retries}")
                                time.sleep(2)
                        except Exception as retry_error:
                            logger.error(f"Download attempt {retry + 1} failed: {retry_error}")
                            if retry < max_retries - 1:
                                time.sleep(3)
                            else:
                                download_result = {
                                    "success": False,
                                    "error": f"Failed after {max_retries} retries: {str(retry_error)}",
                                    "case_title": judgment['case_title']
                                }
                    
                    if download_result and download_result.get('success'):
                        total_files_downloaded += 1
                        progress['downloaded_files'].append(download_result)
                        progress['total_files_downloaded'] = total_files_downloaded
                        progress['current_page'] = current_page
                        
                        # Update yearly counts
                        decision_year = download_result.get('decision_year')
                        if decision_year:
                            if 'yearly_counts' not in progress:
                                progress['yearly_counts'] = {}
                            year_str = str(decision_year)
                            progress['yearly_counts'][year_str] = progress['yearly_counts'].get(year_str, 0) + 1
                        
                        # Update timing statistics
                        download_duration = download_result.get('download_duration_seconds', 0)
                        timing_data = update_timing_stats(timing_data, judgment, download_duration, success=True)
                        
                        # Save progress and timing after each successful download
                        save_progress(progress)
                        save_timing_data(timing_data)
                    else:
                        # Log failed download
                        logger.error(f"Failed to download: {judgment['case_title'][:50]}")
                        failed_download = download_result or {
                            "success": False,
                            "error": "Unknown error",
                            "case_title": judgment['case_title'],
                            "download_duration_seconds": 0
                        }
                        if 'failed_downloads' not in progress:
                            progress['failed_downloads'] = []
                        progress['failed_downloads'].append(failed_download)
                        
                        # Update timing statistics for failed download
                        download_duration = failed_download.get('download_duration_seconds', 0)
                        timing_data = update_timing_stats(timing_data, judgment, download_duration, success=False)
                        
                        save_progress(progress)
                        save_timing_data(timing_data)
                    
                    # Log progress with timing
                    elapsed_time = time.time() - start_time
                    avg_time_per_file = elapsed_time / total_files_downloaded if total_files_downloaded > 0 else 0
                    logger.info(f"Progress: {total_files_downloaded} files downloaded | Elapsed: {elapsed_time:.2f}s | Avg: {avg_time_per_file:.2f}s/file")
                    
                    time.sleep(1)
                
                files_processed_on_page = batch_end
                logger.info(f"Batch complete. Processed {files_processed_on_page}/{len(judgments_data)} files on page {current_page}")
                
                # If we've processed a full batch of 25 and there are more files on this page
                if (batch_end - batch_start) == 25 and files_processed_on_page < len(judgments_data):
                    logger.info(f"Completed batch of 25 files. Reinitializing session before next batch...")
                    
                    if not reinitialize_session():
                        logger.error("Failed to reinitialize session. Stopping process.")
                        return
                    
                    # Navigate back to current page
                    if not navigate_to_specific_page(current_page):
                        logger.error(f"Failed to navigate back to page {current_page} after reinitialization")
                        return
                    
                    # Re-extract table data after reinitialization
                    judgments_data = extract_table_data()
                    if not judgments_data:
                        logger.error("Failed to re-extract table data after reinitialization")
                        return
                    
                    logger.info(f"Successfully re-extracted {len(judgments_data)} judgments on page {current_page}")
                else:
                    logger.info(f"No reinitialization needed. Continuing to next page.")
            
            logger.info(f"Completed page {current_page}. Total files downloaded so far: {total_files_downloaded}")
            
            # Mark page as completed
            if current_page not in progress.get('pages_completed', []):
                progress['pages_completed'].append(current_page)
                save_progress(progress)
            
            # Try to navigate to next page
            if not navigate_to_next_page():
                logger.info("No more pages to process. Download complete!")
                break
                
        except Exception as e:
            logger.error(f"Error processing page {current_page}: {e}")
            
            # Send error notification
            error_details = traceback.format_exc()
            send_error_notification(
                f"Error processing page {current_page}: {str(e)}",
                error_details
            )
            
            # Try multiple recovery attempts
            recovery_success = False
            
            for recovery_attempt in range(3):
                logger.info(f"Recovery attempt {recovery_attempt + 1}/3...")
                
                if recovery_attempt == 0:
                    # First try simple session reinitialization
                    if reinitialize_session():
                        recovery_success = True
                        break
                else:
                    # For subsequent attempts, try full browser recovery
                    if recover_browser_session():
                        # After recovery, navigate back to current page
                        if navigate_to_specific_page(current_page, max_retries=2):
                            recovery_success = True
                            break
                        else:
                            logger.warning(f"Recovery attempt {recovery_attempt + 1}: Navigation failed after browser recovery")
                
                if recovery_attempt < 2:
                    logger.info(f"Recovery attempt {recovery_attempt + 1} failed, waiting before next attempt...")
                    time.sleep(30)  # Wait before next recovery attempt
            
            if recovery_success:
                logger.info("Successfully recovered from error. Continuing...")
                continue
            else:
                logger.error("Failed to recover from error after multiple attempts. Stopping process.")
                send_shutdown_notification("Failed to recover from error after multiple attempts")
                break
    
    # Final summary
    total_time = time.time() - start_time
    avg_time_per_file = total_time / total_files_downloaded if total_files_downloaded > 0 else 0
    
    # Final progress and timing updates
    progress['total_files_downloaded'] = total_files_downloaded
    progress['current_page'] = current_page
    progress['completion_time'] = datetime.now().isoformat()
    
    # Final timing statistics
    timing_data['session_end'] = datetime.now().isoformat()
    timing_data['total_time_seconds'] = round(total_time, 2)
    
    # Add session summary
    session_summary = {
        "script_id": SCRIPT_ID,
        "session_start": timing_data.get('session_start'),
        "session_end": timing_data['session_end'],
        "total_files_processed": timing_data['total_files_processed'],
        "successful_downloads": timing_data['total_successful_downloads'],
        "failed_downloads": timing_data['total_failed_downloads'],
        "session_duration_seconds": round(total_time, 2),
        "session_duration_minutes": round(total_time / 60, 2),
        "average_time_per_file": timing_data['average_time_per_file'],
        "pages_processed": current_page,
        "start_page": START_PAGE,
        "end_page": END_PAGE
    }
    
    if 'session_statistics' not in timing_data:
        timing_data['session_statistics'] = []
    timing_data['session_statistics'].append(session_summary)
    
    save_progress(progress)
    save_timing_data(timing_data)
    
    logger.info(f"\n=== DOWNLOAD COMPLETE ===")
    logger.info(f"Script ID: {SCRIPT_ID}")
    if START_PAGE and END_PAGE:
        logger.info(f"Assigned Range: Pages {START_PAGE} to {END_PAGE}")
    logger.info(f"Total files downloaded: {total_files_downloaded}")
    logger.info(f"Total pages processed: {current_page}")
    logger.info(f"Pages completed: {len(progress.get('pages_completed', []))}")
    failed_count = len(progress.get('failed_downloads', []))
    logger.info(f"Failed downloads: {failed_count}")
    logger.info(f"Success rate: {(total_files_downloaded / (total_files_downloaded + failed_count) * 100):.1f}%" if (total_files_downloaded + failed_count) > 0 else "N/A")
    
    # Log yearly distribution
    yearly_counts = progress.get('yearly_counts', {})
    if yearly_counts:
        logger.info(f"\n=== YEARLY DISTRIBUTION ===")
        for year in sorted(yearly_counts.keys(), reverse=True):
            logger.info(f"Year {year}: {yearly_counts[year]} files")
        logger.info(f"Total years covered: {len(yearly_counts)}")
    
    # Log timing statistics
    logger.info(f"\n=== TIMING STATISTICS ===")
    logger.info(f"Total time taken: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    logger.info(f"Average time per file: {timing_data.get('average_time_per_file', 0):.2f} seconds")
    
    if timing_data.get('fastest_download'):
        logger.info(f"Fastest download: {timing_data['fastest_download']['time']:.2f}s - {timing_data['fastest_download']['case_title']}")
    
    if timing_data.get('slowest_download'):
        logger.info(f"Slowest download: {timing_data['slowest_download']['time']:.2f}s - {timing_data['slowest_download']['case_title']}")
    
    logger.info(f"\nDownload completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Progress tracking file: {PROGRESS_FILE}")
    logger.info(f"Timing data file: {TIMING_FILE}")
    
    # Send completion notification email
    yearly_summary = "\n".join([f"Year {year}: {count} files" for year, count in sorted(yearly_counts.items(), reverse=True)]) if yearly_counts else "No data"
    
    completion_stats = {
        'total_downloaded': total_files_downloaded,
        'total_pages': current_page,
        'failed_count': failed_count,
        'success_rate': (total_files_downloaded / (total_files_downloaded + failed_count) * 100) if (total_files_downloaded + failed_count) > 0 else 0,
        'total_time_minutes': total_time / 60,
        'total_time_hours': total_time / 3600,
        'avg_time_per_file': timing_data.get('average_time_per_file', 0),
        'start_page': START_PAGE,
        'end_page': END_PAGE,
        'pages_completed': len(progress.get('pages_completed', [])),
        'yearly_summary': yearly_summary
    }
    
    send_completion_notification(completion_stats)

        
def main():
    global driver, wait
    
    try:
        logger.info("Starting browser initialization...")
        logger.info(f"Script ID: {SCRIPT_ID}")
        
        if EMAIL_ENABLED:
            logger.info("Email notifications enabled")
        else:
            logger.warning("Email notifications disabled - check .env configuration")
        
        # Initialize progress tracking
        progress = load_progress()
        logger.info(f"Loaded progress: Page {progress.get('current_page', 1)}, Files downloaded: {progress.get('total_files_downloaded', 0)}")
        
        # Step 1: Initialize browser and load page
        initialize_browser()

        # Step 2: Solve captcha with retry logic
        if not fill_captcha():
            logger.error("Failed to solve initial captcha. Exiting...")
            send_error_notification("Failed to solve initial captcha", "Captcha solving failed after multiple retries")
            driver.quit()
            return
        
        # Step 3: Wait until the loading component is invisible
        wait_for_loading_component()
        
        # Step 4: Extract total results from the page
        total_results = extract_total_results()
        if total_results:
            logger.info(f"Total results available: {total_results:,}")
        
        # Step 5: Set table display count to 100
        set_table_display_count()
        
        # Step 6: Process all pages with batch downloading
        process_all_pages()
        
        logger.info("All processing completed. Closing browser...")
        driver.quit()
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        send_shutdown_notification("Interrupted by user (Ctrl+C)")
        if driver:
            driver.quit()
        
    except Exception as e:
        logger.error(f"Fatal error in main process: {e}")
        error_details = traceback.format_exc()
        send_error_notification(f"Fatal error in main process: {str(e)}", error_details)
        if driver:
            driver.quit()
        raise


if __name__ == "__main__":
    try:
        logger.info("=" * 80)
        logger.info(f"Starting Script 55")
        logger.info(f"Page Range: 138,187 to 140,745")
        logger.info(f"Debugging Port: {9222 + SCRIPT_ID}")
        import tempfile
        logger.info(f"Profile Directory: {os.path.join(tempfile.gettempdir(), 'chrome_profile_script_' + str(SCRIPT_ID) + '_*')}")
        logger.info("=" * 80)
        
        # Step 0: Pre-launch cleanup and preparation
        logger.info("Performing pre-launch cleanup...")
        pre_launch_cleanup()
        
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
        
        # Final cleanup and summary
        logger.info("\n=== SCRIPT COMPLETION SUMMARY ===")
        logger.info(f"Total files processed: {total_files_downloaded}")
        
        cleanup_resources()
        
    except KeyboardInterrupt:
        logger.info("\\nScript interrupted by user")
        
        cleanup_resources()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Clean up resources before exit
        
        if EMAIL_ENABLED:
            send_error_notification(
                f"Script {SCRIPT_ID} - Fatal Error",
                f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
        cleanup_resources()
        sys.exit(1)
