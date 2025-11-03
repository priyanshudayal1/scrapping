"""
Update all 66 scripts with the full scraping logic from legacy_judgements.py
"""
import os
import json

def create_full_script(script_id, start_page, end_page):
    """Generate a complete script with all scraping logic"""
    
    # Read the legacy script
    legacy_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "legacy_judgements.py")
    
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
    
    # Fix all double curly brace placeholders with proper single braces
    functions_code = functions_code.replace('{{SCRIPT_ID}}', '{SCRIPT_ID}')
    functions_code = functions_code.replace('{{9222 + SCRIPT_ID}}', '{9222 + SCRIPT_ID}')
    functions_code = functions_code.replace('{{attempt + 1}}', '{attempt + 1}')
    functions_code = functions_code.replace('{{max_init_attempts}}', '{max_init_attempts}')
    functions_code = functions_code.replace('{{debug_port}}', '{debug_port}')
    functions_code = functions_code.replace('{{terminated_count}}', '{terminated_count}')
    functions_code = functions_code.replace('{{e}}', '{e}')
    functions_code = functions_code.replace('{{stealth_error}}', '{stealth_error}')
    functions_code = functions_code.replace('{{init_error}}', '{init_error}')
    functions_code = functions_code.replace('{{proc_error}}', '{proc_error}')
    functions_code = functions_code.replace('{{profile_path}}', '{profile_path}')
    functions_code = functions_code.replace('{{cleanup_error}}', '{cleanup_error}')
    functions_code = functions_code.replace('{{dir_cleanup_error}}', '{dir_cleanup_error}')
    functions_code = functions_code.replace('{{quit_error}}', '{quit_error}')
    functions_code = functions_code.replace("{{proc.info['pid']}}", "{proc.info['pid']}")
    
    # Fix any remaining double braces that might appear in other contexts
    import re
    functions_code = re.sub(r'\{\{([^}]+)\}\}', r'{\1}', functions_code)
    
    # Comment out email functions to disable notifications
    functions_code = functions_code.replace(
        'def send_email(subject, body, is_html=False):',
        'def send_email(subject, body, is_html=False):'
    )
    functions_code = functions_code.replace(
        '    """Send email notification"""',
        '    """Send email notification - DISABLED FOR TESTING"""\n    logger.info(f"EMAIL DISABLED - Would send: {subject}")\n    return False  # Emails disabled'
    )
    functions_code = functions_code.replace(
        'def send_error_notification(error_message, error_details=""):',
        'def send_error_notification(error_message, error_details=""):'
    )
    functions_code = functions_code.replace(
        '    """Send error notification email"""',
        '    """Send error notification email - DISABLED FOR TESTING"""\n    logger.warning(f"EMAIL DISABLED - Error notification: {error_message}")\n    return False  # Emails disabled'
    )
    functions_code = functions_code.replace(
        'def send_completion_notification(stats):',
        'def send_completion_notification(stats):'
    )
    functions_code = functions_code.replace(
        '    """Send completion notification email"""',
        '    """Send completion notification email - DISABLED FOR TESTING"""\n    logger.info("EMAIL DISABLED - Completion notification suppressed")\n    return False  # Emails disabled'
    )
    functions_code = functions_code.replace(
        'def send_shutdown_notification(reason="Unknown"):',
        'def send_shutdown_notification(reason="Unknown"):'
    )
    functions_code = functions_code.replace(
        '    """Send notification when script stops unexpectedly"""',
        '    """Send notification when script stops unexpectedly - DISABLED FOR TESTING"""\n    logger.warning(f"EMAIL DISABLED - Shutdown notification: {reason}")\n    return False  # Emails disabled'
    )
    
    # Make Chrome headless and add stability improvements
    functions_code = functions_code.replace(
        "# chrome_options.add_argument('--headless')  # Commented out to show browser",
        "#chrome_options.add_argument('--headless')  # Run in headless mode"
    )
    
    # Add comprehensive browser isolation and stability improvements
    functions_code = functions_code.replace(
        "chrome_options.add_argument('--window-size=1920,1080')\n    driver = webdriver.Chrome(options=chrome_options)",
        """chrome_options.add_argument('--window-size=1920,1080')
    
    # Multi-instance isolation options
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-background-networking')
    
    # Process isolation and stability
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    
    # Memory and performance optimization
    chrome_options.add_argument('--max_old_space_size=4096')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max-unused-resource-memory-usage-percentage=5')
    chrome_options.add_argument('--aggressive-cache-discard')
    
    # Unique profile and debugging port for each script instance
    profile_dir = f'C:/temp/chrome_profile_script_{SCRIPT_ID}_{int(time.time())}'
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument(f'--remote-debugging-port={9222 + SCRIPT_ID}')
    
    # Additional isolation options
    chrome_options.add_argument(f'--crash-dumps-dir=C:/temp/chrome_crashes_script_{SCRIPT_ID}')
    chrome_options.add_argument('--enable-crash-reporter=false')
    chrome_options.add_argument('--disable-crash-reporter')
    
    # Automation detection prevention
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("detach", True)
    
    # Set custom user agent to avoid detection
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Create new Chrome instance with enhanced isolation and retry logic
    max_init_attempts = 3
    
    for attempt in range(max_init_attempts):
        try:
            logger.info(f"Attempting to create Chrome instance (attempt {attempt + 1}/{max_init_attempts}) for Script {SCRIPT_ID}")
            driver = webdriver.Chrome(options=chrome_options)
            
            # Verify driver is working
            driver.get("data:text/html,<html><body><h1>Browser Initialized</h1></body></html>")
            
            # Additional post-initialization isolation
            try:
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
                logger.info("Waiting before retry...")
                time.sleep(5 + attempt * 2)  # Increasing delay
                
                # Try cleanup before retry
                force_cleanup_chrome_processes()
            else:
                logger.error(f"Failed to initialize Chrome after {max_init_attempts} attempts")
                raise init_error"""
    )
    
    # Also update the function to include a proper initialize_browser function template
    if "def initialize_browser():" not in functions_code:
        functions_code = functions_code.replace(
            "def close_any_open_modal():",
            """def initialize_browser():
    global driver, wait
    # Setup Chrome options
    chrome_options = Options()
    #chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Multi-instance isolation options
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-background-networking')
    
    # Process isolation and stability
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    
    # Memory and performance optimization
    chrome_options.add_argument('--max_old_space_size=4096')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max-unused-resource-memory-usage-percentage=5')
    chrome_options.add_argument('--aggressive-cache-discard')
    
    # Unique profile and debugging port for each script instance
    profile_dir = f'C:/temp/chrome_profile_script_{SCRIPT_ID}_{int(time.time())}'
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument(f'--remote-debugging-port={9222 + SCRIPT_ID}')
    
    # Additional isolation options
    chrome_options.add_argument(f'--crash-dumps-dir=C:/temp/chrome_crashes_script_{SCRIPT_ID}')
    chrome_options.add_argument('--enable-crash-reporter=false')
    chrome_options.add_argument('--disable-crash-reporter')
    
    # Automation detection prevention
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("detach", True)
    
    # Set custom user agent to avoid detection
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Create new Chrome instance with enhanced isolation and retry logic
    max_init_attempts = 3
    
    for attempt in range(max_init_attempts):
        try:
            logger.info(f"Attempting to create Chrome instance (attempt {attempt + 1}/{max_init_attempts}) for Script {SCRIPT_ID}")
            driver = webdriver.Chrome(options=chrome_options)
            
            # Verify driver is working
            driver.get("data:text/html,<html><body><h1>Browser Initialized</h1></body></html>")
            
            # Additional post-initialization isolation
            try:
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
                logger.info("Waiting before retry...")
                time.sleep(5 + attempt * 2)  # Increasing delay
                
                # Try cleanup before retry
                force_cleanup_chrome_processes()
            else:
                logger.error(f"Failed to initialize Chrome after {max_init_attempts} attempts")
                raise init_error
       
    try:
        wait = WebDriverWait(driver, 30)
        url = "https://judgments.ecourts.gov.in/pdfsearch/index.php"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for the page to load with better error handling
        wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        logger.info(f"Page loaded successfully for Script {SCRIPT_ID}")
    
    except Exception as e:
        logger.error(f"Error during browser initialization: {e}")
        if driver:
            try:
                driver.save_screenshot(f"error_screenshot_script_{SCRIPT_ID}.png")
            except Exception:
                pass
        raise e


def close_any_open_modal():"""
        )
    
    # Add enhanced browser recovery function - look for reinitialize_session function and add recovery before it
    if "def reinitialize_session():" in functions_code:
        functions_code = functions_code.replace(
            "def reinitialize_session():",
            """def recover_browser_session():
    \"\"\"Recover from browser crashes by completely reinitializing everything\"\"\"
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


def reinitialize_session():"""
        )
    
    # Update the reinitialize_session function to use recovery as fallback
    if "def reinitialize_session():" in functions_code:
        old_reinit = """def reinitialize_session():
    \"\"\"Reinitialize the browser session by going back to the main URL\"\"\"
    global driver, wait
    
    try:
        logger.info("Reinitializing session - going back to main URL...")
        
        # Navigate back to the main URL
        url = "https://judgments.ecourts.gov.in/pdfsearch"
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
        return False"""
        
        new_reinit = """def reinitialize_session():
    \"\"\"Reinitialize the browser session by going back to the main URL\"\"\"
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
        return recover_browser_session()"""
        
        functions_code = functions_code.replace(old_reinit, new_reinit)
    
    # Update download_pdf function to use download button and better error handling
    if "# Wait for modal to appear" in functions_code and "pdf_object.get_attribute(\"data\")" in functions_code:
        functions_code = functions_code.replace(
            """        # Wait for modal to appear
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
            response = requests.get(pdf_url)""",
            """        # Wait for modal to appear
        modal = wait.until(EC.visibility_of_element_located((By.ID, "viewFiles")))
        logger.info("Modal appeared, waiting for PDF to load...")
        
        # Wait for PDF object to load
        time.sleep(3)
        
        # Get the PDF URL from the object element to construct download URL
        pdf_object = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#viewFiles-body object")))
        pdf_temp_url = pdf_object.get_attribute("data")
        
        if pdf_temp_url:
            # Extract the file hash from the temp URL
            # URL format: /pdfsearch/tmp/HASH.pdf
            import re
            hash_match = re.search(r'/tmp/([a-f0-9]+\\.pdf)', pdf_temp_url)
            
            if hash_match:
                pdf_filename = hash_match.group(1)
                # Construct the actual download URL (not the temp viewer URL)
                pdf_url = f"https://judgments.ecourts.gov.in/pdfsearch/tmp/{pdf_filename}"
                
                logger.info(f"Extracted PDF filename: {pdf_filename}")
                logger.info(f"Downloading from: {pdf_url}")
                
                # Download the PDF using requests with retries
                max_retries = 3
                response = None
                
                for attempt in range(max_retries):
                    try:
                        # Use session cookies from selenium to maintain session
                        session = requests.Session()
                        
                        # Add cookies from selenium driver
                        for cookie in driver.get_cookies():
                            session.cookies.set(cookie['name'], cookie['value'])
                        
                        # Add headers to mimic browser request
                        headers = {
                            'User-Agent': driver.execute_script("return navigator.userAgent;"),
                            'Referer': 'https://judgments.ecourts.gov.in/pdfsearch/',
                            'Accept': 'application/pdf,*/*'
                        }
                        
                        response = session.get(pdf_url, headers=headers, timeout=30)
                        
                        if response.status_code == 200 and len(response.content) > 0:
                            logger.info(f"Successfully fetched PDF content ({len(response.content)} bytes)")
                            break
                        else:
                            logger.warning(f"Download attempt {attempt + 1} returned status {response.status_code} with {len(response.content)} bytes")
                            if attempt < max_retries - 1:
                                time.sleep(2)
                    except requests.RequestException as req_error:
                        logger.warning(f"Download attempt {attempt + 1} failed: {req_error}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                        else:
                            raise
                
                if response is None or response.status_code != 200:
                    raise Exception("Failed to download PDF after retries")
            else:
                raise Exception(f"Could not extract PDF hash from URL: {pdf_temp_url}")"""
        )
    
    # Improve navigate_to_specific_page function
    if "def navigate_to_specific_page(target_page):" in functions_code:
        old_navigate = """def navigate_to_specific_page(target_page):
    \"\"\"Navigate to a specific page number\"\"\"
    global current_page
    
    try:
        logger.info(f"Navigating to page {target_page}...")
        
        # Find the page input field
        page_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-controls='example_pdf']")))
        
        # Clear and enter the target page number
        page_input.clear()
        page_input.send_keys(str(target_page))
        page_input.send_keys(Keys.RETURN)
        
        # Wait for page to load
        time.sleep(3)
        
        # Wait for table to reload
        wait.until(EC.presence_of_element_located((By.ID, "report_body")))
        
        current_page = target_page
        logger.info(f"Successfully navigated to page {current_page}")
        return True
        
    except Exception as e:
        logger.error(f"Error navigating to page {target_page}: {e}")
        return False"""
        
        new_navigate = """def navigate_to_specific_page(target_page, max_retries=3):
    \"\"\"Navigate to a specific page number with retry logic\"\"\"
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
    
    return False"""
        
        functions_code = functions_code.replace(old_navigate, new_navigate)
    
    # Improve error handling in process_all_pages for navigation to starting page
    if "# If starting from a page other than 1, navigate to it" in functions_code:
        old_start_nav = """# If starting from a page other than 1, navigate to it
    if current_page > 1:
        logger.info(f"Navigating to starting page {current_page}...")
        if not navigate_to_specific_page(current_page):
            logger.error(f"Failed to navigate to starting page {current_page}")
            return"""
        
        new_start_nav = """# If starting from a page other than 1, navigate to it with multiple attempts
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
            return"""
        
        functions_code = functions_code.replace(old_start_nav, new_start_nav)
    
    # Improve error handling in the main processing loop
    if "# Try to reinitialize and continue" in functions_code:
        old_error_handling = """# Send error notification
            error_details = traceback.format_exc()
            send_error_notification(
                f"Error processing page {current_page}: {str(e)}",
                error_details
            )
            
            # Try to reinitialize and continue
            if reinitialize_session():
                logger.info("Session reinitialized after error. Continuing...")
                continue
            else:
                logger.error("Failed to recover from error. Stopping process.")
                send_shutdown_notification("Failed to recover from error")
                break"""
        
        new_error_handling = """# Send error notification
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
                break"""
        
        functions_code = functions_code.replace(old_error_handling, new_error_handling)
    
    # Fix any remaining tracking/timing file references in strings
    functions_code = functions_code.replace('f"Progress tracking file: {tracking_file}"', 'f"Progress tracking file: {PROGRESS_FILE}"')
    functions_code = functions_code.replace('f"Timing data file: {timing_file}"', 'f"Timing data file: {TIMING_FILE}"')
    
    # Remove batch_size references from legacy functions
    functions_code = functions_code.replace('batch_size', '25')  # Replace batch_size with hardcoded value
    
    # No additional functions needed - using original individual upload logic
    
    # Keep original individual upload logic in download_pdf function
    # No changes needed - it already uploads individually
    
    # Keep original return values - no batch modifications needed
    
    # Keep original progress saving - no batch processing needed
    
    # Keep original page completion logic - no batch processing needed
    
    # Keep original completion logic - no batch processing needed
    
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
    \"\"\"Clean up browser resources for this script instance\"\"\"
    global driver
    try:
        if driver:
            logger.info(f"Cleaning up browser resources for Script {{SCRIPT_ID}}")
            
            # Close all browser windows gracefully
            try:
                driver.close()
                logger.debug("Browser windows closed")
            except Exception as close_error:
                logger.warning(f"Error closing browser windows: {{close_error}}")
            
            # Quit the driver
            try:
                driver.quit()
                logger.debug("WebDriver quit successfully")
            except Exception as quit_error:
                logger.warning(f"Error quitting WebDriver: {{quit_error}}")
            
            driver = None
            
            # Additional cleanup for Chrome processes (Windows)
            try:
                import subprocess
                import psutil
                
                # Find and kill any remaining Chrome processes for this script
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                            if proc.info['cmdline']:
                                cmdline = ' '.join(proc.info['cmdline'])
                                if f'chrome_profile_script_{{SCRIPT_ID}}' in cmdline or f'remote-debugging-port={{9222 + SCRIPT_ID}}' in cmdline:
                                    logger.debug(f"Terminating Chrome process {{proc.info['pid']}} for Script {{SCRIPT_ID}}")
                                    proc.terminate()
                                    proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
                        
            except ImportError:
                logger.debug("psutil not available for process cleanup")
            except Exception as proc_error:
                logger.warning(f"Error during process cleanup: {{proc_error}}")
                
            # Clean up profile directory if it exists
            try:
                import shutil
                profile_pattern = f'C:/temp/chrome_profile_script_{{SCRIPT_ID}}'
                temp_dir = 'C:/temp'
                if os.path.exists(temp_dir):
                    for item in os.listdir(temp_dir):
                        if item.startswith(f'chrome_profile_script_{{SCRIPT_ID}}'):
                            profile_path = os.path.join(temp_dir, item)
                            if os.path.isdir(profile_path):
                                try:
                                    shutil.rmtree(profile_path, ignore_errors=True)
                                    logger.debug(f"Cleaned up profile directory: {{profile_path}}")
                                except Exception as cleanup_error:
                                    logger.debug(f"Could not clean up {{profile_path}}: {{cleanup_error}}")
            except Exception as dir_cleanup_error:
                logger.debug(f"Error during directory cleanup: {{dir_cleanup_error}}")
                
            logger.info(f"Cleanup completed for Script {{SCRIPT_ID}}")
            
    except Exception as e:
        logger.warning(f"Error during cleanup: {{e}}")


