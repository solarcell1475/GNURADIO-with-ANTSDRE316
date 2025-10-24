# Dashboard Builder Agent

## Agent Metadata
```yaml
name: dashboard-builder
type: developer
specialty: visualization
version: 1.0
```

## Description
Builds real-time visualization dashboard for GPR data using Streamlit and Plotly. Provides interactive control panel, live data display, and system health monitoring.

## Capabilities
- Streamlit web application development
- Real-time A-scan visualization (amplitude vs time)
- B-scan heatmap display (distance vs depth, grayscale)
- Interactive control panel for TX/RX parameters
- Live system metrics (SNR, gain, TX power, GPS lock)
- Data logging and export functionality
- Session management and replay
- Responsive design for desktop/tablet
- WebSocket integration for low-latency updates

## Dashboard Layout

### Header
- Project title and logo
- System status indicators (hardware, GPS, processing)
- Current acquisition parameters
- Timestamp and GPS coordinates

### Main Content (3 Columns)

#### Column 1: Control Panel
- **Hardware Settings**
  - Center frequency slider (400-500 MHz)
  - TX power control (-20 to 0 dBm)
  - RX gain control (0-70 dB)
  - Sample rate selector
  
- **Acquisition Controls**
  - Start/Stop buttons
  - Single scan trigger
  - Continuous mode toggle
  - Save scan button

- **Processing Parameters**
  - Filter bandwidth
  - Time-zero offset
  - Velocity setting
  - Target threshold

#### Column 2: A-Scan Display
- Real-time waveform plot
- X-axis: Time (nanoseconds) or Depth (meters)
- Y-axis: Amplitude (normalized or dB)
- Detected targets marked with indicators
- Zoom/pan controls
- Cursor readout

#### Column 3: B-Scan Display
- Heatmap visualization
- X-axis: Survey distance (meters)
- Y-axis: Depth (meters)
- Colormap: Grayscale or viridis
- Aspect ratio control
- Export as PNG/PDF

### Footer
- **System Metrics**
  - SNR gauge
  - Processing FPS
  - Data buffer status
  - Temperature monitor
  
- **Log Viewer**
  - Scrollable message log
  - Severity filtering (Info/Warning/Error)
  - Export log button

## Key Features

### Real-Time Updates
- WebSocket connection to processing backend
- Auto-refresh interval: 100 ms
- Frame buffer to prevent UI blocking
- Asynchronous data loading

### Data Export
- Raw IQ data → HDF5
- Processed radargram → PNG, PDF, TIFF
- Parameters → JSON metadata
- Session replay → compressed archive

### Configuration Profiles
- Save/load parameter presets
- Quick-switch between survey modes
- Template library for common scenarios

### Accessibility
- High-contrast mode
- Keyboard shortcuts
- Screen reader support
- Responsive layout (desktop/tablet)

## Technology Stack
```python
streamlit==1.28.0
plotly==5.17.0
numpy>=1.24.0
pandas>=2.0.0
websockets>=12.0
h5py>=3.9.0
```

## File Structure
```
src/dashboard/
├── gpr_dashboard.py          # Main Streamlit app
├── components/
│   ├── control_panel.py      # Parameter controls
│   ├── ascan_plot.py         # A-scan visualization
│   ├── bscan_plot.py         # B-scan visualization
│   └── metrics_display.py    # System health metrics
├── utils/
│   ├── data_loader.py        # Load IQ/processed data
│   ├── websocket_client.py   # Real-time data stream
│   └── export_utils.py       # Save/export functions
└── config/
    └── dashboard_config.yaml # UI settings
```

## Launch Command
```bash
streamlit run src/dashboard/gpr_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Configuration Options
```yaml
# dashboard_config.yaml
app:
  title: "450 MHz SFCW GPR Dashboard"
  theme: "dark"
  refresh_rate: 100  # milliseconds

visualization:
  a_scan:
    default_units: "nanoseconds"
    line_width: 2
    color: "#00ff00"
  
  b_scan:
    colormap: "gray"
    aspect_ratio: "auto"
    interpolation: "bilinear"

hardware:
  default_ip: "192.168.1.10"
  timeout: 5.0

processing:
  buffer_size: 1000
  max_traces: 500
```

## User Experience Goals
- **Responsiveness**: < 100 ms latency for UI updates
- **Intuitiveness**: No training required for basic operation
- **Reliability**: Graceful degradation on connection loss
- **Aesthetics**: Professional appearance suitable for field deployment

## Hooks
```bash
echo "🚀 Launching GPR Dashboard"
echo "🌐 Access at http://localhost:8501"
echo "📊 Real-time visualization ready"
```

## Testing Checklist
- [ ] All controls functional
- [ ] Real-time data streaming
- [ ] Export formats validated
- [ ] Mobile responsive
- [ ] Error handling graceful
- [ ] Performance under load

