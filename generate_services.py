#!/usr/bin/env python3
"""
Generate systemd service files for scraping scripts
This script reads service_config.json and generates systemd service files
"""

import json
import os
import sys
from pathlib import Path

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

def generate_service_file(script_num, config):
    """Generate a systemd service file for a specific script"""
    
    working_dir = config['working_directory']
    python_path = config['python_path']
    user = config['user']
    restart_delay = config['restart_delay_seconds']
    
    service_content = f"""[Unit]
Description=Scraping Script {script_num} Service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
Environment="PYTHONUNBUFFERED=1"
ExecStart={python_path} {working_dir}/scripts/script{script_num}/script{script_num}.py
Restart=always
RestartSec={restart_delay}
StandardOutput=append:/var/log/scraping/script{script_num}.log
StandardError=append:/var/log/scraping/script{script_num}.error.log

# Resource limits (optional - uncomment and adjust as needed)
# MemoryLimit=2G
# CPUQuota=50%

[Install]
WantedBy=multi-user.target
"""
    return service_content

def main():
    """Main function to generate all service files"""
    
    config = load_config()
    
    # Create services directory
    services_dir = Path(__file__).parent / 'systemd_services'
    services_dir.mkdir(exist_ok=True)
    
    enabled_scripts = [s for s in config['scripts_to_run'] if s['enabled']]
    
    if not enabled_scripts:
        print("No scripts enabled in service_config.json!")
        print("Please edit service_config.json and set 'enabled': true for scripts you want to run")
        sys.exit(1)
    
    print(f"Generating service files for {len(enabled_scripts)} scripts...")
    print()
    
    generated_files = []
    
    for script in enabled_scripts:
        script_num = script['script_number']
        service_name = f"scraping-script{script_num}.service"
        service_file = services_dir / service_name
        
        service_content = generate_service_file(script_num, config)
        
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        generated_files.append(service_name)
        print(f"✓ Generated: {service_file}")
        print(f"  Description: {script['description']}")
    
    print()
    print("=" * 70)
    print("SERVICE FILES GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Next steps to install on your Debian VPS:")
    print()
    print("1. Create log directory:")
    print("   sudo mkdir -p /var/log/scraping")
    print(f"   sudo chown {config['user']}:{config['user']} /var/log/scraping")
    print()
    print("2. Copy service files to systemd:")
    print(f"   sudo cp systemd_services/*.service /etc/systemd/system/")
    print()
    print("3. Reload systemd:")
    print("   sudo systemctl daemon-reload")
    print()
    print("4. Enable services (to start on boot):")
    for service_name in generated_files:
        print(f"   sudo systemctl enable {service_name}")
    print()
    print("5. Start services:")
    for service_name in generated_files:
        print(f"   sudo systemctl start {service_name}")
    print()
    print("6. Check status:")
    for service_name in generated_files:
        print(f"   sudo systemctl status {service_name}")
    print()
    print("For easier management, use the provided management script:")
    print("   python3 manage_services.py status")
    print("   python3 manage_services.py start")
    print("   python3 manage_services.py stop")
    print("   python3 manage_services.py restart")
    print()

if __name__ == '__main__':
    main()
