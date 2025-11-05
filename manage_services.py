#!/usr/bin/env python3
"""
Service Management Script
Helps manage all scraping services easily
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def load_config():
    """Load service configuration"""
    config_file = Path(__file__).parent / 'service_config.json'
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_file} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_file}: {e}")
        sys.exit(1)

def get_enabled_services():
    """Get list of enabled service names"""
    config = load_config()
    enabled_scripts = [s for s in config['scripts_to_run'] if s['enabled']]
    return [f"scraping-script{s['script_number']}.service" for s in enabled_scripts]

def run_command(command, capture_output=True):
    """Run a shell command"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)

def status_command():
    """Show status of all services"""
    services = get_enabled_services()
    
    print("=" * 80)
    print(f"SCRAPING SERVICES STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    for service in services:
        print(f"Service: {service}")
        print("-" * 80)
        returncode, stdout, stderr = run_command(f"systemctl status {service}")
        print(stdout)
        print()

def start_command():
    """Start all services"""
    services = get_enabled_services()
    
    print("Starting services...")
    print()
    
    for service in services:
        print(f"Starting {service}...", end=" ")
        returncode, stdout, stderr = run_command(f"sudo systemctl start {service}")
        if returncode == 0:
            print("✓ Started")
        else:
            print(f"✗ Failed: {stderr}")
    
    print()
    print("Checking status...")
    print()
    status_command()

def stop_command():
    """Stop all services"""
    services = get_enabled_services()
    
    print("Stopping services...")
    print()
    
    for service in services:
        print(f"Stopping {service}...", end=" ")
        returncode, stdout, stderr = run_command(f"sudo systemctl stop {service}")
        if returncode == 0:
            print("✓ Stopped")
        else:
            print(f"✗ Failed: {stderr}")

def restart_command():
    """Restart all services"""
    services = get_enabled_services()
    
    print("Restarting services...")
    print()
    
    for service in services:
        print(f"Restarting {service}...", end=" ")
        returncode, stdout, stderr = run_command(f"sudo systemctl restart {service}")
        if returncode == 0:
            print("✓ Restarted")
        else:
            print(f"✗ Failed: {stderr}")
    
    print()
    print("Checking status...")
    print()
    status_command()

def enable_command():
    """Enable all services (start on boot)"""
    services = get_enabled_services()
    
    print("Enabling services to start on boot...")
    print()
    
    for service in services:
        print(f"Enabling {service}...", end=" ")
        returncode, stdout, stderr = run_command(f"sudo systemctl enable {service}")
        if returncode == 0:
            print("✓ Enabled")
        else:
            print(f"✗ Failed: {stderr}")

def disable_command():
    """Disable all services (don't start on boot)"""
    services = get_enabled_services()
    
    print("Disabling services from starting on boot...")
    print()
    
    for service in services:
        print(f"Disabling {service}...", end=" ")
        returncode, stdout, stderr = run_command(f"sudo systemctl disable {service}")
        if returncode == 0:
            print("✓ Disabled")
        else:
            print(f"✗ Failed: {stderr}")

def logs_command(service_num=None, lines=50):
    """Show logs for a service"""
    if service_num:
        log_file = f"/var/log/scraping/script{service_num}.log"
        error_file = f"/var/log/scraping/script{service_num}.error.log"
        
        print(f"=== STDOUT LOG (last {lines} lines) ===")
        run_command(f"tail -n {lines} {log_file}", capture_output=False)
        print()
        print(f"=== STDERR LOG (last {lines} lines) ===")
        run_command(f"tail -n {lines} {error_file}", capture_output=False)
    else:
        services = get_enabled_services()
        for service in services:
            service_num = service.replace('scraping-script', '').replace('.service', '')
            print(f"=== LOGS FOR SCRIPT {service_num} ===")
            print()
            logs_command(service_num, lines=20)
            print()
            print("-" * 80)
            print()

def list_command():
    """List all configured services"""
    config = load_config()
    
    print("=" * 80)
    print("CONFIGURED SERVICES")
    print("=" * 80)
    print()
    
    for script in config['scripts_to_run']:
        status = "✓ ENABLED" if script['enabled'] else "✗ DISABLED"
        print(f"Script {script['script_number']}: {status}")
        print(f"  Description: {script['description']}")
        print()
    
    print(f"Python Path: {config['python_path']}")
    print(f"Working Directory: {config['working_directory']}")
    print(f"User: {config['user']}")
    print(f"Restart on Failure: {config['restart_on_failure']}")
    print(f"Restart Delay: {config['restart_delay_seconds']} seconds")

def print_usage():
    """Print usage information"""
    print("Scraping Services Management Script")
    print()
    print("Usage: python3 manage_services.py [command]")
    print()
    print("Commands:")
    print("  status          Show status of all services")
    print("  start           Start all services")
    print("  stop            Stop all services")
    print("  restart         Restart all services")
    print("  enable          Enable services to start on boot")
    print("  disable         Disable services from starting on boot")
    print("  logs [NUM]      Show logs (optionally for specific script number)")
    print("  list            List all configured services")
    print("  help            Show this help message")
    print()
    print("Examples:")
    print("  python3 manage_services.py status")
    print("  python3 manage_services.py start")
    print("  python3 manage_services.py logs 1")
    print("  python3 manage_services.py logs")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        status_command()
    elif command == 'start':
        start_command()
    elif command == 'stop':
        stop_command()
    elif command == 'restart':
        restart_command()
    elif command == 'enable':
        enable_command()
    elif command == 'disable':
        disable_command()
    elif command == 'logs':
        if len(sys.argv) > 2:
            logs_command(sys.argv[2])
        else:
            logs_command()
    elif command == 'list':
        list_command()
    elif command in ['help', '-h', '--help']:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print()
        print_usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
