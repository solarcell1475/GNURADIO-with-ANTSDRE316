# 🚀 450MHz SFCW Ground Penetrating Radar (GPR) System

A production-grade Stepped Frequency Continuous Wave (SFCW) Ground Penetrating Radar system operating at 450 MHz, integrating **GNU Radio**, **ANTSDR E316 SDR hardware**, **Claude Code AI agents**, and **real-time Streamlit visualization**.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Calibration](#calibration)
- [Project Structure](#project-structure)
- [Agent-Driven Development](#agent-driven-development)
- [Standards Compliance](#standards-compliance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements a complete Ground Penetrating Radar system designed for subsurface investigation up to 5 meters depth. The system uses:

- **SFCW Technique**: 400-500 MHz frequency sweep in 2 MHz steps (50 steps)
- **ANTSDR E316**: Single TX/RX SDR based on AD9364
- **GNU Radio**: Signal processing flowgraphs
- **Streamlit Dashboard**: Real-time A-scan and B-scan visualization
- **AI-Assisted Development**: Multi-agent orchestration using Claude Code and MGX.dev

### Key Specifications

| Parameter | Value |
|-----------|-------|
| Frequency Range | 400–500 MHz |
| Frequency Steps | 50 (2 MHz spacing) |
| Sample Rate | 10 MSPS |
| TX Power | -10 dBm (adjustable) |
| RX Gain | 60 dB (adjustable) |
| Dwell Time | 1 ms per step |
| Expected Penetration | ~5 meters (soil dependent) |
| Data Formats | HDF5, SEG-Y |

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code + MGX Agents                      │
│                    (Orchestration Layer)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│  GNU Radio    │    │  ANTSDR E316   │    │  Streamlit   │
│  Flowgraph    │◄──►│  (AD9364)      │◄──►│  Dashboard   │
│  (gr-mcp)     │    │  via IIO       │    │  (Real-time) │
└───────────────┘    └────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  Data Processing │
                    │  & Analysis      │
                    └──────────────────┘
```

## Features

### Hardware Control
- ✅ Automated ANTSDR E316 configuration via IIO
- ✅ Frequency sweep test (400-500 MHz)
- ✅ TX power and RX gain control
- ✅ GPS synchronization (MAX-M8Q)

### Signal Processing
- ✅ SFCW waveform generation
- ✅ Dechirping and matched filtering
- ✅ FFT-based range processing
- ✅ Time-zero correction
- ✅ Envelope detection (Hilbert transform)
- ✅ Automatic Gain Control (AGC)
- ✅ Bandpass filtering

### Visualization
- ✅ Real-time A-scan display (time & depth)
- ✅ B-scan radargram (heatmap)
- ✅ Target detection markers
- ✅ System health metrics (SNR, temperature, GPS)
- ✅ Interactive parameter controls

### Data Management
- ✅ HDF5 data storage with metadata
- ✅ SEG-Y export (geophysical standard)
- ✅ Session recording and replay
- ✅ GPS-tagged measurements

### Testing & Calibration
- ✅ ASTM D6432 compliance testing
- ✅ Calibration targets (0.5m, 1.0m, 2.0m)
- ✅ SNR and depth accuracy validation
- ✅ Automated test report generation

## Hardware Requirements

### Required
- **ANTSDR E316** (or compatible AD9364-based SDR)
  - Frequency range: 70 MHz - 6 GHz
  - Sample rate: up to 61.44 MSPS
  - Interface: Gigabit Ethernet (IIO)
  
- **Antennas**
  - TX/RX antennas for 450 MHz (e.g., dipoles, bow-tie)
  - Recommended: ~50 cm separation

- **Computer**
  - CPU: 4+ cores recommended
  - RAM: 8+ GB
  - OS: Linux (Ubuntu 22.04+), macOS, or Windows (WSL2)
  - Network: Gigabit Ethernet

### Optional
- GPS antenna (for positioning)
- Calibration targets (metal plates, pipes)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd GNURADIO
```

### 2. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y gnuradio gr-iio libiio-dev libiio-utils \
    python3-pip python3-venv build-essential
```

#### macOS
```bash
brew install gnuradio libiio python@3.11
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure ANTSDR Network
Set your ANTSDR E316 IP address (default: `192.168.1.10`):
```bash
# Test connection
ping 192.168.1.10

# Verify IIO access
iio_info -u ip:192.168.1.10
```

### 6. Install gr-mcp (Optional, for agent-driven control)
```bash
git clone https://github.com/yoelbassin/gr-mcp.git
cd gr-mcp
pip install -e .
```

## Quick Start

### 1. Test Hardware Connection
```bash
python src/hardware/antsdr_control.py
```

Expected output:
```
✅ Successfully connected to ANTSDR E316
✅ TX configuration complete
✅ RX configuration complete
✅ Frequency sweep complete: 50 steps
```

### 2. Run GNU Radio Flowgraph (Simulation)
```bash
python src/flowgraphs/sfcw_gpr_450mhz.py
```

### 3. Launch Dashboard
```bash
streamlit run src/dashboard/gpr_dashboard.py
```

Open browser to `http://localhost:8501`

### 4. Run Calibration Tests
```bash
python src/testing/run_calibration_tests.py --mode quick
```

## Usage

### Hardware Configuration

Edit hardware parameters in `src/hardware/antsdr_control.py` or via dashboard:

```python
from src.hardware.antsdr_control import ANTSDRController, ANTSDRConfig

config = ANTSDRConfig(
    ip_address="192.168.1.10",
    center_freq=450e6,      # 450 MHz
    tx_power=-10.0,         # dBm
    rx_gain=60.0,           # dB
    sample_rate=10e6        # 10 MSPS
)

controller = ANTSDRController(config)
controller.configure_all()
```

### Data Acquisition

#### Single Scan
```python
from src.flowgraphs.sfcw_gpr_450mhz import sfcw_gpr_450mhz

# Create flowgraph
tb = sfcw_gpr_450mhz(use_hardware=True)

# Run acquisition
tb.start()
time.sleep(5)  # 5 seconds
tb.stop()
tb.wait()

# Save data
tb.save_to_hdf5("scan_001.h5")
```

#### Continuous Survey
Use the Streamlit dashboard for real-time continuous surveys with B-scan visualization.

### Data Processing

```python
from src.analysis.process_ascan import GPRDataProcessor, GPRProcessingParams

# Configure processing
params = GPRProcessingParams(
    velocity=0.1,           # m/ns (soil)
    time_zero_offset=0.0,
    snr_threshold=10.0,
    apply_agc=True
)

processor = GPRDataProcessor(params)

# Load and process data
data = processor.load_hdf5("scan_001.h5")
processed, targets = processor.process_ascan(data['a_scans'][0], data['sample_rate'])

# Visualize
processor.plot_ascan(processed, data['sample_rate'], targets)
```

## Calibration

### Standard Procedure

1. **Prepare Calibration Targets**
   - Bury metal plates or pipes at known depths: 0.5m, 1.0m, 2.0m
   - Use homogeneous soil with known dielectric constant

2. **Run Calibration Tests**
   ```bash
   python src/testing/run_calibration_tests.py --mode full --hardware
   ```

3. **Review Report**
   - Check `docs/test_reports/calibration_report_*.json`
   - Verify depth accuracy within tolerance
   - Confirm SNR > 10 dB for all targets

4. **Adjust Parameters**
   - Update velocity based on measured depths
   - Adjust gain/power if SNR is low
   - Re-run tests until all pass

### Velocity Estimation

Velocity depends on soil dielectric constant (εᵣ):

```
v = c / √εᵣ

where:
  c = 3×10⁸ m/s (speed of light)
  εᵣ = dielectric constant
  
Common values:
  Air:        εᵣ = 1   → v = 0.30 m/ns
  Dry sand:   εᵣ = 4   → v = 0.15 m/ns
  Wet soil:   εᵣ = 16  → v = 0.075 m/ns
  Clay:       εᵣ = 25  → v = 0.06 m/ns
```

## Project Structure

```
GNURADIO/
├── .claude/
│   ├── agents/                    # Agent definitions
│   │   ├── gpr-project-manager.md
│   │   ├── antsdr-hardware-specialist.md
│   │   ├── gnuradio-architect.md
│   │   ├── gpr-data-analyst.md
│   │   ├── dashboard-builder.md
│   │   └── gpr-test-engineer.md
│   └── gpr_queue.txt              # Task queue
│
├── src/
│   ├── hardware/
│   │   ├── __init__.py
│   │   └── antsdr_control.py      # ANTSDR E316 control
│   │
│   ├── flowgraphs/
│   │   ├── __init__.py
│   │   └── sfcw_gpr_450mhz.py     # GNU Radio SFCW flowgraph
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── gpr_dashboard.py       # Streamlit dashboard
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── process_ascan.py       # Signal processing
│   │
│   └── testing/
│       ├── __init__.py
│       └── run_calibration_tests.py  # Calibration suite
│
├── config/
│   └── mcp.json                   # MCP server configuration
│
├── data/                          # Data storage (created at runtime)
│   └── gpr_survey/
│
├── docs/                          # Documentation
│   ├── test_reports/              # Test reports (created at runtime)
│   ├── calibration_procedures.md
│   └── user_manual.md
│
├── requirement.md                 # Original requirements
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Agent-Driven Development

This project uses **MGX.dev** and **Claude Code** for agent-driven development:

### Agents

1. **gpr-project-manager**: Orchestrates overall project
2. **antsdr-hardware-specialist**: Hardware configuration
3. **gnuradio-architect**: Flowgraph generation
4. **gpr-data-analyst**: Signal processing
5. **dashboard-builder**: UI development
6. **gpr-test-engineer**: Testing and validation

### Task Queue

See `.claude/gpr_queue.txt` for the development task sequence.

### MCP Integration

The project integrates with **gr-mcp** (GNU Radio MCP Server) for automated flowgraph generation and control.

Configuration: `config/mcp.json`

## Standards Compliance

### ASTM D6432
*Standard Guide for Using the Surface Ground Penetrating Radar Method for Subsurface Investigation*

- ✅ Equipment calibration procedures
- ✅ Data acquisition protocols
- ✅ Quality control measures
- ✅ Reporting standards

### SEG-Y v2.0
*Geophysical Data Exchange Format*

- ✅ Trace header format
- ✅ Binary header structure
- ✅ Coordinate reference systems

### IEEE GPR Standards
- ✅ Data exchange formats
- ✅ Metadata requirements

## Troubleshooting

### Hardware Connection Issues

**Problem**: Cannot connect to ANTSDR E316
```
❌ Failed to connect to ANTSDR E316
```

**Solutions**:
1. Verify device is powered on and connected via Ethernet
2. Check IP address: `ping 192.168.1.10`
3. Test IIO access: `iio_info -u ip:192.168.1.10`
4. Check firewall settings
5. Try different IP if device was reconfigured

### Low SNR

**Problem**: Detected targets have SNR < 10 dB

**Solutions**:
1. Increase RX gain (up to 70 dB)
2. Reduce noise: check antenna cables, grounding
3. Increase TX power (within regulatory limits)
4. Check antenna positioning and coupling
5. Verify frequency range is appropriate for target depth

### Depth Accuracy Issues

**Problem**: Measured depth differs from actual depth

**Solutions**:
1. Calibrate velocity using known targets
2. Adjust time-zero offset
3. Check dielectric constant of soil
4. Verify antenna separation is accounted for
5. Run calibration test suite

### Dashboard Not Loading

**Problem**: Streamlit dashboard shows errors

**Solutions**:
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check Python version: 3.9+ required
3. Clear Streamlit cache: `streamlit cache clear`
4. Check firewall: port 8501 must be open

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

## License

[Specify license - e.g., MIT, GPL, Apache 2.0]

## Acknowledgments

- **GNU Radio Project**: Signal processing framework
- **ANTSDR**: Open-source SDR hardware
- **Claude AI**: Agent-driven development
- **gr-mcp**: GNU Radio MCP integration

## Contact

[Add contact information or project maintainer details]

---

**Status**: ✅ Active Development  
**Version**: 1.0.0  
**Last Updated**: 2025-10-24

For detailed development instructions, see `requirement.md`.

