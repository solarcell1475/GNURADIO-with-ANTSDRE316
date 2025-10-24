# 450MHz SFCW GPR User Manual

## Quick Start Guide

### 1. Power On System

1. Connect ANTSDR E316 to power supply
2. Connect Ethernet cable from ANTSDR to computer
3. Wait 30 seconds for device to boot
4. Verify IP connectivity: `ping 192.168.1.10`

### 2. Launch Dashboard

```bash
cd /Users/solarcell1474/GNURADIO
source venv/bin/activate
streamlit run src/dashboard/gpr_dashboard.py
```

Open browser to: `http://localhost:8501`

### 3. Connect Hardware

1. In dashboard sidebar, click **"🔌 Connect"**
2. Wait for connection confirmation
3. Verify status indicators show green

### 4. Configure Parameters

**Hardware Settings**:
- Center Frequency: 450 MHz (recommended)
- TX Power: -10 dBm (safe default)
- RX Gain: 60 dB (adjust based on depth)

**Processing Settings**:
- Velocity: 0.10 m/ns (typical soil)
- SNR Threshold: 10 dB

### 5. Acquire Data

- **Single Scan**: Click "📸 Single Scan"
- **Continuous**: Click "▶️ Start"

### 6. Interpret Results

**A-Scan Display**:
- X-axis: Time (nanoseconds) or Depth (meters)
- Y-axis: Signal amplitude
- Red markers: Detected targets

**B-Scan Display**:
- X-axis: Survey distance (meters)
- Y-axis: Depth (meters)
- Grayscale: Signal strength

## Safety

### RF Safety

⚠️ **WARNING**: This device emits radio frequency energy.

- TX power: -10 dBm (0.1 mW) – very low, safe for operation
- Maintain 30 cm separation from antennas during transmission
- Do not touch antennas while transmitting
- Follow local RF exposure guidelines

### Frequency Allocation

- 450 MHz band may require licensing in some regions
- ISM band: 433-434.79 MHz (region-dependent)
- Amateur radio: 420-450 MHz (license required)
- Verify regulatory compliance before operation

### Electrical Safety

- Use only supplied power adapter
- Do not operate in wet conditions
- Protect equipment from moisture
- Disconnect power during antenna changes

## Field Operation

### Pre-Survey Checklist

- [ ] Equipment fully charged or powered
- [ ] GPS locked (if using positioning)
- [ ] Antennas connected and secured
- [ ] System calibrated (within last 30 days)
- [ ] Survey area marked and documented
- [ ] Weather conditions acceptable
- [ ] Safety equipment available

### Survey Procedure

1. **Mark Survey Lines**
   - Use string, chalk, or stakes
   - Typical spacing: 0.5m to 1.0m
   - Record GPS start/end points

2. **Position Equipment**
   - Place antennas on ground surface
   - Maintain constant height (±2 cm)
   - Antenna separation: 50 cm
   - Keep antennas parallel to surface

3. **Acquire Baseline**
   - Take reading in known "clear" area
   - Verify system noise and SNR
   - Document baseline characteristics

4. **Conduct Survey**
   - Move antennas along survey line
   - Trigger scan every 10-20 cm
   - Maintain consistent speed in continuous mode
   - Mark anomalies for re-scan

5. **Post-Survey**
   - Save all data files
   - Download GPS tracks
   - Photograph survey area
   - Document any observations

### Data Collection Best Practices

- **Antenna Coupling**: Ensure good contact with ground
- **Speed**: Move slowly (~0.5 m/s) for best results
- **Overlap**: Use 50% overlap between adjacent lines
- **Moisture**: Wet soil improves coupling but reduces penetration
- **Obstacles**: Avoid metal fences, power lines, vehicles

## Data Interpretation

### A-Scan Analysis

**Direct Wave** (0-5 ns):
- Coupling between TX and RX antennas
- Should be strong and consistent
- Indicates system health

**Ground Surface** (variable, typically 5-10 ns):
- Strong reflection from air-ground interface
- Used for time-zero calibration
- Amplitude depends on moisture content

**Subsurface Targets** (>10 ns):
- Hyperbolic or point reflections
- Depth calculated from two-way travel time
- SNR indicates target strength/size

### B-Scan Features

**Hyperbolas**:
- Point targets (pipes, rocks)
- Apex indicates target location
- Width indicates depth (wider = deeper)

**Horizontal Layers**:
- Soil strata or water table
- Continuous linear features
- Dielectric contrast boundaries

**Vertical Features**:
- Walls, foundations, trenches
- May show as disrupted layers
- Often with diffraction patterns

### Common Targets

