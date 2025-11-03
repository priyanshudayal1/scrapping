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
    
    # Make Chrome headless and add stability improvements
    functions_code = functions_code.replace(
        "# chrome_options.add_argument('--headless')  # Commented out to show browser",
        "chrome_options.add_argument('--headless')  # Run in headless mode"
    )
    
    # Add browser stability improvements
    functions_code = functions_code.replace(
        "chrome_options.add_argument('--window-size=1920,1080')\n    driver = webdriver.Chrome(options=chrome_options)",
        """chrome_options.add_argument('--window-size=1920,1080')
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
    driver = webdriver.Chrome(options=chrome_options)"""
    )
    
    # Add browser recovery function - look for reinitialize_session function and add recovery before it
    if "def reinitialize_session():" in functions_code:
        functions_code = functions_code.replace(
            "def reinitialize_session():",
            """def recover_browser_session():
    \"\"\"Recover from browser crashes by completely reinitializing everything\"\"\"
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
    
    # Add batch processing functions
    batch_functions = '''

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
        logger.info(f"\\n=== BATCH UPLOAD PROCESS ===")
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

'''
    
    functions_code += batch_functions
    
    # Modify download_pdf function for batch processing
    if "# Save the PDF locally first" in functions_code:
        old_download_save = """# Save the PDF locally first
                with open(safe_filename, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Successfully downloaded: {safe_filename}")
                
                # Upload to S3
                s3_key = f"judgements/{safe_filename}"
                upload_success = upload_to_s3(safe_filename, s3_key)
                
                # Delete local file after successful upload
                if upload_success:
                    delete_local_file(safe_filename)
                else:
                    logger.warning(f"Failed to upload to S3, keeping local file: {safe_filename}")"""
        
        new_download_save = """# Save the PDF to batch download directory
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
                logger.info(f"Added to batch: {len(current_batch_files)}/{batch_size} files")"""
        
        functions_code = functions_code.replace(old_download_save, new_download_save)
    
    # Update return value in download_pdf function
    if '"uploaded_to_s3": upload_success,' in functions_code:
        old_return = '''"uploaded_to_s3": upload_success,
                    "cnr": judgment_data['cnr'],
                    "case_title": judgment_data['case_title'],
                    "decision_date": judgment_data.get('decision_date', ''),
                    "decision_year": judgment_data.get('decision_year'),
                    "download_time": datetime.now().isoformat(),
                    "download_duration_seconds": round(download_duration, 2)'''
        
        new_return = '''"local_path": local_file_path,
                    "uploaded_to_s3": False,  # Will be updated after batch upload
                    "cnr": judgment_data['cnr'],
                    "case_title": judgment_data['case_title'],
                    "decision_date": judgment_data.get('decision_date', ''),
                    "decision_year": judgment_data.get('decision_year'),
                    "download_time": datetime.now().isoformat(),
                    "download_duration_seconds": round(download_duration, 2),
                    "in_batch": True'''
        
        functions_code = functions_code.replace(old_return, new_return)
    
    # Fix s3_key reference in return statement
    if '"s3_key": s3_key if upload_success else None,' in functions_code:
        functions_code = functions_code.replace(
            '"s3_key": s3_key if upload_success else None,',
            '"s3_key": s3_key,'
        )
    
    # Add batch processing logic to main processing loop
    if "# Save progress and timing after each successful download" in functions_code:
        old_progress_save = """# Save progress and timing after each successful download
                        save_progress(progress)
                        save_timing_data(timing_data)"""
        
        new_progress_save = """# Check if batch is full and process upload
                        if len(current_batch_files) >= batch_size:
                            logger.info(f"\\n📦 Batch of {batch_size} files ready for S3 upload")
                            
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
                        save_timing_data(timing_data)"""
        
        functions_code = functions_code.replace(old_progress_save, new_progress_save)
    
    # Add batch processing at end of page
    if "# Mark page as completed" in functions_code:
        old_page_complete = """logger.info(f"Completed page {current_page}. Total files downloaded so far: {total_files_downloaded}")
            
            # Mark page as completed
            if current_page not in progress.get('pages_completed', []):
                progress['pages_completed'].append(current_page)
                save_progress(progress)"""
        
        new_page_complete = """# Process any remaining files in the current batch at the end of the page
            if current_batch_files:
                logger.info(f"\\n📦 Processing remaining {len(current_batch_files)} files in batch at end of page {current_page}")
                batch_success = process_batch_upload()
                
                if batch_success:
                    logger.info(f"✅ Final batch upload for page {current_page} completed successfully")
                else:
                    logger.warning(f"⚠️  Some files in final batch failed to upload")
            
            logger.info(f"Completed page {current_page}. Total files downloaded so far: {total_files_downloaded}")
            
            # Mark page as completed
            if current_page not in progress.get('pages_completed', []):
                progress['pages_completed'].append(current_page)
                save_progress(progress)"""
        
        functions_code = functions_code.replace(old_page_complete, new_page_complete)
    
    # Add final batch processing before completion
    if "save_progress(progress)" in functions_code and "save_timing_data(timing_data)" in functions_code:
        old_final_save = """save_progress(progress)
    save_timing_data(timing_data)
    
    logger.info(f"\\n=== DOWNLOAD COMPLETE ===\")"""
        
        new_final_save = """# Process any remaining files in the final batch
    if current_batch_files:
        logger.info(f"\\n📦 Processing final batch of {len(current_batch_files)} files")
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
    
    logger.info(f"\\n=== DOWNLOAD COMPLETE ===\")"""
        
        functions_code = functions_code.replace(old_final_save, new_final_save)
    
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

# Batch processing variables
current_batch_files = []
batch_download_dir = os.path.join(SCRIPT_DIR, f"batch_downloads_script{script_id}")

# Ensure batch download directory exists
if not os.path.exists(batch_download_dir):
    os.makedirs(batch_download_dir)
    logger.info(f"Created batch download directory: {{batch_download_dir}}")


def cleanup_resources():
    \"\"\"Clean up browser resources for this script instance\"\"\"
    global driver
    try:
        if driver:
            logger.info(f"Cleaning up browser resources for Script {{SCRIPT_ID}}")
            driver.quit()
            driver = None
    except Exception as e:
        logger.warning(f"Error during cleanup: {{e}}")

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
        
        # Final cleanup and summary
        logger.info("\\n=== SCRIPT COMPLETION SUMMARY ===")
        logger.info(f"Total files processed: {{total_files_downloaded}}")
        if current_batch_files:
            logger.info(f"Files in final batch: {{len(current_batch_files)}}")
        
        # Check for any remaining files in batch directory
        remaining_files = []
        if os.path.exists(batch_download_dir):
            remaining_files = [f for f in os.listdir(batch_download_dir) if f.endswith('.pdf')]
            if remaining_files:
                logger.warning(f"⚠️  {{len(remaining_files)}} files remain in batch directory - may need manual upload")
        
        cleanup_resources()
        
    except KeyboardInterrupt:
        logger.info("\\\\nScript interrupted by user")
        
        # Process any pending batch files before exit
        if current_batch_files:
            logger.info("Processing pending batch files before exit...")
            try:
                process_batch_upload()
            except Exception as batch_error:
                logger.error(f"Error processing batch during interruption: {{batch_error}}")
        
        cleanup_resources()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {{str(e)}}")
        logger.error(traceback.format_exc())
        
        # Try to process any pending batch files before exit
        if current_batch_files:
            logger.info("Attempting to save pending batch files before exit...")
            try:
                process_batch_upload()
            except Exception as batch_error:
                logger.error(f"Error processing batch during error handling: {{batch_error}}")
        
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
