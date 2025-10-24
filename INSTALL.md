# Installation Guide

## System Requirements

### Minimum Requirements
- **CPU**: 4+ cores (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **OS**: Ubuntu 22.04+, macOS 12+, or Windows 11 (with WSL2)
- **Network**: Gigabit Ethernet (for ANTSDR)
- **Python**: 3.9 or newer

### Recommended Requirements
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7 or better)
- **RAM**: 16 GB
- **Storage**: 50 GB free space (for data collection)
- **GPU**: Optional, for accelerated processing

## Installation Steps

### 1. Install System Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install build essentials
sudo apt install -y build-essential git cmake pkg-config

# Install GNU Radio and dependencies
sudo apt install -y gnuradio gr-iio

# Install libiio for ANTSDR
sudo apt install -y libiio-dev libiio-utils python3-libiio

# Install Python development headers
sudo apt install -y python3-dev python3-pip python3-venv

# Install optional dependencies
sudo apt install -y libfftw3-dev libvolk2-dev
```

#### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 git cmake pkg-config

# Install GNU Radio
brew install gnuradio

# Install libiio
brew install libiio

# Install FFTW (optional, for performance)
brew install fftw
```

#### Windows (WSL2)

1. Install WSL2 with Ubuntu 22.04:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. Open WSL2 terminal and follow Ubuntu instructions above

3. For hardware access, install usbipd:
   ```powershell
   winget install usbipd
   ```

### 2. Clone Repository

```bash
git clone <repository-url>
cd GNURADIO
```

### 3. Run Setup Script

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

The setup script will:
- Check Python version
- Create virtual environment
- Install Python dependencies
- Create data directories
- Test hardware connection (optional)

### 4. Manual Installation (Alternative)

If the setup script doesn't work, install manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install -r requirements.txt

# Create directories
mkdir -p data/gpr_survey data/calibration docs/test_reports
```

### 5. Initialize Project

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run initialization script
python init_project.py
```

This creates:
- Configuration files
- Data directories
- .gitignore
- Project structure

### 6. Configure Hardware

#### ANTSDR E316 Network Setup

1. Connect ANTSDR to computer via Ethernet

2. Configure network interface:

**Linux:**
```bash
# Set static IP
sudo nmcli con add type ethernet ifname eth0 con-name antsdr ip4 192.168.1.100/24

# Or use network manager GUI
```

**macOS:**
```
System Preferences → Network → Ethernet → Configure IPv4: Manually
  IP Address: 192.168.1.100
  Subnet Mask: 255.255.255.0
```

**Windows:**
```
Control Panel → Network → Ethernet → Properties → IPv4 → Manual
  IP Address: 192.168.1.100
  Subnet Mask: 255.255.255.0
```

3. Test connection:
```bash
ping 192.168.1.10
```

4. Verify IIO access:
```bash
iio_info -u ip:192.168.1.10
```

Expected output should show `ad9364-phy` device.

### 7. Verify Installation

```bash
# Test imports
python3 << EOF
import numpy
import scipy
import matplotlib
import streamlit
import plotly
import h5py
print("✓ All packages imported successfully")
EOF

# Test hardware control (simulation mode)
python src/hardware/antsdr_control.py

# Test signal processing
python src/analysis/process_ascan.py

# Test calibration suite
python src/testing/run_calibration_tests.py --mode quick
```

### 8. Launch Dashboard

```bash
streamlit run src/dashboard/gpr_dashboard.py
```

Open browser to: http://localhost:8501

## Optional Components

### gr-mcp (for Agent-Driven Control)

```bash
git clone https://github.com/yoelbassin/gr-mcp.git
cd gr-mcp
pip install -e .
```

Update `config/mcp.json` with correct path.

### GPS Support (if using positioning)

```bash
# Linux
sudo apt install gpsd python3-gps

# macOS
brew install gpsd
pip install gpsd-py3
```

### SEG-Y Export

```bash
pip install segysak obspy
```

### Documentation Generation

```bash
pip install sphinx sphinx-rtd-theme
cd docs
sphinx-quickstart
make html
```

## Troubleshooting

### GNU Radio Not Found

**Problem**: `gnuradio-config-info` not found

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install gnuradio

# macOS
brew install gnuradio

# Verify installation
gnuradio-config-info --version
```

### libiio Not Found

**Problem**: Cannot connect to ANTSDR

**Solution**:
```bash
# Install libiio
# Ubuntu/Debian
sudo apt install libiio-utils libiio-dev

# macOS
brew install libiio

# Test
iio_info -u ip:192.168.1.10
```

### Python Package Installation Fails

**Problem**: pip install errors

**Solutions**:

1. Update pip:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. Install system dependencies first (see step 1)

3. Install packages one by one to isolate issue:
   ```bash
   pip install numpy scipy matplotlib
   pip install streamlit plotly pandas
   pip install h5py
   ```

4. Check Python version:
   ```bash
   python3 --version  # Should be 3.9+
   ```

### Virtual Environment Issues

**Problem**: Cannot activate venv

**Solution**:
```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

**Problem**: Permission denied errors

**Solution**:
```bash
# Don't use sudo with pip in venv
# If needed, fix ownership:
sudo chown -R $USER:$USER ~/GNURADIO
```

### Network Connection Issues

**Problem**: Cannot reach ANTSDR at 192.168.1.10

**Solutions**:

1. Verify device is powered on
2. Check Ethernet cable
3. Disable WiFi (may conflict)
4. Check firewall settings
5. Verify IP configuration:
   ```bash
   ip addr show  # Linux
   ifconfig      # macOS
   ipconfig      # Windows
   ```

6. Try direct connection (no switch/router)

## Post-Installation

### Update Configuration

Edit `config/gpr_config.json` to match your setup:
- Hardware IP address
- Frequency range
- Processing parameters

### Run Tests

```bash
# Quick system check
python src/testing/run_calibration_tests.py --mode quick

# Full test suite (requires hardware)
python src/testing/run_calibration_tests.py --mode full --hardware
```

### Read Documentation

- `README.md` - Project overview
- `docs/user_manual.md` - Operation guide
- `docs/calibration_procedures.md` - Calibration procedures

### Join Community

[Add links to project discussions, issues, etc.]

## Uninstallation

To completely remove the project:

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf GNURADIO

# Optional: Remove system packages
# Ubuntu/Debian:
sudo apt remove gnuradio gr-iio libiio-dev

# macOS:
brew uninstall gnuradio libiio
```

## Getting Help

If you encounter issues:

1. Check troubleshooting section above
2. Review logs in `logs/` directory
3. Check system compatibility
4. Open issue on project repository
5. Contact support (see README.md)

---

**Last Updated**: 2025-10-24  
**Version**: 1.0