| Target Type | Appearance | Depth Range | Notes |
|-------------|------------|-------------|-------|
| Metal pipe | Strong hyperbola | 0.5-3m | Very high reflectivity |
| Plastic pipe | Weak hyperbola | 0.5-2m | Requires high SNR |
| Concrete | Layer or hyperbola | 0.3-2m | Strong but dispersive |
| Voids (air) | Strong hyperbola | 0.5-3m | High dielectric contrast |
| Water table | Horizontal layer | Variable | Limits penetration |
| Rock | Point scatterers | Variable | Cluttered appearance |

## Maintenance

### Daily
- Inspect cables and connectors
- Check antenna condition
- Verify system boots correctly
- Test with known target (optional)

### Weekly
- Clean antennas (dry cloth only)
- Tighten all connectors
- Verify GPS operation
- Check cable strain reliefs

### Monthly
- Full system calibration
- Firmware/software updates
- Backup all data
- Review system logs

### Annual
- Professional inspection (recommended)
- Replace worn cables
- Verify against reference standards
- Update calibration certificate

## Troubleshooting

### Problem: No Connection to Hardware

**Symptoms**:
- Dashboard shows "Disconnected"
- `ping 192.168.1.10` fails

**Solutions**:
1. Check Ethernet cable connection
2. Verify ANTSDR is powered on
3. Check computer network settings:
   - IP: 192.168.1.x (not .10)
   - Subnet: 255.255.255.0
4. Disable WiFi (may interfere)
5. Try different Ethernet port
6. Reboot ANTSDR

### Problem: Low Signal Quality

**Symptoms**:
- SNR < 10 dB
- Noisy A-scans
- No target detection

**Solutions**:
1. Increase RX gain (60 → 70 dB)
2. Check antenna connections
3. Improve antenna-ground coupling
4. Reduce external interference:
   - Move away from power lines
   - Turn off nearby electronics
   - Avoid metal structures
5. Check soil conditions (very dry = poor coupling)
6. Verify TX is enabled and powered

### Problem: Incorrect Depth Measurements

**Symptoms**:
- Targets at wrong depth
- Inconsistent measurements

**Solutions**:
1. Recalibrate velocity:
   - Use known target
   - Adjust velocity parameter
   - Typical: 0.05-0.15 m/ns
2. Check time-zero setting
3. Verify antenna separation is accounted for
4. Consider soil layering (varying velocity)
5. Run calibration test suite

### Problem: Dashboard Not Updating

**Symptoms**:
- Frozen display
- Old data shown

**Solutions**:
1. Refresh browser (Cmd+R or F5)
2. Clear Streamlit cache: `streamlit cache clear`
3. Restart Streamlit server
4. Check Python process (shouldn't be consuming 100% CPU)
5. Update Streamlit: `pip install --upgrade streamlit`

### Problem: GPS Not Locking

**Symptoms**:
- GPS status shows "Searching"
- No position data

**Solutions**:
1. Ensure GPS antenna is connected
2. Move to location with clear sky view
3. Wait longer (first fix can take 5-10 minutes)
4. Check antenna cable for damage
5. Verify GPS is enabled in hardware config
6. Note: GPS not required for operation, only for positioning

## Appendix

### Keyboard Shortcuts (Dashboard)

- `Ctrl+S`: Save current scan
- `Space`: Trigger single scan (when focused)
- `Ctrl+R`: Refresh display

### File Formats

**HDF5** (`.h5`):
- Raw IQ data
- Processed A-scans
- Metadata and parameters
- GPS tracks
- Open with: Python (h5py), MATLAB, HDFView

**SEG-Y** (`.sgy`):
- Standard geophysical format
- Compatible with commercial GPR software
- Includes trace headers
- Open with: OpendTect, Petrel, GPR-SLICE

### Velocity Reference Table

| Material | εᵣ | Velocity (m/ns) |
|----------|-----|-----------------|
| Air | 1 | 0.300 |
| Ice | 3-4 | 0.160 |
| Dry sand | 3-5 | 0.150 |
| Wet sand | 10-30 | 0.060 |
| Limestone | 4-8 | 0.120 |
| Concrete | 6-12 | 0.100 |
| Dry clay | 2-6 | 0.130 |
| Wet clay | 15-40 | 0.050 |
| Granite | 4-6 | 0.130 |
| Freshwater | 80 | 0.033 |

### Contact Support

For technical support:
- Email: [support email]
- Documentation: [project URL]
- Issues: [GitHub/GitLab issues]

---

**Manual Version**: 1.0  
**Last Updated**: 2025-10-24  
**Compatible with**: System v1.0+

