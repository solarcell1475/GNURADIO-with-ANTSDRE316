# Software Installation for ANTSDR E316 on Xubuntu 22.04

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Installing libiio](#installing-libiio)
- [Installing GNU Radio](#installing-gnu-radio)
- [Installing gr-iio](#installing-gr-iio)
- [Installing Python Dependencies](#installing-python-dependencies)
- [Verification](#verification)
- [Optional Tools](#optional-tools)

---

## Prerequisites

### System Update

First, ensure your Xubuntu system is up to date:

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install basic build tools
sudo apt install -y build-essential git cmake pkg-config
```

### Check System Info

```bash
# Verify Ubuntu version
lsb_release -a
# Should show: Ubuntu 22.04.x LTS

# Check Python version
python3 --version
# Should show: Python 3.10.x or newer

# Check available memory
free -h
# Should have at least 2GB available
```

---

## Installing libiio

libiio is the Industrial I/O library for interfacing with the ANTSDR E316.

### Method 1: Install from Ubuntu Repository (Recommended)

```bash
# Install libiio packages
sudo apt install -y libiio-utils libiio0 libiio-dev

# Install Python bindings
sudo apt install -y python3-libiio

# Install IIO daemon (optional, for remote access)
sudo apt install -y iiod
```

### Verify Installation

```bash
# Check libiio version
iio_info --version

# Should output:
# Library version: 0.23 (git tag: v0.23)

# List available IIO tools
which iio_info iio_attr iio_readdev iio_writedev

# All should return paths like: /usr/bin/iio_info
```

### Method 2: Build from Source (Latest Version)

If you need the latest version:

```bash
# Install dependencies
sudo apt install -y libxml2-dev libserialport-dev libavahi-client-dev \
    libusb-1.0-0-dev libusb-dev python3-setuptools

# Clone libiio repository
cd ~/
git clone https://github.com/analogdevicesinc/libiio.git
cd libiio

# Checkout stable version
git checkout v0.25  # Or latest stable tag

# Build and install
mkdir build && cd build
cmake ../ -DPYTHON_BINDINGS=ON
make -j$(nproc)
sudo make install

# Update library cache
sudo ldconfig

# Verify
iio_info --version
```

### Test libiio with E316

```bash
# Connect to E316 (ensure network is configured)
iio_info -u ip:192.168.1.10

# Should list devices including ad9361-phy
# If successful, libiio is working! ✅
```

---

## Installing GNU Radio

GNU Radio is the signal processing framework we'll use.

### Method 1: Install from Ubuntu Repository

```bash
# Install GNU Radio
sudo apt install -y gnuradio

# Check version
gnuradio-config-info --version

# Should show version 3.10.x
```

### Install GNU Radio Companion (GUI)

```bash
# Install GUI components
sudo apt install -y gnuradio-dev python3-pyqt5

# Install additional blocks
sudo apt install -y gr-osmosdr gr-fosphor gr-radar
```

### Method 2: Install from PPA (Newer Version)

For the latest stable version:

```bash
# Add GNU Radio PPA
sudo add-apt-repository ppa:gnuradio/gnuradio-releases
sudo apt update

# Install GNU Radio
sudo apt install -y gnuradio

# Verify version
gnuradio-config-info --version
```

### Test GNU Radio Installation

```bash
# Test Python import
python3 -c "from gnuradio import gr; print('GNU Radio version:', gr.version())"

# Should print version without errors

# Launch GNU Radio Companion (GUI)
gnuradio-companion

# A window should open - close it if it does
```

---

## Installing gr-iio

gr-iio provides GNU Radio blocks for IIO devices like the ANTSDR E316.

### Install from Repository

```bash
# Install gr-iio
sudo apt install -y gr-iio

# Verify installation
python3 -c "from gnuradio import iio; print('gr-iio installed successfully')"
```

### Build from Source (If Repository Version Not Available)

```bash
# Install dependencies
sudo apt install -y libad9361-dev libiio-dev

# Clone gr-iio repository
cd ~/
git clone https://github.com/analogdevicesinc/gr-iio.git
cd gr-iio

# Build and install
mkdir build && cd build
cmake ../
make -j$(nproc)
sudo make install
sudo ldconfig

# Update GNU Radio block path
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

### Test gr-iio

```bash
# Test import
python3 << EOF
from gnuradio import iio
print("gr-iio blocks available:")
print("- fmcomms2_source")
print("- fmcomms2_sink")
print("gr-iio is working! ✅")
EOF
```

---

## Installing Python Dependencies

Install Python packages needed for the GPR project:

```bash
# Navigate to project directory
cd /path/to/GNURADIO

# Install from requirements.txt
pip3 install -r requirements.txt

# Or install manually:
pip3 install numpy scipy matplotlib h5py pandas streamlit plotly
```

### Verify Python Packages

```bash
# Test imports
python3 << EOF
import numpy as np
import scipy
import matplotlib.pyplot as plt
import h5py
import streamlit
import plotly
print("All Python packages installed successfully ✅")
print(f"NumPy version: {np.__version__}")
print(f"SciPy version: {scipy.__version__}")
EOF
```

---

## Verification

### Complete System Test

Run this comprehensive test script:

```bash
#!/bin/bash
# save as: test_installation.sh

echo "====================================="
echo "ANTSDR E316 Software Installation Test"
echo "====================================="

# Test 1: libiio
echo -e "\n[TEST 1] libiio"
if command -v iio_info &> /dev/null; then
    echo "✅ iio_info found: $(which iio_info)"
    iio_info --version | head -n 1
else
    echo "❌ iio_info not found"
fi

# Test 2: GNU Radio
echo -e "\n[TEST 2] GNU Radio"
if command -v gnuradio-config-info &> /dev/null; then
    echo "✅ GNU Radio found"
    gnuradio-config-info --version
else
    echo "❌ GNU Radio not found"
fi

# Test 3: Python GNU Radio
echo -e "\n[TEST 3] Python GNU Radio bindings"
python3 -c "from gnuradio import gr; print('✅ GNU Radio Python OK')" 2>/dev/null || echo "❌ GNU Radio Python FAIL"

# Test 4: gr-iio
echo -e "\n[TEST 4] gr-iio"
python3 -c "from gnuradio import iio; print('✅ gr-iio OK')" 2>/dev/null || echo "❌ gr-iio FAIL"

# Test 5: Python packages
echo -e "\n[TEST 5] Python packages"
python3 -c "import numpy, scipy, matplotlib, h5py; print('✅ Scientific Python OK')" 2>/dev/null || echo "❌ Scientific Python FAIL"

# Test 6: E316 connectivity (if connected)
echo -e "\n[TEST 6] E316 Connectivity"
if ping -c 1 -W 1 192.168.1.10 &> /dev/null; then
    echo "✅ E316 reachable at 192.168.1.10"
    echo "   Testing IIO connection..."
    if timeout 5 iio_info -u ip:192.168.1.10 &> /dev/null; then
        echo "✅ IIO connection successful"
    else
        echo "⚠️  Ping OK but IIO connection failed"
    fi
else
    echo "⚠️  E316 not reachable (may not be connected)"
fi

echo -e "\n====================================="
echo "Test Complete"
echo "====================================="
```

Make it executable and run:

```bash
chmod +x test_installation.sh
./test_installation.sh
```

### Expected Output

All tests should show ✅:
```
[TEST 1] libiio
✅ iio_info found: /usr/bin/iio_info
Library version: 0.23

[TEST 2] GNU Radio
✅ GNU Radio found
3.10.5.1

[TEST 3] Python GNU Radio bindings
✅ GNU Radio Python OK

[TEST 4] gr-iio
✅ gr-iio OK

[TEST 5] Python packages
✅ Scientific Python OK

[TEST 6] E316 Connectivity
✅ E316 reachable at 192.168.1.10
   Testing IIO connection...
✅ IIO connection successful
```

---

## Optional Tools

### 1. IIO Oscilloscope (GUI for IIO devices)

```bash
# Install IIO Oscilloscope
sudo apt install -y libiio-utils-extra iio-oscilloscope

# Launch (with E316 connected)
osc

# Or specify IP:
osc ip:192.168.1.10
```

### 2. GQRX (SDR Receiver GUI)

```bash
# Install GQRX
sudo apt install -y gqrx-sdr

# Launch
gqrx

# Configure for E316:
# - Device: "Other"
# - Device string: iio,uri=ip:192.168.1.10
```

### 3. SoapySDR (Alternative SDR Framework)

```bash
# Install SoapySDR
sudo apt install -y soapysdr-tools python3-soapysdr

# Install PlutoSDR module (works with E316)
sudo apt install -y soapysdr-module-plutosdr

# Test detection
SoapySDRUtil --find="driver=plutosdr"
```

### 4. Development Tools

```bash
# Install debugging tools
sudo apt install -y gdb valgrind wireshark

# Install documentation generators
sudo apt install -y doxygen graphviz

# Install code editors
sudo apt install -y vim-gtk3 geany code  # VS Code
```

### 5. Performance Monitoring Tools

```bash
# Install system monitors
sudo apt install -y htop iotop iftop nethogs

# Install profiling tools
sudo apt install -y linux-tools-common linux-tools-generic
```

---

## Configuration Files

### Create IIO Configuration

```bash
# Create IIO config directory
mkdir -p ~/.config/iio

# Create default context file
cat > ~/.config/iio/context.conf << 'EOF'
# Default IIO context for ANTSDR E316
[contexts]
e316 = ip:192.168.1.10
EOF
```

### Setup Environment Variables

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# ANTSDR E316 / GNU Radio Environment
export IIO_URI=ip:192.168.1.10
export GR_DONT_LOAD_PREFS=1  # Disable GNU Radio startup messages
export PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH

# Aliases for E316
alias e316-info='iio_info -u $IIO_URI'
alias e316-attr='iio_attr -u $IIO_URI'
alias e316-read='iio_readdev -u $IIO_URI'
alias e316-ping='ping 192.168.1.10'

EOF

# Reload bashrc
source ~/.bashrc
```

### Test Aliases

```bash
# Test new aliases (with E316 connected)
e316-ping
e316-info | head -n 20
```

---

## Troubleshooting Installation

### Problem: Package Not Found

```bash
# Solution: Update package list
sudo apt update

# If still not found, enable universe repository
sudo add-apt-repository universe
sudo apt update
```

### Problem: GNU Radio Import Fails

```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Reinstall GNU Radio Python bindings
sudo apt install --reinstall python3-gnuradio

# Or set PYTHONPATH manually
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
```

### Problem: libiio Build Fails

```bash
# Install all possible dependencies
sudo apt install -y cmake git libxml2-dev bison flex \
    libcdk5-dev libaio-dev libusb-1.0-0-dev libserialport-dev \
    libavahi-client-dev doxygen graphviz

# Try build again
cd ~/libiio/build
cmake ../ -DCMAKE_INSTALL_PREFIX=/usr/local
make clean
make -j$(nproc)
```

### Problem: Permission Denied for USB Devices

```bash
# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Create udev rule for PlutoSDR/E316
sudo bash -c 'cat > /etc/udev/rules.d/53-adi-plutosdr-usb.rules << EOF
# ANTSDR E316
SUBSYSTEM=="usb", ATTRS{idVendor}=="0456", ATTRS{idProduct}=="b673", MODE="0666"
EOF'

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Log out and back in for group changes
```

---

## Post-Installation Checklist

- [ ] libiio installed and `iio_info` works
- [ ] GNU Radio installed and `gnuradio-config-info` works
- [ ] gr-iio blocks importable in Python
- [ ] Python packages (numpy, scipy, etc.) installed
- [ ] Can connect to E316: `iio_info -u ip:192.168.1.10` works
- [ ] Environment variables set in `~/.bashrc`
- [ ] All tests in verification script pass

---

## Next Steps

✅ Once all software is installed, proceed to:
- **04_TESTING_PROCEDURES.md** - Run hardware and software tests
- **05_GPR_PROJECT_SETUP.md** - Configure and run the GPR project

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-24  
**Tested With**: Xubuntu 22.04 LTS, ANTSDR E316

