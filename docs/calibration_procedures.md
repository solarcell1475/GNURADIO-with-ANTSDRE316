# GPR Calibration Procedures

## Overview

This document describes the calibration procedures for the 450 MHz SFCW GPR system to ensure ASTM D6432 compliance and measurement accuracy.

## Required Equipment

### Calibration Targets
1. **Metal plates** (minimum 30×30 cm)
   - Aluminum or steel
   - Flat and smooth surface
   
2. **Burial depths**: 0.5m, 1.0m, 2.0m
   
3. **Soil conditions**
   - Homogeneous (uniform composition)
   - Known or measurable dielectric constant
   - Documented moisture content

### Measurement Tools
- Measuring tape or rod (accurate to ±1 cm)
- Soil moisture meter
- Temperature sensor
- GPS receiver
- Digital camera (for documentation)

## Pre-Calibration Checklist

- [ ] ANTSDR E316 connected and configured
- [ ] GPS locked (if available)
- [ ] Antennas properly positioned (50 cm separation)
- [ ] System warmed up (15 minutes minimum)
- [ ] Test site prepared and marked
- [ ] Weather conditions documented
- [ ] Soil temperature and moisture measured

## Procedure

### 1. System Initialization

```bash
# Connect to hardware
python src/hardware/antsdr_control.py

# Verify configuration
# - Center frequency: 450 MHz
# - TX power: -10 dBm
# - RX gain: 60 dB
# - Sample rate: 10 MSPS
```

### 2. Shallow Target (0.5m)

**Setup**:
1. Bury metal plate horizontally at 0.5m depth
2. Ensure soil is well compacted above plate
3. Mark surface location with high precision
4. Allow soil to settle (30 minutes minimum)

**Acquisition**:
```bash
# Single scan at target location
python src/flowgraphs/sfcw_gpr_450mhz.py --output calibration_050m.h5
```

**Acceptance Criteria**:
- Measured depth: 0.5m ± 0.05m (±10%)
- SNR > 20 dB
- Clear target signature visible

### 3. Mid-Range Target (1.0m)

**Setup**:
1. Bury metal plate horizontally at 1.0m depth
2. Same precautions as shallow target
3. Consider using larger plate if available

**Acquisition**:
```bash
python src/flowgraphs/sfcw_gpr_450mhz.py --output calibration_100m.h5
```

**Acceptance Criteria**:
- Measured depth: 1.0m ± 0.08m (±8%)
- SNR > 15 dB
- Consistent detection across survey line

### 4. Deep Target (2.0m)

**Setup**:
1. Bury large metal object or plate at 2.0m depth
2. May require excavation equipment
3. Critical: accurate depth measurement

**Acquisition**:
```bash
python src/flowgraphs/sfcw_gpr_450mhz.py --output calibration_200m.h5
```

**Acceptance Criteria**:
- Measured depth: 2.0m ± 0.15m (±7.5%)
- SNR > 10 dB
- Depth estimation within specification

### 5. Velocity Calibration

Using the measured target depths and two-way travel times, calculate propagation velocity:

```
v = 2 × d / t

where:
  v = velocity (m/s)
  d = actual depth (m)
  t = two-way travel time (s)
```

Average velocity across all three targets should be consistent (within ±5%).

**Velocity Adjustment**:
```python
# In src/analysis/process_ascan.py
params = GPRProcessingParams(
    velocity=<calculated_velocity>,  # Update this value
    ...
)
```

### 6. Automated Test Suite

Run comprehensive calibration:

```bash
python src/testing/run_calibration_tests.py --mode full --hardware
```

Review generated report in `docs/test_reports/`.

## Verification

### Data Quality Checks

1. **SNR Requirements**
   - All targets: SNR > 10 dB
   - Shallow target: SNR > 20 dB preferred

2. **Depth Accuracy**
   - 0.5m: ±5 cm
   - 1.0m: ±8 cm
   - 2.0m: ±15 cm

3. **Repeatability**
   - Conduct 3 measurements per target
   - Standard deviation < 3 cm

### System Health Checks

1. **Temperature Stability**
   - Monitor ANTSDR temperature
   - Should not exceed 70°C
   - Allow cooling if necessary

2. **GPS Lock**
   - Verify GPS coordinates for each measurement
   - Accuracy < 5m CEP

3. **Power Supply**
   - Check voltage stability
   - Ensure no brownouts during acquisition

## Documentation

### Required Records

1. **Calibration Certificate**
   - Date and time
   - Target depths (actual vs measured)
   - Calculated velocity
   - SNR for each target
   - Pass/fail status
   - Operator signature

2. **Environmental Data**
   - Soil type and moisture content
   - Temperature (air and soil)
   - Weather conditions
   - GPS coordinates

3. **System Configuration**
   - Hardware serial numbers
   - Software versions
   - Parameter settings
   - Antenna specifications

### Report Template

```
CALIBRATION REPORT
Date: [YYYY-MM-DD]
Operator: [Name]
Location: [GPS or description]

SYSTEM CONFIGURATION
- Hardware: ANTSDR E316 S/N [...]
- Frequency: 400-500 MHz (50 steps)
- TX Power: -10 dBm
- RX Gain: 60 dB

ENVIRONMENTAL CONDITIONS
- Soil Type: [...]
- Soil Moisture: [%]
- Temperature: [°C]
- Weather: [...]

CALIBRATION RESULTS
Target 1 (0.5m):
  Actual Depth: 0.500 m
  Measured Depth: [x.xxx] m
  Error: [±x.xxx] m ([±x.x%])
  SNR: [xx.x] dB
  Status: [PASS/FAIL]

[Repeat for 1.0m and 2.0m]

CALCULATED VELOCITY
  v = [x.xxx] m/ns
  (εᵣ ≈ [x.x])

OVERALL STATUS: [PASS/FAIL]

Signature: _______________
```

## Recalibration Schedule

### Periodic Recalibration
- **Daily**: Quick SNR check (5 minutes)
- **Weekly**: Single target verification (0.5m or 1.0m)
- **Monthly**: Full 3-target calibration
- **Annual**: Complete system validation with external standards

### Event-Based Recalibration
Recalibrate immediately after:
- Hardware replacement or repair
- Antenna changes
- Firmware/software updates
- Extreme temperature exposure
- Physical damage or suspected misalignment

## Troubleshooting

### Low SNR
1. Increase RX gain (up to 70 dB)
2. Check antenna connections
3. Verify target is metallic and sufficient size
4. Reduce noise sources (turn off nearby electronics)

### Depth Inaccuracy
1. Verify target depth measurement (use ruler/rod)
2. Recalculate velocity with multiple targets
3. Check soil uniformity (avoid layered soils)
4. Adjust time-zero offset

### No Target Detection
1. Confirm target is at expected depth
2. Increase TX power (within limits)
3. Check dwell time (may need longer integration)
4. Verify antenna orientation

## ASTM D6432 Compliance

This calibration procedure addresses the following ASTM D6432 requirements:

- **Section 8.1**: Equipment calibration before field use
- **Section 8.2**: Velocity determination using known targets
- **Section 9**: Quality control measures
- **Section 10**: Data interpretation and reporting

## References

1. ASTM D6432-19: Standard Guide for Using the Surface Ground Penetrating Radar Method for Subsurface Investigation
2. IEEE Std 1502-2020: Recommended Practice for Radar Cross-Section Test Procedures
3. ANTSDR E316 User Manual
4. GNU Radio Documentation

---

**Revision**: 1.0  
**Date**: 2025-10-24  
**Next Review**: 2026-10-24

