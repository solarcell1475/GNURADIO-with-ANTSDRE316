#!/usr/bin/env python3
"""
GPR Project Initialization Script
Performs initial setup, validation, and configuration
"""

import sys
import os
from pathlib import Path
import json
import subprocess
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_python_version():
    """Verify Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required Python packages are installed"""
    required = [
        'numpy',
        'scipy',
        'matplotlib',
        'h5py',
        'streamlit',
        'plotly',
        'pandas'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)
    
    return len(missing) == 0


def create_directories():
    """Create necessary project directories"""
    directories = [
        'data/gpr_survey',
        'data/calibration',
        'data/test_data',
        'docs/test_reports',
        'logs',
        'exports'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    return True


def create_config_file():
    """Create default configuration file"""
    config = {
        "project": {
            "name": "450MHz SFCW GPR",
            "version": "1.0.0",
            "created": datetime.now().isoformat()
        },
        "hardware": {
            "device": "ANTSDR E316",
            "ip_address": "192.168.1.10",
            "center_freq": 450e6,
            "tx_power": -10.0,
            "rx_gain": 60.0,
            "sample_rate": 10e6
        },
        "processing": {
            "velocity": 0.1,
            "time_zero_offset": 0.0,
            "filter_low": 100e6,
            "filter_high": 400e6,
            "snr_threshold": 10.0,
            "apply_agc": True
        },
        "acquisition": {
            "freq_start": 400e6,
            "freq_stop": 500e6,
            "freq_step": 2e6,
            "dwell_time": 1e-3
        }
    }
    
    config_path = Path("config/gpr_config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration file created: {config_path}")
    return True


def test_hardware_connection(ip_address="192.168.1.10"):
    """Test connection to ANTSDR hardware"""
    print(f"\nTesting connection to {ip_address}...")
    
    # Test ping
    try:
        result = subprocess.run(
            ['ping', '-c', '3', ip_address],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Hardware reachable at {ip_address}")
            return True
        else:
            print(f"⚠️  Hardware not reachable at {ip_address}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"⚠️  Could not test hardware connection")
        return False


def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/

# Data files
data/
*.h5
*.hdf5
*.dat
*.sgy
*.segy

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Exports
exports/
*.png
*.pdf
*.jpg

# Configuration (may contain sensitive info)
config/local_*.json

# Test reports
docs/test_reports/*.json
docs/test_reports/*.pdf
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✓ .gitignore created")
    return True


def display_summary():
    """Display project summary and next steps"""
    print("\n" + "=" * 60)
    print("✅ PROJECT INITIALIZATION COMPLETE")
    print("=" * 60)
    
    print("\nProject Structure:")
    print("  ├── .claude/agents/     - Agent definitions")
    print("  ├── src/                - Source code")
    print("  │   ├── hardware/       - Hardware control")
    print("  │   ├── flowgraphs/     - GNU Radio flowgraphs")
    print("  │   ├── dashboard/      - Streamlit dashboard")
    print("  │   ├── analysis/       - Signal processing")
    print("  │   └── testing/        - Calibration & tests")
    print("  ├── config/             - Configuration files")
    print("  ├── data/               - Data storage")
    print("  ├── docs/               - Documentation")
    print("  └── logs/               - Log files")
    
    print("\nQuick Start Commands:")
    print("  1. Test hardware:       python src/hardware/antsdr_control.py")
    print("  2. Launch dashboard:    streamlit run src/dashboard/gpr_dashboard.py")
    print("  3. Run calibration:     python src/testing/run_calibration_tests.py --mode quick")
    print("  4. Process data:        python src/analysis/process_ascan.py")
    
    print("\nConfiguration:")
    print("  - Hardware: config/gpr_config.json")
    print("  - MCP: config/mcp.json")
    
    print("\nDocumentation:")
    print("  - README.md              - Project overview")
    print("  - docs/user_manual.md    - Operation guide")
    print("  - docs/calibration_procedures.md - Calibration guide")
    
    print("\n" + "=" * 60)


def main():
    """Main initialization routine"""
    print_header("450MHz SFCW GPR - Project Initialization")
    
    print("\nChecking Python version...")
    if not check_python_version():
        sys.exit(1)
    
    print("\nChecking dependencies...")
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️  Some dependencies missing. Run: pip install -r requirements.txt")
    
    print("\nCreating project directories...")
    create_directories()
    
    print("\nCreating configuration files...")
    create_config_file()
    
    print("\nCreating .gitignore...")
    create_gitignore()
    
    # Optional hardware test
    response = input("\nTest hardware connection? (y/n): ").strip().lower()
    if response == 'y':
        test_hardware_connection()
    
    # Display summary
    display_summary()
    
    print("\n✨ Ready to start development!")
    print("   For help, run: python init_project.py --help")


if __name__ == "__main__":
    main()

