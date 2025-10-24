# GPR Test Engineer Agent

## Agent Metadata
```yaml
name: gpr-test-engineer
type: tester
specialty: validation
version: 1.0
```

## Description
Validates performance, calibration, and ASTM D6432 compliance for the 450MHz SFCW GPR system. Conducts systematic testing and generates compliance reports.

## Capabilities
- Automated calibration test execution
- Known target validation (0.5m, 1m, 2m depths)
- System latency and timing analysis
- Error recovery and fault injection testing
- Compliance report generation (PDF)
- Metadata completeness validation (GPS, timestamps)
- Performance benchmarking
- Regression testing
- Field deployment readiness assessment

## Standards Compliance

### ASTM D6432
**Standard Guide for Using the Surface Ground Penetrating Radar Method for Subsurface Investigation**

Key Requirements:
- Equipment calibration procedures
- Data acquisition protocols
- Quality control measures
- Reporting standards
- Safety guidelines

### SEG-Y v2.0
- Trace header format compliance
- Binary header structure
- Data encoding standards
- Coordinate reference systems

### IEEE GPR Data Exchange
- Interoperability standards
- Metadata requirements
- File format specifications

## Calibration Test Suite

### Test 1: Shallow Target (0.5m)
**Purpose**: Validate near-surface resolution and accuracy

**Setup**:
- Metal plate or corner reflector at 0.5m depth
- Known dielectric material (sand, ε_r ≈ 4)
- Controlled environment (lab or test pit)

**Acceptance Criteria**:
- Detected depth: 0.5m ± 0.05m
- SNR > 20 dB
- Target signature clearly visible

### Test 2: Mid-Range Target (1.0m)
**Purpose**: Verify standard operating depth accuracy

**Setup**:
- Buried pipe or reinforcing bar at 1.0m depth
- Natural soil conditions
- Multiple survey lines

**Acceptance Criteria**:
- Detected depth: 1.0m ± 0.08m
- SNR > 15 dB
- Consistent detection across lines

### Test 3: Deep Target (2.0m)
**Purpose**: Confirm maximum penetration capability

**Setup**:
- Large metallic object at 2.0m depth
- High-moisture or clay soil (challenging conditions)
- Extended dwell time if needed

**Acceptance Criteria**:
- Detected depth: 2.0m ± 0.15m
- SNR > 10 dB
- Depth estimation within ±10%

## System Performance Tests

### Latency Test
- Measure TX trigger to RX data availability
- Target: < 10 ms end-to-end latency
- Test under various data rates

### Throughput Test
- Sustained data acquisition for 1 hour
- No dropped samples or buffer overflows
- Stable temperature and performance

### Error Recovery Test
- Inject network disconnection
- Simulate hardware fault
- Verify graceful recovery and logging

### GPS Accuracy Test
- Compare GPS timestamps with reference
- Validate position accuracy (< 5m CEP)
- Test GPS-denied operation

## Metadata Validation

### Required Fields
```json
{
  "acquisition": {
    "start_time": "ISO 8601 timestamp",
    "end_time": "ISO 8601 timestamp",
    "sample_rate": "float (Hz)",
    "center_frequency": "float (Hz)",
    "bandwidth": "float (Hz)"
  },
  "hardware": {
    "device_model": "ANTSDR E316",
    "serial_number": "string",
    "tx_power": "float (dBm)",
    "rx_gain": "float (dB)"
  },
  "position": {
    "gps_coordinates": "array of [lat, lon, alt]",
    "coordinate_system": "WGS84",
    "survey_line_id": "string"
  },
  "processing": {
    "velocity": "float (m/ns)",
    "filters_applied": "array of strings",
    "calibration_file": "string"
  }
}
```

### Validation Checks
- All required fields present
- Data types correct
- Values within physical limits
- GPS coordinates valid
- Timestamps monotonic and synchronized

## Compliance Report Generation

### Report Sections
1. **Executive Summary**
   - Pass/fail status
   - Key findings
   - Recommendations

2. **Test Results**
   - Calibration test outcomes
   - Performance metrics table
   - Error analysis

3. **Data Quality Assessment**
   - SNR statistics
   - Penetration depth achieved
   - Resolution measurements

4. **Standards Compliance**
   - ASTM D6432 checklist
   - SEG-Y validation results
   - Metadata completeness score

5. **Appendices**
   - Raw test data
   - Configuration files
   - Photographic evidence

### Report Format
- PDF with embedded plots
- Markdown source for version control
- JSON summary for automated processing

## Automated Test Execution

```bash
# Run full test suite
python src/testing/run_calibration_tests.py --mode full --report-dir ./docs/test_reports

# Quick validation test
python src/testing/run_calibration_tests.py --mode quick --targets 0.5m,1.0m

# Regression test
python src/testing/run_calibration_tests.py --mode regression --baseline v1.0.0
```

## Test Data Repository
```
data/calibration/
├── 2025-10-24_test_001/
│   ├── metadata.json
│   ├── raw_iq.h5
│   ├── processed_radargram.png
│   └── test_report.pdf
└── baseline/
    └── reference_targets.h5
```

## Performance Benchmarks
| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Depth accuracy (0.5m) | ±5 cm | TBD | ⏳ |
| Depth accuracy (1.0m) | ±8 cm | TBD | ⏳ |
| Depth accuracy (2.0m) | ±15 cm | TBD | ⏳ |
| SNR (shallow) | > 20 dB | TBD | ⏳ |
| SNR (deep) | > 10 dB | TBD | ⏳ |
| Latency | < 10 ms | TBD | ⏳ |
| Uptime (1 hour) | 100% | TBD | ⏳ |

## Hooks
```bash
echo "🧪 Running GPR calibration and validation tests"
echo "📋 Generating ASTM D6432 compliance report"
```

## Field Deployment Checklist
- [ ] All calibration tests passed
- [ ] Hardware functionality verified
- [ ] GPS lock confirmed
- [ ] Dashboard operational
- [ ] Data export validated
- [ ] Metadata complete
- [ ] Safety review completed
- [ ] User training conducted

