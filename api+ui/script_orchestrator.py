"""
Script Orchestrator - Manages multiple scraping scripts
Handles sequential startup, monitoring, and control of individual scripts
"""
import subprocess
import threading
import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScriptOrchestrator:
    def __init__(self, scripts_base_dir, instance_id=1):
        self.scripts_base_dir = Path(scripts_base_dir)
        self.instance_id = instance_id
        self.running_scripts = {}  # script_id -> process
        self.script_threads = {}   # script_id -> thread
        self.stop_flags = {}       # script_id -> stop_flag
        
        # Load instance script assignments
        assignments_file = self.scripts_base_dir.parent / "instance_script_assignments.json"
        with open(assignments_file, 'r') as f:
            assignments = json.load(f)
        
        self.assigned_scripts = assignments[f"instance{instance_id}"]["scripts"]
        logger.info(f"Orchestrator initialized for Instance {instance_id} with {len(self.assigned_scripts)} scripts")
    
    def get_script_status(self, script_id):
        """Get status of a specific script"""
        script_dir = self.scripts_base_dir / f"script{script_id}"
        progress_file = script_dir / f"script{script_id}_progress.json"
        
        try:
            if progress_file.exists():
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                
                # Check if process is running
                is_running = script_id in self.running_scripts and self.running_scripts[script_id].poll() is None
                progress['is_running'] = is_running
                
                return progress
            else:
                return {
                    "script_id": script_id,
                    "status": "not_initialized",
                    "is_running": False
                }
        except Exception as e:
            logger.error(f"Error reading script {script_id} status: {e}")
            return {
                "script_id": script_id,
                "status": "error",
                "error": str(e),
                "is_running": False
            }
    
    def get_all_scripts_status(self):
        """Get status of all assigned scripts"""
        statuses = []
        for script_id in self.assigned_scripts:
            status = self.get_script_status(script_id)
            statuses.append(status)
        return statuses
    
    def get_overall_status(self):
        """Get overall status of the instance"""
        statuses = self.get_all_scripts_status()
        
        total_downloaded = sum(s.get('total_files_downloaded', 0) for s in statuses)
        running_count = sum(1 for s in statuses if s.get('is_running', False))
        completed_count = sum(1 for s in statuses if s.get('status') == 'completed')
        error_count = sum(1 for s in statuses if s.get('status') == 'error')
        
        total_pages = sum(s.get('total_pages', 0) for s in statuses)
        completed_pages = sum(len(s.get('pages_completed', [])) for s in statuses)
        
        return {
            "instance_id": self.instance_id,
            "total_scripts": len(self.assigned_scripts),
            "running_scripts": running_count,
            "completed_scripts": completed_count,
            "error_scripts": error_count,
            "total_files_downloaded": total_downloaded,
            "total_pages": total_pages,
            "completed_pages": completed_pages,
            "progress_percentage": (completed_pages / total_pages * 100) if total_pages > 0 else 0,
            "scripts": statuses
        }
    
    def start_script(self, script_id):
        """Start a single script"""
        if script_id not in self.assigned_scripts:
            raise ValueError(f"Script {script_id} is not assigned to Instance {self.instance_id}")
        
        if script_id in self.running_scripts and self.running_scripts[script_id].poll() is None:
            logger.warning(f"Script {script_id} is already running")
            return False
        
        script_dir = self.scripts_base_dir / f"script{script_id}"
        script_file = script_dir / f"script{script_id}.py"
        
        if not script_file.exists():
            raise FileNotFoundError(f"Script file not found: {script_file}")
        
        try:
            # Start the script as a subprocess
            logger.info(f"Starting script {script_id}...")
            process = subprocess.Popen(
                ['python', str(script_file)],
                cwd=str(script_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_scripts[script_id] = process
            logger.info(f"Script {script_id} started successfully (PID: {process.pid})")
            
            return True
        except Exception as e:
            logger.error(f"Error starting script {script_id}: {e}")
            raise
    
    def start_scripts_sequential(self, script_ids, delay=2):
        """Start multiple scripts one by one with delay"""
        def start_sequential():
            for script_id in script_ids:
                try:
                    if script_id in self.assigned_scripts:
                        self.start_script(script_id)
                        logger.info(f"Waiting {delay} seconds before starting next script...")
                        time.sleep(delay)
                    else:
                        logger.warning(f"Skipping script {script_id} - not assigned to this instance")
                except Exception as e:
                    logger.error(f"Failed to start script {script_id}: {e}")
        
        thread = threading.Thread(target=start_sequential, daemon=True)
        thread.start()
        return True
    
    def start_n_scripts(self, n, delay=2):
        """Start first N scripts sequentially"""
        scripts_to_start = self.assigned_scripts[:n]
        logger.info(f"Starting {len(scripts_to_start)} scripts: {scripts_to_start}")
        return self.start_scripts_sequential(scripts_to_start, delay)
    
    def stop_script(self, script_id):
        """Stop a running script"""
        if script_id not in self.running_scripts:
            logger.warning(f"Script {script_id} is not running")
            return False
        
        try:
            process = self.running_scripts[script_id]
            if process.poll() is None:
                logger.info(f"Stopping script {script_id}...")
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
                logger.info(f"Script {script_id} stopped")
            
            del self.running_scripts[script_id]
            return True
        except Exception as e:
            logger.error(f"Error stopping script {script_id}: {e}")
            raise
    
    def stop_all_scripts(self):
        """Stop all running scripts"""
        script_ids = list(self.running_scripts.keys())
        for script_id in script_ids:
            try:
                self.stop_script(script_id)
            except Exception as e:
                logger.error(f"Error stopping script {script_id}: {e}")
        return True
    
    def get_script_logs(self, script_id, lines=50):
        """Get recent log lines from a script"""
        script_dir = self.scripts_base_dir / f"script{script_id}"
        log_file = script_dir / f"script{script_id}.log"
        
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
            else:
                return []
        except Exception as e:
            logger.error(f"Error reading logs for script {script_id}: {e}")
            return []

# Global orchestrator instance
orchestrator = None

def get_orchestrator(scripts_dir=None, instance_id=None):
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        if scripts_dir is None or instance_id is None:
            raise ValueError("Must provide scripts_dir and instance_id for first initialization")
        orchestrator = ScriptOrchestrator(scripts_dir, instance_id)
    return orchestrator

if __name__ == "__main__":
    # Test the orchestrator
    orch = ScriptOrchestrator("../scripts", instance_id=1)
    
    print("\n📊 Overall Status:")
    print(json.dumps(orch.get_overall_status(), indent=2))
    
    print("\n📝 Script 1 Status:")
    print(json.dumps(orch.get_script_status(1), indent=2))
