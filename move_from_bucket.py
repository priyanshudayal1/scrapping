"""
Script to move PDF files from ap-south-1 bucket (s3-vector-storage) 
to us-east-1 bucket (judgements-vectors-pdf)

Source: s3://s3-vector-storage/judgements-test-final/{script_number}/{filename}
Destination: s3://judgements-vectors-pdf/judgments/{script_number}/{filename}
"""

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging
from datetime import datetime
import json
from typing import Dict, List, Tuple
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bucket_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
SOURCE_BUCKET = 's3-vector-storage'
SOURCE_REGION = 'ap-south-1'
SOURCE_PREFIX = 'judgements-test-final/'

DESTINATION_BUCKET = 'judgements-vectors-pdf'
DESTINATION_REGION = 'us-east-1'
DESTINATION_PREFIX = 'judgments/'

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Progress tracking file
PROGRESS_FILE = 'migration_progress.json'


class S3Migrator:
    """Class to handle S3 bucket migration"""
    
    def __init__(self):
        """Initialize S3 clients for source and destination regions"""
        self.source_s3 = boto3.client(
            's3',
            region_name=SOURCE_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        
        self.dest_s3 = boto3.client(
            's3',
            region_name=DESTINATION_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        
        self.stats = {
            'total_files': 0,
            'copied': 0,
            'skipped': 0,
            'failed': 0,
            'total_size_mb': 0,
            'start_time': None,
            'end_time': None,
            'failed_files': []
        }
        
        # Load existing progress
        self.processed_files = self._load_progress()
    
    def _load_progress(self) -> set:
        """Load previously processed files from progress file"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_files', []))
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        return set()
    
    def _save_progress(self):
        """Save current progress to file"""
        try:
            progress_data = {
                'processed_files': list(self.processed_files),
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def list_all_pdf_files(self) -> List[Dict]:
        """List all PDF files from source bucket"""
        logger.info(f"Listing PDF files from s3://{SOURCE_BUCKET}/{SOURCE_PREFIX}")
        pdf_files = []
        
        try:
            paginator = self.source_s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=SOURCE_BUCKET,
                Prefix=SOURCE_PREFIX
            )
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # Only process PDF files
                        if key.lower().endswith('.pdf'):
                            pdf_files.append({
                                'key': key,
                                'size': obj['Size'],
                                'last_modified': obj['LastModified']
                            })
            
            logger.info(f"Found {len(pdf_files)} PDF files")
            return pdf_files
            
        except ClientError as e:
            logger.error(f"Error listing files from source bucket: {e}")
            raise
    
    def check_file_exists(self, dest_key: str) -> bool:
        """Check if file already exists in destination bucket"""
        try:
            self.dest_s3.head_object(Bucket=DESTINATION_BUCKET, Key=dest_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking file existence: {e}")
                raise
    
    def copy_file(self, source_key: str, dest_key: str, file_size: int) -> bool:
        """Copy a file from source to destination bucket"""
        try:
            copy_source = {
                'Bucket': SOURCE_BUCKET,
                'Key': source_key
            }
            
            # Use multipart copy for files larger than 5GB
            if file_size > 5 * 1024 * 1024 * 1024:  # 5GB
                logger.info(f"Using multipart copy for large file: {source_key}")
            
            self.dest_s3.copy_object(
                CopySource=copy_source,
                Bucket=DESTINATION_BUCKET,
                Key=dest_key,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully copied: {source_key} -> {dest_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to copy {source_key}: {e}")
            return False
    
    def delete_source_file(self, source_key: str) -> bool:
        """Delete file from source bucket after successful copy"""
        try:
            self.source_s3.delete_object(
                Bucket=SOURCE_BUCKET,
                Key=source_key
            )
            logger.info(f"Deleted source file: {source_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete source file {source_key}: {e}")
            return False
    
    def convert_path(self, source_key: str) -> str:
        """
        Convert source path to destination path
        Source: judgements-test-final/03/filename.pdf
        Destination: judgments/filename.pdf (without script number directory)
        """
        # Remove source prefix
        relative_path = source_key.replace(SOURCE_PREFIX, '', 1)
        
        # Extract just the filename (remove script number directory like 01/, 02/, etc.)
        # relative_path is like "03/filename.pdf", we want just "filename.pdf"
        parts = relative_path.split('/')
        if len(parts) > 1:
            filename = parts[-1]  # Get the last part (filename)
        else:
            filename = relative_path
        
        # Add destination prefix directly to filename
        dest_key = DESTINATION_PREFIX + filename
        
        return dest_key
    
    def migrate_files(self, delete_source: bool = False, skip_existing: bool = True):
        """
        Main migration function
        
        Args:
            delete_source: Whether to delete files from source after successful copy
            skip_existing: Whether to skip files that already exist in destination
        """
        logger.info("=" * 80)
        logger.info("Starting S3 Migration")
        logger.info(f"Source: s3://{SOURCE_BUCKET}/{SOURCE_PREFIX} (Region: {SOURCE_REGION})")
        logger.info(f"Destination: s3://{DESTINATION_BUCKET}/{DESTINATION_PREFIX} (Region: {DESTINATION_REGION})")
        logger.info(f"Delete source after copy: {delete_source}")
        logger.info(f"Skip existing files: {skip_existing}")
        logger.info("=" * 80)
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        # List all PDF files
        pdf_files = self.list_all_pdf_files()
        self.stats['total_files'] = len(pdf_files)
        
        if not pdf_files:
            logger.warning("No PDF files found to migrate")
            return
        
        # Calculate total size
        total_size_bytes = sum(f['size'] for f in pdf_files)
        self.stats['total_size_mb'] = round(total_size_bytes / (1024 * 1024), 2)
        logger.info(f"Total size to migrate: {self.stats['total_size_mb']} MB")
        
        # Process each file
        for idx, file_info in enumerate(pdf_files, 1):
            source_key = file_info['key']
            dest_key = self.convert_path(source_key)
            file_size = file_info['size']
            
            logger.info(f"\nProcessing [{idx}/{self.stats['total_files']}]: {source_key}")
            
            # Skip if already processed
            if source_key in self.processed_files:
                logger.info(f"Already processed, skipping: {source_key}")
                self.stats['skipped'] += 1
                continue
            
            # Check if file exists in destination
            if skip_existing and self.check_file_exists(dest_key):
                logger.info(f"File already exists in destination, skipping: {dest_key}")
                self.stats['skipped'] += 1
                self.processed_files.add(source_key)
                continue
            
            # Copy file
            success = self.copy_file(source_key, dest_key, file_size)
            
            if success:
                self.stats['copied'] += 1
                self.processed_files.add(source_key)
                
                # Delete source file if requested
                if delete_source:
                    self.delete_source_file(source_key)
            else:
                self.stats['failed'] += 1
                self.stats['failed_files'].append({
                    'source': source_key,
                    'destination': dest_key,
                    'error': 'Copy failed'
                })
            
            # Save progress every 10 files
            if idx % 10 == 0:
                self._save_progress()
                self._print_progress()
            
            # Rate limiting - small delay to avoid throttling
            time.sleep(0.1)
        
        # Final progress save
        self._save_progress()
        
        self.stats['end_time'] = datetime.now().isoformat()
        self._print_final_report()
    
    def _print_progress(self):
        """Print current progress"""
        logger.info(f"\n--- Progress Update ---")
        logger.info(f"Total: {self.stats['total_files']} | "
                   f"Copied: {self.stats['copied']} | "
                   f"Skipped: {self.stats['skipped']} | "
                   f"Failed: {self.stats['failed']}")
    
    def _print_final_report(self):
        """Print final migration report"""
        logger.info("\n" + "=" * 80)
        logger.info("MIGRATION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Total files found: {self.stats['total_files']}")
        logger.info(f"Successfully copied: {self.stats['copied']}")
        logger.info(f"Skipped (already exist): {self.stats['skipped']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Total size migrated: {self.stats['total_size_mb']} MB")
        logger.info(f"Start time: {self.stats['start_time']}")
        logger.info(f"End time: {self.stats['end_time']}")
        
        if self.stats['failed_files']:
            logger.error("\nFailed Files:")
            for failed in self.stats['failed_files']:
                logger.error(f"  - {failed['source']} -> {failed['destination']}")
        
        logger.info("=" * 80)
        logger.info(f"Progress saved to: {PROGRESS_FILE}")
        logger.info(f"Log file: bucket_migration.log")
        logger.info("=" * 80)


def verify_credentials():
    """Verify AWS credentials are configured"""
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        logger.error("AWS credentials not found in .env file")
        logger.error("Please ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set")
        return False
    return True


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("S3 BUCKET MIGRATION TOOL")
    print("=" * 80)
    print(f"Source: s3://{SOURCE_BUCKET}/{SOURCE_PREFIX} (ap-south-1)")
    print(f"Destination: s3://{DESTINATION_BUCKET}/{DESTINATION_PREFIX} (us-east-1)")
    print("=" * 80)
    
    # Verify credentials
    if not verify_credentials():
        return
    
    # Ask user for confirmation
    print("\nOptions:")
    print("1. Copy files (keep source files)")
    print("2. Move files (delete source after copy)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '3':
        print("Exiting...")
        return
    
    delete_source = (choice == '2')
    
    # Confirm action
    action = "MOVE" if delete_source else "COPY"
    print(f"\nYou are about to {action} PDF files from:")
    print(f"  Source: s3://{SOURCE_BUCKET}/{SOURCE_PREFIX}")
    print(f"  Destination: s3://{DESTINATION_BUCKET}/{DESTINATION_PREFIX}")
    
    confirm = input(f"\nAre you sure you want to proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        # Create migrator and start migration
        migrator = S3Migrator()
        migrator.migrate_files(delete_source=delete_source, skip_existing=True)
        
        print("\n✓ Migration completed successfully!")
        print(f"Check '{PROGRESS_FILE}' for details")
        print(f"Check 'bucket_migration.log' for full logs")
        
    except Exception as e:
        logger.error(f"Migration failed with error: {e}", exc_info=True)
        print(f"\n✗ Migration failed: {e}")
        print("Check 'bucket_migration.log' for details")


if __name__ == "__main__":
    main()