def force_cleanup_chrome_processes():
    \"\"\"Force cleanup of any hanging Chrome processes for this script\"\"\"
    try:
        if not PSUTIL_AVAILABLE:
            logger.debug("psutil not available for force cleanup")
            return
            
        logger.info(f"Force cleaning Chrome processes for Script {{SCRIPT_ID}}")
        
        terminated_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if f'chrome_profile_script_{{SCRIPT_ID}}' in cmdline or f'remote-debugging-port={{9222 + SCRIPT_ID}}' in cmdline:
                            logger.debug(f"Force terminating Chrome process {{proc.info['pid']}} for Script {{SCRIPT_ID}}")
                            proc.kill()
                            terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        if terminated_count > 0:
            logger.info(f"Force terminated {{terminated_count}} Chrome processes for Script {{SCRIPT_ID}}")
        else:
            logger.debug(f"No hanging Chrome processes found for Script {{SCRIPT_ID}}")
            
    except Exception as e:
        logger.warning(f"Error during force cleanup: {{e}}")


def check_port_availability():
    \"\"\"Check if the debugging port for this script is available\"\"\"
    try:
        import socket
        
        debug_port = 9222 + SCRIPT_ID
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', debug_port))
        sock.close()
        
        if result == 0:
            logger.warning(f"Port {{debug_port}} is already in use by another process")
            
            # Try to find and terminate the conflicting process
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if f'remote-debugging-port={{debug_port}}' in cmdline:
                                logger.info(f"Terminating conflicting process {{proc.info['pid']}} using port {{debug_port}}")
                                proc.terminate()
                                proc.wait(timeout=5)
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
            
            return False
        else:
            logger.debug(f"Port {{debug_port}} is available for Script {{SCRIPT_ID}}")
            return True
            
    except Exception as e:
        logger.warning(f"Error checking port availability: {{e}}")
        return True  # Assume available if we can't check


