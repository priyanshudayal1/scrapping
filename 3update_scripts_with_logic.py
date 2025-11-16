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
    
    # Make captcha filenames unique per script to avoid conflicts
    functions_code = functions_code.replace(
        'captcha_img.screenshot("captcha.png")',
        'captcha_img.screenshot(f"captcha_script_{SCRIPT_ID}.png")'
    )
    functions_code = functions_code.replace(
        'with open("captcha.png", "rb") as image_file:',
        'with open(f"captcha_script_{SCRIPT_ID}.png", "rb") as image_file:'
    )
    functions_code = functions_code.replace(
        'logger.info("Captcha image saved as captcha.png")',
        'logger.info(f"Captcha image saved as captcha_script_{SCRIPT_ID}.png")'
    )
    
    # Make screenshot filenames unique per script
    functions_code = functions_code.replace(
        'driver.save_screenshot("after_loading.png")',
        'driver.save_screenshot(f"after_loading_script_{SCRIPT_ID}.png")'
    )
    functions_code = functions_code.replace(
        '# driver.save_screenshot("initial_page.png")',
        '# driver.save_screenshot(f"initial_page_script_{SCRIPT_ID}.png")'
    )
    
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
    
    # Fix filename generation to prevent empty filenames and add timestamps
    # Update sanitize_filename to ensure non-empty result
    functions_code = functions_code.replace(
        "    # Limit length to avoid filesystem issues\n    if len(filename) > 200:\n        filename = filename[:200]\n    \n    return filename",
        "    # Remove leading/trailing underscores and dots\n    filename = filename.strip('_. ')\n    \n    # If filename is empty after sanitization, return a default name\n    if not filename or len(filename) == 0:\n        filename = \"document\"\n    \n    # Limit length to avoid filesystem issues\n    if len(filename) > 200:\n        filename = filename[:200]\n    \n    return filename"
    )
    
    # Update filename generation to add timestamps for uniqueness
    functions_code = functions_code.replace(
        "                # Create filename with CNR number\n                base_filename = sanitize_filename(case_title)\n                if cnr:\n                    filename = f\"{base_filename}_CNR_{sanitize_filename(cnr)}.pdf\"\n                else:\n                    filename = f\"{base_filename}.pdf\"",
        "                # Create filename with CNR number and timestamp for uniqueness\n                base_filename = sanitize_filename(case_title)\n                timestamp = int(time.time() * 1000)  # milliseconds for uniqueness\n                \n                # Ensure base_filename is not empty\n                if not base_filename or base_filename == \"document\":\n                    base_filename = f\"judgment_{timestamp}\"\n                \n                if cnr:\n                    filename = f\"{base_filename}_CNR_{sanitize_filename(cnr)}_{timestamp}.pdf\"\n                else:\n                    filename = f\"{base_filename}_{timestamp}.pdf\""
    )
    
    # Update S3 upload to use new path structure
    functions_code = functions_code.replace(
        "            # Upload to S3 with instance-specific folder (01, 02, etc.)\n            instance_folder = f\"{INSTANCE_ID:02d}\"  # Format as 01, 02, 03, etc.\n            s3_key = f\"judgements-test-final/{instance_folder}/{safe_filename}\"",
        "            # Upload to S3 with new path structure: /judgments/(filename_scriptno)\n            # Extract base filename without extension and add script ID\n            base_name = os.path.splitext(safe_filename)[0]\n            file_extension = os.path.splitext(safe_filename)[1]\n            s3_filename = f\"{base_name}_{SCRIPT_ID:02d}{file_extension}\"\n            s3_key = f\"judgments/{s3_filename}\""
    )
    
    # Replace Google Cloud Vision API with AWS Bedrock (Claude) for captcha solving
    # Replace the client check
    functions_code = functions_code.replace(
        'if vision_client is None:\n        logger.error("Google Cloud Vision API client is not initialized.")\n        return False',
        'if bedrock_runtime is None:\n        logger.error("AWS Bedrock runtime client is not initialized.")\n        return False'
    )
    
    # Replace the Vision API captcha solving logic with Bedrock
    old_vision_logic = '''# Use Google Cloud Vision API to solve captcha
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
                result = result.replace('\\n', '').replace(' ', '')
                logger.info(f"Vision API Prediction: {result}")
            else:
                logger.warning("No text detected in captcha image")
                driver.refresh()
                time.sleep(3)
                continue'''
    
    new_bedrock_logic = '''# Use AWS Bedrock (Amazon Nova) to solve captcha with fallback
            with open(f"captcha_script_{SCRIPT_ID}.png", "rb") as image_file:
                captcha_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Try Amazon Nova Lite first, fallback to Nova Pro if it fails
            models_to_try = [
                ("arn:aws:bedrock:ap-south-1:491085399248:inference-profile/apac.amazon.nova-lite-v1:0", "Amazon Nova Lite"),
                ("arn:aws:bedrock:ap-south-1:491085399248:inference-profile/apac.amazon.nova-pro-v1:0", "Amazon Nova Pro")
            ]
            
            result = None
            for model_id, model_name in models_to_try:
                try:
                    logger.info(f"Attempting captcha with {model_name}...")
                    response = bedrock_runtime.converse(
                        modelId=model_id,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "image": {
                                            "format": "png",
                                            "source": {
                                                "bytes": base64.b64decode(captcha_base64)
                                            }
                                        }
                                    },
                                    {
                                        "text": "What text is shown in this image? Only respond with the text—no explanation."
                                    }
                                ]
                            }
                        ],
                        inferenceConfig={
                            "maxTokens": 512,
                            "temperature": 0.7,
                            "topP": 0.9,
                            "stopSequences": []
                        },
                        additionalModelRequestFields={}
                    )
                    
                    result = response['output']['message']['content'][0]['text'].strip()
                    # Remove any newlines or spaces
                    result = result.replace('\\n', '').replace(' ', '')
                    logger.info(f"{model_name} Prediction: {result}")
                    break  # Success, exit the loop
                    
                except Exception as bedrock_error:
                    logger.warning(f"{model_name} failed: {bedrock_error}")
                    if model_id == models_to_try[-1][0]:  # Last model failed
                        logger.error(f"All models failed. Last error: {bedrock_error}")
                        driver.refresh()
                        time.sleep(3)
                        continue
                    else:
                        logger.info(f"Trying fallback model...")
                        time.sleep(1)  # Brief pause before fallback
            
            if result is None:
                logger.error("Failed to get captcha result from all models")
                driver.refresh()
                time.sleep(3)
                continue'''
    
    if old_vision_logic in functions_code:
        functions_code = functions_code.replace(old_vision_logic, new_bedrock_logic)
    
    # Make Chrome headless and add stability improvements
    functions_code = functions_code.replace(
        "# chrome_options.add_argument('--headless')  # Commented out to show browser",
        "chrome_options.add_argument('--headless')  # Run in headless mode"
    )
    
    # Add comprehensive browser isolation and stability improvements
    functions_code = functions_code.replace(
        "chrome_options.add_argument('--window-size=1920,1080')\n    driver = webdriver.Chrome(options=chrome_options)",
        """chrome_options.add_argument('--window-size=1920,1080')
    
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
                raise init_error"""
    )
    
    # Also update the function to include a proper initialize_browser function template
    if "def initialize_browser():" not in functions_code:
        functions_code = functions_code.replace(
            "def close_any_open_modal():",
            """def initialize_browser():
    global driver, wait
    import random
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # CRITICAL: Multi-instance isolation
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
    
    # Shared memory isolation
    chrome_options.add_argument('--force-device-scale-factor=1')
    
    # Memory and performance optimization
    chrome_options.add_argument('--max_old_space_size=4096')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max-unused-resource-memory-usage-percentage=5')
    chrome_options.add_argument('--aggressive-cache-discard')
    
    # Unique profile and debugging port - with millisecond precision + random
    import tempfile
    profile_timestamp = int(time.time() * 1000)
    temp_base = tempfile.gettempdir()  # Cross-platform temp directory
    profile_dir = os.path.join(temp_base, f'chrome_profile_script_{SCRIPT_ID}_{profile_timestamp}_{instance_random}')
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument(f'--remote-debugging-port={9222 + SCRIPT_ID}')
    
    # Disk cache isolation
    disk_cache_dir = os.path.join(temp_base, f'chrome_cache_script_{SCRIPT_ID}_{profile_timestamp}')
    chrome_options.add_argument(f'--disk-cache-dir={disk_cache_dir}')
    chrome_options.add_argument('--disk-cache-size=104857600')
    
    # Additional isolation options
    chrome_options.add_argument(f'--crash-dumps-dir={os.path.join(temp_base, f"chrome_crashes_script_{SCRIPT_ID}_{profile_timestamp}")}')
    chrome_options.add_argument('--enable-crash-reporter=false')
    chrome_options.add_argument('--disable-crash-reporter')
    
    # Process per site
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
    
    # Set custom user agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Create Chrome instance with retry logic
    max_init_attempts = 5
    
    for attempt in range(max_init_attempts):
        try:
            logger.info(f"Attempting to create Chrome instance (attempt {attempt + 1}/{max_init_attempts}) for Script {SCRIPT_ID}")
            logger.info(f"Profile: {profile_dir}")
            logger.info(f"Debug port: {9222 + SCRIPT_ID}")
            
            # Add random startup delay to prevent simultaneous starts
            if attempt == 0:
                startup_delay = random.uniform(0.5, 3.0) * SCRIPT_ID * 0.1
                logger.info(f"Startup delay: {startup_delay:.2f}s")
                time.sleep(startup_delay)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Verify driver is working
            driver.get("data:text/html,<html><body><h1>Browser Initialized - Script {SCRIPT_ID}</h1></body></html>")
            
            # Set timeouts
            driver.set_page_load_timeout(60)
            driver.set_script_timeout(60)
            
            # Post-initialization isolation
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
                logger.info(f"Waiting {retry_delay:.2f}s before retry...")
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
        captcha_filename = f"captcha_script_{SCRIPT_ID}.png"
        captcha_img.screenshot(captcha_filename)
        logger.info(f"Captcha image saved as {captcha_filename}")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def close_any_open_modal():
            
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
        
        # Solve captcha with infinite retry logic
        captcha_attempts = 0
        
        while True:
            try:
                if fill_captcha():
                    logger.info("Captcha solved successfully during recovery")
                    break
                else:
                    captcha_attempts += 1
                    logger.warning(f"Captcha attempt {{captcha_attempts}} failed during recovery - will retry infinitely")
                    time.sleep(3)
            except Exception as captcha_error:
                captcha_attempts += 1
                logger.warning(f"Captcha error during recovery (attempt {{captcha_attempts}}): {{captcha_error}} - will retry infinitely")
                time.sleep(3)
        
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
    
    # Update download_pdf function to use improved object/embed selector approach
    if "# Wait for modal to appear" in functions_code and "New approach: Look for object/embed tags" in functions_code:
        # Replace the PDF download logic section
        old_pdf_logic = """        # Wait for modal to appear
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
                            logger.info(f"Object URL: {pdf_url}")
                            
                            if pdf_url and (".pdf" in pdf_url.lower()):
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
                                    
                                    response = session.get(pdf_url, timeout=20, headers=headers)
                                    if response.status_code == 200:
                                        if (response.headers.get('content-type', '').lower().startswith('application/pdf') or 
                                            response.content.startswith(b'%PDF')):
                                            logger.info(f"Successfully fetched PDF content ({len(response.content)} bytes)")
                                            pdf_downloaded_success = True
                                            break
                                        else:
                                            logger.warning(f"Object response is not a PDF file")
                                except Exception as obj_download_error:
                                    logger.error(f"Error downloading from object: {str(obj_download_error)}")
                                    continue
                    
                    if pdf_downloaded_success:
                        break
                except Exception as selector_error:
                    logger.debug(f"Selector {selector} failed: {str(selector_error)}")
                    continue
            
            if not pdf_downloaded_success:
                raise Exception("Could not download PDF using any selector")
                
        except Exception as e:
            logger.error(f"Error in new download approach: {e}")
            raise"""
        
        new_pdf_logic = """        # Wait for modal to appear
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
                                            logger.error(f"❌ Invalid PDF content - Content-Type: {content_type}, Size: {len(response.content)} bytes")
                                            logger.error(f"❌ URL: {pdf_url}")
                                            if len(response.content) < 1000:
                                                logger.error(f"❌ Response preview: {response.text[:500]}")
                                    else:
                                        logger.error(f"❌ HTTP {response.status_code} for URL: {pdf_url}")
                                        logger.error(f"❌ Response headers: {dict(response.headers)}")
                                        
                                except Exception as obj_download_error:
                                    logger.error(f"Error downloading from object: {str(obj_download_error)}")
                                    continue
                    
                    if pdf_downloaded_success:
                        break
                except Exception as selector_error:
                    logger.debug(f"Selector {selector} failed: {str(selector_error)}")
                    continue
            
            if not pdf_downloaded_success:
                logger.error(f"❌ FAILED: Could not download PDF using any selector")
                logger.error(f"❌ Tried {len(pdf_selectors)} different selectors")
                logger.error(f"❌ Case: {judgment_data.get('case_title', 'Unknown')[:100]}")
                raise Exception("Could not download PDF using any selector")
                
        except Exception as e:
            logger.error(f"❌ Error in PDF download approach: {e}")
            logger.error(f"❌ Case: {judgment_data.get('case_title', 'Unknown')[:100]}")
            raise"""
        
        functions_code = functions_code.replace(old_pdf_logic, new_pdf_logic)
    
    # Replace navigate_to_specific_page function with proper implementation
    if "def navigate_to_specific_page(target_page):" in functions_code:
        old_navigate = """def navigate_to_specific_page(target_page):
    \"\"\"Navigate to a specific page number by clicking 'Next'\"\"\"
    global current_page, driver, wait
    
    try:
        if driver is None:
            logger.error("Driver is None, cannot navigate")
            return False
        
        try:
            driver.current_url
        except Exception as e:
            logger.error(f"Driver is not responsive: {e}")
            return False
        
        logger.info(f"Navigating to page {target_page} from {current_page}...")

        if target_page <= current_page:
            logger.warning(f"Target page {target_page} is not greater than current page {current_page}. Navigation might not be as expected.")
            if target_page < current_page:
                logger.error("Cannot navigate backwards with this method. Reinitialization would be required.")
                return False

        while current_page < target_page:
            logger.info(f"Current page: {current_page}, Target: {target_page}. Clicking 'Next'.")
            
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "example_pdf_next")))
            
            if "disabled" in next_button.get_attribute("class"):
                logger.error(f"Cannot navigate further. 'Next' button is disabled on page {current_page}.")
                return False

            next_button.click()
            
            time.sleep(2) 
            wait.until(EC.presence_of_element_located((By.ID, "report_body")))
            
            current_page += 1
            logger.info(f"Successfully navigated to page {current_page}")

        logger.info(f"Reached target page {target_page}")
        return True
        
    except Exception as e:
        logger.error(f"Error navigating to page {target_page}: {e}")
        logger.error(traceback.format_exc())
        return False"""
        
        new_navigate = """def navigate_to_specific_page(target_page, max_retries=3):
    \"\"\"Navigate to a specific page number by clicking 'Next' button repeatedly\"\"\"
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
    
    return False"""
        
        functions_code = functions_code.replace(old_navigate, new_navigate)
        
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
    
    # Fix batch processing logic to properly continue after each batch
    if "# Process in batches of 25" in functions_code and "files_processed_on_page = 0" in functions_code:
        # Update batch processing header
        functions_code = functions_code.replace(
            """            # Process in batches of 25
            files_processed_on_page = 0
            
            while files_processed_on_page < len(judgments_data):
                batch_start = files_processed_on_page
                batch_end = min(files_processed_on_page + 25, len(judgments_data))
                
                logger.info(f"\\n--- Processing batch {batch_start+1}-{batch_end} on page {current_page} ---")""",
            """            # Process in batches of 25
            files_processed_on_page = 0
            
            while files_processed_on_page < len(judgments_data):
                batch_start = files_processed_on_page
                batch_end = min(files_processed_on_page + 25, len(judgments_data))
                
                logger.info(f"\\n--- Processing batch {batch_start+1}-{batch_end} on page {current_page} (Total on page: {len(judgments_data)}) ---")"""
        )
        
        # Update batch continuation logic
        functions_code = functions_code.replace(
            """                files_processed_on_page = batch_end
                
                # If we've processed a full batch of 25 and there are more files on this page
                if (batch_end - batch_start) == 25 and files_processed_on_page < len(judgments_data):
                    logger.info(f"Completed batch of 25 files. Reinitializing session before next batch...")
                    
                    if not reinitialize_session():
                        logger.error("Failed to reinitialize session. Stopping process.")
                        return
                    
                    # Re-extract table data after reinitialization
                    judgments_data = extract_table_data()
                    if not judgments_data:
                        logger.error("Failed to re-extract table data after reinitialization")
                        return""",
            """                files_processed_on_page = batch_end
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
                    logger.info(f"No reinitialization needed. Continuing to next page.")"""
        )
    
    # Add enhanced error logging for download failures
    if 'logger.error(f"Failed to download PDF. Status code:' in functions_code:
        functions_code = functions_code.replace(
            'logger.error(f"Failed to download PDF. Status code: {response.status_code if response else \'No response\'}")',
            '''logger.error(f"❌ DOWNLOAD FAILED for: {judgment_data['case_title'][:50]}")
            logger.error(f"❌ Status code: {response.status_code if response else 'No response'}")
            logger.error(f"❌ CNR: {judgment_data.get('cnr', 'N/A')}")
            if response:
                logger.error(f"❌ Response size: {len(response.content)} bytes")
                logger.error(f"❌ Content-Type: {response.headers.get('content-type', 'Unknown')}")'''
        )
    
    # Add enhanced exception logging
    if 'logger.error(f"Error downloading PDF for {judgment_data' in functions_code:
        functions_code = functions_code.replace(
            'logger.error(f"Error downloading PDF for {judgment_data[\'case_title\'][:50]}: {e}")',
            '''logger.error(f"❌ EXCEPTION during PDF download")
        logger.error(f"❌ Case: {judgment_data['case_title'][:50]}")
        logger.error(f"❌ CNR: {judgment_data.get('cnr', 'N/A')}")
        logger.error(f"❌ Error: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")'''
        )
    
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


# Initialize AWS Bedrock and S3 clients
try:
    from botocore.config import Config
    from botocore.exceptions import ClientError, EndpointConnectionError, ReadTimeoutError, ConnectTimeoutError
    
    config = Config(
        connect_timeout=30,
        read_timeout=30,
        retries={{'max_attempts': 2}}
    )

    # Initialize AWS session with credentials from environment variables
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'ap-south-1')
    )
    bedrock_runtime = session.client("bedrock-runtime", config=config)
    s3_client = session.client("s3", config=config)
    S3_BUCKET_NAME = "judgements-vectors-pdf"
    logger.info("AWS Bedrock and S3 clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AWS clients: {{str(e)}}")
    bedrock_runtime = None
    s3_client = None
    S3_BUCKET_NAME = None

# Email configuration
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_ENABLED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)  # Enabled

# Global variables
driver = None
wait = None
current_page = START_PAGE
total_files_downloaded = 0
start_time = None


def cleanup_resources():
    \"\"\"Clean up browser resources for this script instance ONLY\"\"\"
    global driver
    try:
        if driver:
            logger.info(f"Cleaning up browser resources for Script {{SCRIPT_ID}}")
            
            # Quit the driver gracefully - this will close only this script's Chrome instance
            try:
                driver.quit()
                logger.debug("WebDriver quit successfully")
            except Exception as quit_error:
                logger.warning(f"Error quitting WebDriver: {{quit_error}}")
            
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
                                    if f'chrome_profile_script_{{SCRIPT_ID}}_' in cmdline:
                                        logger.debug(f"Terminating Chrome process {{proc.info['pid']}} for Script {{SCRIPT_ID}}")
                                        proc.terminate()
                                        proc.wait(timeout=3)
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                            pass
                except Exception as proc_error:
                    logger.warning(f"Error during process cleanup: {{proc_error}}")
                
            # Clean up only THIS script's profile and cache directories
            if SHUTIL_AVAILABLE:
                try:
                    import tempfile
                    temp_dir = tempfile.gettempdir()  # Cross-platform temp directory
                    if os.path.exists(temp_dir):
                        for item in os.listdir(temp_dir):
                            # Only delete profiles/caches that start with our script ID
                            if (item.startswith(f'chrome_profile_script_{{SCRIPT_ID}}_') or 
                                item.startswith(f'chrome_cache_script_{{SCRIPT_ID}}_') or
                                item.startswith(f'chrome_crashes_script_{{SCRIPT_ID}}_')):
                                dir_path = os.path.join(temp_dir, item)
                                if os.path.isdir(dir_path):
                                    try:
                                        shutil.rmtree(dir_path, ignore_errors=True)
                                        logger.debug(f"Cleaned up directory: {{dir_path}}")
                                    except Exception as cleanup_error:
                                        logger.debug(f"Could not clean up {{dir_path}}: {{cleanup_error}}")
                except Exception as dir_cleanup_error:
                    logger.debug(f"Error during directory cleanup: {{dir_cleanup_error}}")
                
            logger.info(f"Cleanup completed for Script {{SCRIPT_ID}}")
            
    except Exception as e:
        logger.warning(f"Error during cleanup: {{e}}")


def force_cleanup_chrome_processes():
    \"\"\"Force cleanup of any hanging Chrome processes for this script ONLY\"\"\"
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
                        # CRITICAL: Only terminate Chrome with THIS script's unique profile (with timestamp)
                        # This prevents killing other Chrome instances including user's personal browser
                        if f'chrome_profile_script_{{SCRIPT_ID}}_' in cmdline:
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
            
            # Try to find and terminate the conflicting process ONLY if it's our script's Chrome
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            # Only terminate if BOTH the port AND our profile are in the command line
                            # This prevents terminating other Chrome instances that happen to use the same port
                            if f'remote-debugging-port={{debug_port}}' in cmdline and f'chrome_profile_script_{{SCRIPT_ID}}_' in cmdline:
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
    
    # Cleanup any existing profile, cache, and crash directories
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()  # Cross-platform temp directory
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                # Clean up all Chrome-related directories for this script
                if (item.startswith(f'chrome_profile_script_{{SCRIPT_ID}}_') or 
                    item.startswith(f'chrome_cache_script_{{SCRIPT_ID}}_') or
                    item.startswith(f'chrome_crashes_script_{{SCRIPT_ID}}_')):
                    dir_path = os.path.join(temp_dir, item)
                    if os.path.isdir(dir_path):
                        try:
                            if SHUTIL_AVAILABLE:
                                shutil.rmtree(dir_path, ignore_errors=True)
                                logger.debug(f"Cleaned up existing directory: {{dir_path}}")
                        except Exception as cleanup_error:
                            logger.debug(f"Could not clean up {{dir_path}}: {{cleanup_error}}")
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
        import tempfile
        logger.info(f"Profile Directory: {{os.path.join(tempfile.gettempdir(), 'chrome_profile_script_' + str(SCRIPT_ID) + '_*')}}")
        logger.info("=" * 80)
        
        # Step 0: Pre-launch cleanup and preparation
        logger.info("Performing pre-launch cleanup...")
        pre_launch_cleanup()
        
        # Step 1: Initialize browser and load page
        logger.info("Initializing browser...")
        initialize_browser()

        # Step 2: Solve captcha with infinite retry logic
        logger.info("Solving captcha...")
        captcha_attempts = 0
        while True:
            try:
                if fill_captcha():
                    logger.info("Captcha solved successfully")
                    break
                else:
                    captcha_attempts += 1
                    logger.warning(f"Captcha attempt {{captcha_attempts}} failed - will retry infinitely")
                    time.sleep(3)
            except Exception as captcha_error:
                captcha_attempts += 1
                logger.warning(f"Captcha error (attempt {{captcha_attempts}}): {{captcha_error}} - will retry infinitely")
                time.sleep(3)
        
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
