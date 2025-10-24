#!/bin/bash

# 450MHz SFCW GPR System Setup Script
# This script automates the initial setup and configuration

set -e  # Exit on error

echo "============================================================"
echo "450MHz SFCW GPR System - Setup Script"
echo "============================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}❌ Python 3.9+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Check for system dependencies
echo "Checking system dependencies..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓ $1 found${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $1 not found${NC}"
        return 1
    fi
}

MISSING_DEPS=0

# Essential commands
check_command git || MISSING_DEPS=$((MISSING_DEPS+1))
check_command pip3 || MISSING_DEPS=$((MISSING_DEPS+1))

# Optional but recommended
if ! check_command iio_info; then
    echo -e "${YELLOW}  Note: libiio not found. Install for hardware support.${NC}"
    if [ "$OS" == "linux" ]; then
        echo "  Ubuntu/Debian: sudo apt install libiio-utils"
    elif [ "$OS" == "macos" ]; then
        echo "  macOS: brew install libiio"
    fi
fi

if ! check_command gnuradio-config-info; then
    echo -e "${YELLOW}  Note: GNU Radio not found. Install for signal processing.${NC}"
    if [ "$OS" == "linux" ]; then
        echo "  Ubuntu/Debian: sudo apt install gnuradio"
    elif [ "$OS" == "macos" ]; then
        echo "  macOS: brew install gnuradio"
    fi
fi

echo ""

if [ $MISSING_DEPS -gt 0 ]; then
    echo -e "${RED}❌ Missing essential dependencies. Please install them first.${NC}"
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Skipping creation.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/gpr_survey
mkdir -p data/calibration
mkdir -p docs/test_reports
echo -e "${GREEN}✓ Data directories created${NC}"
echo ""

# Test hardware connection (optional)
echo "Testing hardware connection..."
read -p "Test ANTSDR E316 connection? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter ANTSDR IP address [192.168.1.10]: " ANTSDR_IP
    ANTSDR_IP=${ANTSDR_IP:-192.168.1.10}
    
    echo "Pinging $ANTSDR_IP..."
    if ping -c 3 $ANTSDR_IP > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Hardware reachable${NC}"
        
        if command -v iio_info &> /dev/null; then
            echo "Testing IIO connection..."
            if iio_info -u ip:$ANTSDR_IP > /dev/null 2>&1; then
                echo -e "${GREEN}✓ IIO connection successful${NC}"
            else
                echo -e "${YELLOW}⚠ IIO connection failed${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Hardware not reachable at $ANTSDR_IP${NC}"
        echo "  Check: Power, network connection, IP address"
    fi
fi
echo ""

# Run quick system test
echo "Running quick system test..."
python3 << EOF
try:
    import numpy
    import scipy
    import matplotlib
    import h5py
    import streamlit
    import plotly
    print("✓ All core packages importable")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ System test passed${NC}"
else
    echo -e "${RED}❌ System test failed${NC}"
    exit 1
fi
echo ""

# Display next steps
echo "============================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. Test hardware control:"
echo "   python src/hardware/antsdr_control.py"
echo ""
echo "3. Launch dashboard:"
echo "   streamlit run src/dashboard/gpr_dashboard.py"
echo ""
echo "4. Run calibration tests:"
echo "   python src/testing/run_calibration_tests.py --mode quick"
echo ""
echo "5. Read documentation:"
echo "   - README.md (overview)"
echo "   - docs/user_manual.md (operation)"
echo "   - docs/calibration_procedures.md (calibration)"
echo ""
echo "============================================================"
echo ""