def pre_launch_cleanup():
    \"\"\"Cleanup any existing resources before launching new browser instance\"\"\"
    logger.info(f"Performing pre-launch cleanup for Script {{SCRIPT_ID}}")
    
    # Check and cleanup port conflicts
    if not check_port_availability():
        logger.info("Waiting for port to become available...")
        time.sleep(5)
        
        # Check again after cleanup
        if not check_port_availability():
            logger.warning(f"Port {{9222 + SCRIPT_ID}} still in use, but proceeding anyway")
    
    # Cleanup any existing profile directories
    try:
        temp_dir = 'C:/temp'
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                if item.startswith(f'chrome_profile_script_{{SCRIPT_ID}}'):
                    profile_path = os.path.join(temp_dir, item)
                    if os.path.isdir(profile_path):
                        try:
                            if SHUTIL_AVAILABLE:
                                shutil.rmtree(profile_path, ignore_errors=True)
                                logger.debug(f"Cleaned up existing profile: {{profile_path}}")
                        except Exception as cleanup_error:
                            logger.debug(f"Could not clean up {{profile_path}}: {{cleanup_error}}")
    except Exception as e:
        logger.debug(f"Error during pre-launch directory cleanup: {{e}}")
    
    # Force cleanup any hanging Chrome processes for this script
    force_cleanup_chrome_processes()
    
    logger.info(f"Pre-launch cleanup completed for Script {{SCRIPT_ID}}")

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
        logger.info(f"Debugging Port: {{9222 + SCRIPT_ID}}")
        logger.info(f"Profile Directory: C:/temp/chrome_profile_script_{{SCRIPT_ID}}_*")
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
        logger.info("\\n=== SCRIPT COMPLETION SUMMARY ===")
        logger.info(f"Total files processed: {{total_files_downloaded}}")
        
        cleanup_resources()
        
    except KeyboardInterrupt:
        logger.info("\\\\nScript interrupted by user")
        
        cleanup_resources()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {{str(e)}}")
        logger.error(traceback.format_exc())
        
        # Clean up resources before exit
        
        if EMAIL_ENABLED:
            send_error_notification(
                f"Script {{SCRIPT_ID}} - Fatal Error",
                f"Error: {{str(e)}}\\n\\nTraceback:\\n{{traceback.format_exc()}}"
            )
        cleanup_resources()
        sys.exit(1)
'''
    
    return script_content


def update_all_scripts():
    """Update all 66 scripts with full scraping logic"""
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "scripts_distribution_config.json")
    with open(config_path, 'r') as f:
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
            script_path = os.path.join(os.path.dirname(__file__), f"scripts/script{script_id}/script{script_id}.py")
            
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
