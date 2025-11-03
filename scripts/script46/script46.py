"""
Scraping Script 46
Pages: 115,156 to 117,714
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
SCRIPT_ID = 46
START_PAGE = 115156
END_PAGE = 117714
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(SCRIPT_DIR, f"script46_progress.json")
TIMING_FILE = os.path.join(SCRIPT_DIR, f"script46_timing.json")

# Configure logging with UTF-8 encoding
log_file = os.path.join(SCRIPT_DIR, f"script46.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Script 46] - %(levelname)s - %(message)s',
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
    logger.error(f"Failed to initialize AWS clients: {str(e)}")
    bedrock_runtime = None
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
batch_size = 25

# Batch processing variables
current_batch_files = []
batch_download_dir = os.path.join(SCRIPT_DIR, f"batch_downloads_script46")

# Ensure batch download directory exists
if not os.path.exists(batch_download_dir):
    os.makedirs(batch_download_dir)
    logger.info(f"Created batch download directory: {batch_download_dir}")


def cleanup_resources():
    """Clean up browser resources for this script instance"""
    global driver
    try:
        if driver:
            logger.info(f"Cleaning up browser resources for Script {SCRIPT_ID}")
            driver.quit()
            driver = None
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")

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
    """Navigate to a specific page number with retry logic"""
    global current_page
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Navigating to page {target_page} (attempt {attempt + 1}/{max_retries})...")
            
            # Check if driver is still responsive
            try:
                driver.current_url
            except Exception as driver_error:
                logger.warning(f"Driver unresponsive during navigation: {driver_error}")
                if not recover_browser_session():
                    logger.error("Failed to recover browser session")
                    continue
            
            # Find the page input field with multiple selectors
            page_input = None
            selectors = [
                "input[aria-controls='example_pdf']",
                "input[name='example_pdf_goto_page']",
                "input.form-control[type='text']"
            ]
            
            for selector in selectors:
                try:
                    page_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if not page_input:
                logger.error("Could not find page input field")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return False
            
            # Clear and enter the target page number
            page_input.clear()
            time.sleep(0.5)
            page_input.send_keys(str(target_page))
            time.sleep(0.5)
            page_input.send_keys(Keys.RETURN)
            
            # Wait for page to load with longer timeout
            logger.info("Waiting for page navigation to complete...")
            time.sleep(5)
            
            # Wait for table to reload with extended timeout
            wait.until(EC.presence_of_element_located((By.ID, "report_body")))
            
            # Verify we're on the correct page by checking page info
            try:
                # Look for pagination info to confirm page number
                page_info_elements = driver.find_elements(By.CSS_SELECTOR, ".dataTables_info")
                if page_info_elements and str(target_page) in page_info_elements[0].text:
                    logger.info(f"Page navigation verified: {page_info_elements[0].text}")
            except Exception as verify_error:
                logger.debug(f"Could not verify page number: {verify_error}")
            
            current_page = target_page
            logger.info(f"Successfully navigated to page {current_page}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to page {target_page} (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying navigation after {5 * (attempt + 1)} seconds...")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
                
                # Try to recover session before retry if it's the last attempt before giving up
                if attempt == max_retries - 2:
                    logger.info("Attempting session recovery before final retry...")
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
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--max_old_space_size=4096')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument(f'--user-data-dir=C:/temp/chrome_profile_script_' + str(SCRIPT_ID))
    chrome_options.add_argument(f'--remote-debugging-port=' + str(9222 + SCRIPT_ID))
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Create new Chrome instance (allow multiple instances)
    driver = webdriver.Chrome(options=chrome_options)
       
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
        captcha_img.screenshot("captcha.png")
        # save this image in the same directory as the script
        logger.info("Captcha image saved as captcha.png")
        # driver.save_screenshot("initial_page.png")
    
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
    
    if bedrock_runtime is None:
        logger.error("AWS Bedrock runtime client is not initialized.")
        return False

    max_captcha_retries = 3
    
    for attempt in range(max_captcha_retries):
        try:
            logger.info(f"Attempting to solve captcha (attempt {attempt + 1}/{max_captcha_retries})...")
            
            # Ensure we have a fresh captcha image
            try:
                captcha_img = wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                captcha_img.screenshot("captcha.png")
                logger.info("Captcha image captured")
            except Exception as img_error:
                logger.error(f"Failed to capture captcha image: {img_error}")
                if attempt < max_captcha_retries - 1:
                    driver.refresh()
                    time.sleep(3)
                    continue
                else:
                    return False
            
            # calling bedrock to solve captcha
            with open("captcha.png", "rb") as image_file:
                captcha_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 30,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": captcha_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": "What text is shown in this image? Only respond with the text—no explanation."
                            }
                        ]
                    }
                ]
            }

            response = bedrock_runtime.invoke_model(
                modelId="arn:aws:bedrock:ap-south-1:491085399248:inference-profile/apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
                body=json.dumps(body)
            )

            result_json = json.loads(response['body'].read())
            result = result_json['content'][0]['text'].strip()
            logger.info(f"Claude Prediction: {result}")
            
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
                logger.warning(f"Captcha validation failed on attempt {attempt + 1}")
                close_captcha_error_modal()
                
                if attempt < max_captcha_retries - 1:
                    logger.info("Refreshing page and retrying captcha...")
                    driver.refresh()
                    time.sleep(3)
                    # Wait for page to reload
                    wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                    continue
                else:
                    logger.error("Failed to solve captcha after maximum retries")
                    return False
            else:
                # Captcha seems to be successful
                logger.info("Captcha submitted successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to solve captcha on attempt {attempt + 1}: {str(e)}")
            if attempt < max_captcha_retries - 1:
                logger.info("Refreshing page and retrying...")
                driver.refresh()
                time.sleep(3)
                try:
                    wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
                except:
                    pass
                continue
            else:
                return False
    
    return False
    

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
    
    driver.save_screenshot("after_loading.png")


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
        
        # Get the PDF URL from the object element
        pdf_object = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#viewFiles-body object")))
        pdf_url = pdf_object.get_attribute("data")
        
        if pdf_url:
            # Convert relative URL to absolute URL
            if pdf_url.startswith("/"):
                pdf_url = "https://judgments.ecourts.gov.in" + pdf_url
            
            logger.info(f"PDF URL: {pdf_url}")
            
            # Download the PDF using requests
            response = requests.get(pdf_url)
            
            if response.status_code == 200:
                # Use the sanitized case title as filename
                safe_filename = judgment_data['filename']
                
                # Save the PDF to batch download directory
                local_file_path = os.path.join(batch_download_dir, safe_filename)
                with open(local_file_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Successfully downloaded: {safe_filename}")
                
                # Add to current batch for later S3 upload
                s3_key = f"judgements/{safe_filename}"
                file_info = {
                    'filename': safe_filename,
                    'local_path': local_file_path,
                    's3_key': s3_key,
                    'judgment_data': judgment_data,
                    'download_time': datetime.now().isoformat()
                }
                
                current_batch_files.append(file_info)
                logger.info(f"Added to batch: {len(current_batch_files)}/{batch_size} files")
                
                # Calculate download time
                download_end_time = time.time()
                download_duration = download_end_time - download_start_time
                
                # Return success info for tracking
                return {
                    "success": True,
                    "filename": safe_filename,
                    "s3_key": s3_key,
                    "local_path": local_file_path,
                    "uploaded_to_s3": False,  # Will be updated after batch upload
                    "cnr": judgment_data['cnr'],
                    "case_title": judgment_data['case_title'],
                    "decision_date": judgment_data.get('decision_date', ''),
                    "decision_year": judgment_data.get('decision_year'),
                    "download_time": datetime.now().isoformat(),
                    "download_duration_seconds": round(download_duration, 2),
                    "in_batch": True
                }
                
            else:
                logger.error(f"Failed to download PDF. Status code: {response.status_code}")
                download_end_time = time.time()
                download_duration = download_end_time - download_start_time
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "case_title": judgment_data['case_title'],
                    "download_duration_seconds": round(download_duration, 2)
                }
        
        # Close the modal
        if not close_any_open_modal():
            logger.warning("Failed to close modal properly")
        
        # Additional wait to ensure modal is fully closed
        time.sleep(1)
        
    except Exception as e:
        logger.error(f"Error downloading PDF for {judgment_data['case_title'][:50]}: {e}")
        
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
    end_index = min(start_index + batch_size, total_judgments)
    
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
        next_button.click()
        
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
        logger.warning("Browser session crashed or became unresponsive. Attempting recovery...")
        
        # Force close only the current driver instance
        if driver:
            try:
                driver.quit()
                logger.info("Closed crashed browser session for this script")
            except Exception as quit_error:
                logger.warning(f"Error closing crashed browser: {quit_error}")
        
        # Wait before reinitialization
        time.sleep(5)
        
        # Reinitialize browser completely
        initialize_browser()
        
        # Navigate to the main URL
        url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        logger.info("Page loaded successfully after recovery")
        
        # Solve captcha with retry logic
        if not fill_captcha():
            logger.error("Failed to solve captcha during recovery")
            return False
        
        # Wait for loading to complete
        wait_for_loading_component()
        
        # Set table display count to 100
        set_table_display_count()
        
        logger.info("Browser session recovered successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to recover browser session: {e}")
        return False


def reinitialize_session():
    """Reinitialize the browser session by going back to the main URL"""
    global driver, wait
    
    try:
        logger.info("Reinitializing session - going back to main URL...")
        
        # Check if driver is responsive
        try:
            driver.current_url
        except Exception as driver_error:
            logger.warning(f"Driver unresponsive: {driver_error}. Attempting full recovery...")
            return recover_browser_session()
        
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
        # Try full recovery as fallback
        return recover_browser_session()


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
                batch_end = min(files_processed_on_page + batch_size, len(judgments_data))
                
                logger.info(f"\n--- Processing batch {batch_start+1}-{batch_end} on page {current_page} ---")
                
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
                        
                        # Check if batch is full and process upload
                        if len(current_batch_files) >= batch_size:
                            logger.info(f"\n📦 Batch of {batch_size} files ready for S3 upload")
                            
                            # Process batch upload
                            batch_success = process_batch_upload()
                            
                            if batch_success:
                                logger.info(f"✅ Batch upload completed successfully")
                            else:
                                logger.warning(f"⚠️  Some files in batch failed to upload")
                                send_error_notification(
                                    f"Batch upload issues on page {current_page}",
                                    "Some files in the batch failed to upload to S3. Check logs for details."
                                )
                        
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
                
                # If we've processed a full batch of 25 and there are more files on this page
                if (batch_end - batch_start) == batch_size and files_processed_on_page < len(judgments_data):
                    logger.info(f"Completed batch of {batch_size} files. Reinitializing session before next batch...")
                    
                    if not reinitialize_session():
                        logger.error("Failed to reinitialize session. Stopping process.")
                        return
                    
                    # Re-extract table data after reinitialization
                    judgments_data = extract_table_data()
                    if not judgments_data:
                        logger.error("Failed to re-extract table data after reinitialization")
                        return
            
            # Process any remaining files in the current batch at the end of the page
            if current_batch_files:
                logger.info(f"\n📦 Processing remaining {len(current_batch_files)} files in batch at end of page {current_page}")
                batch_success = process_batch_upload()
                
                if batch_success:
                    logger.info(f"✅ Final batch upload for page {current_page} completed successfully")
                else:
                    logger.warning(f"⚠️  Some files in final batch failed to upload")
            
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
    
    # Process any remaining files in the final batch
    if current_batch_files:
        logger.info(f"\n📦 Processing final batch of {len(current_batch_files)} files")
        final_batch_success = process_batch_upload()
        
        if final_batch_success:
            logger.info(f"✅ Final batch upload completed successfully")
        else:
            logger.warning(f"⚠️  Some files in final batch failed to upload")
            send_error_notification(
                "Final batch upload issues",
                f"Script {SCRIPT_ID}: Some files in the final batch failed to upload to S3. Check logs for details."
            )
    
    # Clean up batch download directory if empty
    try:
        if os.path.exists(batch_download_dir) and not os.listdir(batch_download_dir):
            os.rmdir(batch_download_dir)
            logger.info(f"Cleaned up empty batch download directory")
    except Exception as cleanup_error:
        logger.debug(f"Error cleaning up batch directory: {cleanup_error}")
    
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

def upload_batch_to_s3(batch_files):
    """Upload a batch of files to S3 and verify all uploads"""
    try:
        if not batch_files:
            logger.warning("No files in batch to upload")
            return [], []
        
        logger.info(f"Starting batch upload of {len(batch_files)} files to S3...")
        
        successful_uploads = []
        failed_uploads = []
        
        # Upload each file in the batch
        for file_info in batch_files:
            file_path = file_info['local_path']
            s3_key = file_info['s3_key']
            
            try:
                if not os.path.exists(file_path):
                    logger.error(f"Local file not found: {file_path}")
                    failed_uploads.append(file_info)
                    continue
                
                logger.info(f"Uploading {os.path.basename(file_path)} to S3...")
                
                with open(file_path, 'rb') as file_data:
                    s3_client.put_object(
                        Bucket=S3_BUCKET_NAME,
                        Key=s3_key,
                        Body=file_data,
                        ContentType='application/pdf'
                    )
                
                # Verify the upload by checking if file exists in S3
                try:
                    s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                    logger.info(f"✅ Successfully uploaded and verified: {s3_key}")
                    successful_uploads.append(file_info)
                except Exception as verify_error:
                    logger.error(f"❌ Upload verification failed for {s3_key}: {verify_error}")
                    failed_uploads.append(file_info)
                
            except Exception as upload_error:
                logger.error(f"❌ Failed to upload {file_path}: {upload_error}")
                failed_uploads.append(file_info)
        
        logger.info(f"Batch upload completed: {len(successful_uploads)} successful, {len(failed_uploads)} failed")
        return successful_uploads, failed_uploads
        
    except Exception as e:
        logger.error(f"Error in batch upload process: {e}")
        return [], batch_files


def cleanup_successful_files(successful_uploads):
    """Delete local files that were successfully uploaded to S3"""
    try:
        deleted_count = 0
        
        for file_info in successful_uploads:
            file_path = file_info['local_path']
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted local file: {os.path.basename(file_path)}")
                    deleted_count += 1
                else:
                    logger.warning(f"File not found for deletion: {file_path}")
            except Exception as delete_error:
                logger.error(f"Error deleting local file {file_path}: {delete_error}")
        
        logger.info(f"Cleaned up {deleted_count} local files after successful S3 upload")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 0


def process_batch_upload():
    """Process the current batch of downloaded files for S3 upload"""
    global current_batch_files
    
    if not current_batch_files:
        logger.debug("No files in current batch to upload")
        return True
    
    try:
        logger.info(f"\n=== BATCH UPLOAD PROCESS ===")
        logger.info(f"Processing batch of {len(current_batch_files)} files")
        
        # Upload batch to S3
        successful_uploads, failed_uploads = upload_batch_to_s3(current_batch_files)
        
        # Clean up successfully uploaded files
        if successful_uploads:
            cleanup_successful_files(successful_uploads)
            logger.info(f"✅ Successfully processed {len(successful_uploads)} files")
        
        # Handle failed uploads
        if failed_uploads:
            logger.warning(f"❌ {len(failed_uploads)} files failed to upload")
            
            # Move failed files to a failed directory for manual review
            failed_dir = os.path.join(batch_download_dir, "failed_uploads")
            if not os.path.exists(failed_dir):
                os.makedirs(failed_dir)
            
            for file_info in failed_uploads:
                try:
                    src_path = file_info['local_path']
                    if os.path.exists(src_path):
                        dst_path = os.path.join(failed_dir, os.path.basename(src_path))
                        os.rename(src_path, dst_path)
                        logger.info(f"Moved failed file to: {dst_path}")
                except Exception as move_error:
                    logger.error(f"Error moving failed file: {move_error}")
        
        # Clear the current batch
        current_batch_files = []
        
        # Log batch processing summary
        total_processed = len(successful_uploads) + len(failed_uploads)
        success_rate = (len(successful_uploads) / total_processed * 100) if total_processed > 0 else 0
        logger.info(f"Batch processing complete: {success_rate:.1f}% success rate")
        
        return len(failed_uploads) == 0  # Return True if no failures
        
    except Exception as e:
        logger.error(f"Error processing batch upload: {e}")
        return False




if __name__ == "__main__":
    try:
        logger.info("=" * 80)
        logger.info(f"Starting Script 46")
        logger.info(f"Page Range: 115,156 to 117,714")
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
        
        # Final cleanup and summary
        logger.info("\n=== SCRIPT COMPLETION SUMMARY ===")
        logger.info(f"Total files processed: {total_files_downloaded}")
        if current_batch_files:
            logger.info(f"Files in final batch: {len(current_batch_files)}")
        
        # Check for any remaining files in batch directory
        remaining_files = []
        if os.path.exists(batch_download_dir):
            remaining_files = [f for f in os.listdir(batch_download_dir) if f.endswith('.pdf')]
            if remaining_files:
                logger.warning(f"⚠️  {len(remaining_files)} files remain in batch directory - may need manual upload")
        
        cleanup_resources()
        
    except KeyboardInterrupt:
        logger.info("\\nScript interrupted by user")
        
        # Process any pending batch files before exit
        if current_batch_files:
            logger.info("Processing pending batch files before exit...")
            try:
                process_batch_upload()
            except Exception as batch_error:
                logger.error(f"Error processing batch during interruption: {batch_error}")
        
        cleanup_resources()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to process any pending batch files before exit
        if current_batch_files:
            logger.info("Attempting to save pending batch files before exit...")
            try:
                process_batch_upload()
            except Exception as batch_error:
                logger.error(f"Error processing batch during error handling: {batch_error}")
        
        if EMAIL_ENABLED:
            send_error_notification(
                f"Script {SCRIPT_ID} - Fatal Error",
                f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            )
        cleanup_resources()
        sys.exit(1)
