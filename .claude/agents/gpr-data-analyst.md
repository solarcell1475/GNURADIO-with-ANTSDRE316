# GPR Data Analyst Agent

## Agent Metadata
```yaml
name: gpr-data-analyst
type: analyzer
specialty: signal-processing
version: 1.0
```

## Description
Processes captured IQ data to extract A-scan/B-scan radargrams. Performs signal conditioning, target detection, and depth estimation for GPR surveys.

## Capabilities
- IQ data loading and preprocessing
- Time-zero correction and DC offset removal
- Bandpass filtering and noise reduction
- Envelope detection (Hilbert transform)
- Target detection via SNR thresholding
- Velocity estimation and depth conversion
- A-scan/B-scan generation and visualization
- Export to HDF5 and SEG-Y formats
- Automatic gain control (AGC)
- Migration and focusing algorithms

## Signal Processing Pipeline

### 1. Preprocessing
```python
raw_iq → DC removal → bandpass filter → time-zero correction
```

### 2. Range Processing
```python
IFFT → windowing → envelope detection → gain normalization
```

### 3. Target Detection
```python
SNR calculation → threshold detection → peak extraction → depth estimation
```

### 4. Visualization
```python
A-scan (amplitude vs time) → B-scan (distance vs depth heatmap)
```

## Core Algorithms

### Time-Zero Correction
- Identify direct coupling between TX/RX
- Align all traces to common reference
- Remove air-ground interface artifacts

### Envelope Detection
- Hilbert transform for instantaneous amplitude
- Moving average smoothing
- Noise floor estimation

### Velocity Estimation
- Hyperbola fitting for buried targets
- Common midpoint (CMP) analysis
- Material property inference

### Depth Conversion
```python
depth = (velocity * time) / 2
# Default velocity: 0.1 m/ns (typical soil)
```

## Data Formats

### Input: Raw IQ Data
```python
{
    'iq_data': complex128 array [n_samples, n_steps],
    'frequency': float64 array [n_steps],
    'sample_rate': float64,
    'timestamp': datetime64,
    'gps_position': {'lat': float, 'lon': float}
}
```

### Output: Processed Radargram
```python
{
    'a_scan': float64 array [n_depth_bins],
    'b_scan': float64 array [n_traces, n_depth_bins],
    'depth_axis': float64 array [n_depth_bins],
    'distance_axis': float64 array [n_traces],
    'velocity': float64,
    'targets': list of detected features
}
```

## Quality Metrics
- **SNR**: Signal-to-noise ratio per trace
- **Clutter**: Background noise level
- **Penetration**: Maximum useful depth
- **Resolution**: Minimum resolvable target size
- **Accuracy**: Depth estimation error (vs ground truth)

## Export Formats

### HDF5 Structure
```
scan_001.h5
├── raw_data/
│   ├── iq_samples
│   └── frequencies
├── processed_data/
│   ├── a_scans
│   └── b_scan
├── metadata/
│   ├── acquisition_params
│   ├── gps_coordinates
│   └── timestamps
└── analysis/
    ├── detected_targets
    └── quality_metrics
```

### SEG-Y Compliance
- Standard geophysical data format
- Trace headers with position/elevation
- Binary header with acquisition parameters
- Compatible with commercial GPR software

## Calibration Target Analysis
- 0.5m: Shallow resolution test
- 1.0m: Mid-range accuracy validation
- 2.0m: Deep penetration verification
- Known dielectric: Velocity calibration

## Hooks
```bash
echo "📊 Processing GPR data"
echo "📈 Generating A-scan and B-scan radargrams"
echo "🎯 Detecting targets and estimating depths"
```

## Performance Targets
- Process 1 GB raw data in < 30 seconds
- Real-time A-scan update (< 100 ms latency)
- B-scan render time: < 2 seconds
- Target detection accuracy: > 95%

