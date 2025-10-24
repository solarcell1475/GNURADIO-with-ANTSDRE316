"""
Real-Time GPR Dashboard using Streamlit
Provides interactive visualization and control for 450MHz SFCW GPR system
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime
import time
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.hardware.antsdr_control import ANTSDRController, ANTSDRConfig
    from src.analysis.process_ascan import GPRDataProcessor, GPRProcessingParams
except ImportError:
    st.warning("⚠️ Could not import hardware/analysis modules. Running in demo mode.")
    ANTSDRController = None
    GPRDataProcessor = None


# Page configuration
st.set_page_config(
    page_title="450 MHz SFCW GPR Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-good {
        color: #00ff00;
        font-weight: bold;
    }
    .status-warning {
        color: #ffa500;
        font-weight: bold;
    }
    .status-error {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'hardware_connected' not in st.session_state:
    st.session_state.hardware_connected = False
if 'acquisition_running' not in st.session_state:
    st.session_state.acquisition_running = False
if 'a_scan_data' not in st.session_state:
    st.session_state.a_scan_data = None
if 'b_scan_data' not in st.session_state:
    st.session_state.b_scan_data = []
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'targets_detected' not in st.session_state:
    st.session_state.targets_detected = []


def add_log(message: str, level: str = "INFO"):
    """Add message to log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.log_messages.append({
        'timestamp': timestamp,
        'level': level,
        'message': message
    })
    # Keep only last 50 messages
    if len(st.session_state.log_messages) > 50:
        st.session_state.log_messages = st.session_state.log_messages[-50:]


def generate_synthetic_ascan(n_samples=1000):
    """Generate synthetic A-scan data for demo"""
    time_axis = np.linspace(0, 100, n_samples)  # nanoseconds
    
    # Simulate targets at different depths
    signal = np.zeros(n_samples)
    
    # Target 1 at ~20 ns (1m depth)
    target1_pos = 200
    signal[target1_pos:target1_pos+50] = np.exp(-(np.arange(50)/10)**2) * 0.8
    
    # Target 2 at ~40 ns (2m depth)
    target2_pos = 400
    signal[target2_pos:target2_pos+50] = np.exp(-(np.arange(50)/10)**2) * 0.6
    
    # Target 3 at ~70 ns (3.5m depth)
    target3_pos = 700
    signal[target3_pos:target3_pos+50] = np.exp(-(np.arange(50)/10)**2) * 0.4
    
    # Add noise
    noise = np.random.normal(0, 0.05, n_samples)
    signal += noise
    
    return time_axis, signal


def generate_synthetic_bscan(n_traces=50, n_samples=1000):
    """Generate synthetic B-scan data for demo"""
    b_scan = np.zeros((n_traces, n_samples))
    
    for i in range(n_traces):
        _, a_scan = generate_synthetic_ascan(n_samples)
        # Add some variation
        b_scan[i] = a_scan + np.random.normal(0, 0.02, n_samples)
    
    return b_scan


# Header
st.markdown('<div class="main-header">📡 450 MHz SFCW GPR Dashboard</div>', unsafe_allow_html=True)

# Sidebar - Control Panel
st.sidebar.header("⚙️ Control Panel")

# Hardware Configuration
st.sidebar.subheader("Hardware Settings")

with st.sidebar.expander("ANTSDR Configuration", expanded=True):
    ip_address = st.text_input("IP Address", value="192.168.1.10", key="ip_addr")
    center_freq = st.slider("Center Frequency (MHz)", 400, 500, 450, 1, key="center_freq")
    tx_power = st.slider("TX Power (dBm)", -20, 0, -10, 1, key="tx_power")
    rx_gain = st.slider("RX Gain (dB)", 0, 70, 60, 1, key="rx_gain")
    sample_rate = st.selectbox("Sample Rate (MSPS)", [1, 5, 10, 20], index=2, key="sample_rate")

# Processing Parameters
st.sidebar.subheader("Processing Parameters")

with st.sidebar.expander("Signal Processing", expanded=False):
    velocity = st.number_input("Velocity (m/ns)", 0.05, 0.20, 0.10, 0.01, key="velocity")
    time_zero_offset = st.number_input("Time-Zero Offset (ns)", -10.0, 10.0, 0.0, 0.1, key="time_zero")
    snr_threshold = st.slider("SNR Threshold (dB)", 0.0, 30.0, 10.0, 0.5, key="snr_thresh")
    apply_agc = st.checkbox("Apply AGC", value=True, key="apply_agc")
    envelope_detect = st.checkbox("Envelope Detection", value=True, key="envelope_detect")

# Acquisition Controls
st.sidebar.subheader("Acquisition Controls")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🔌 Connect", disabled=st.session_state.hardware_connected, use_container_width=True):
        add_log("Attempting to connect to hardware...", "INFO")
        # In real implementation, connect to hardware here
        st.session_state.hardware_connected = True
        add_log("✅ Hardware connected (demo mode)", "INFO")
        st.rerun()

with col2:
    if st.button("🔌 Disconnect", disabled=not st.session_state.hardware_connected, use_container_width=True):
        st.session_state.hardware_connected = False
        st.session_state.acquisition_running = False
        add_log("Hardware disconnected", "INFO")
        st.rerun()

col3, col4 = st.sidebar.columns(2)

with col3:
    if st.button("▶️ Start", disabled=not st.session_state.hardware_connected or st.session_state.acquisition_running, use_container_width=True):
        st.session_state.acquisition_running = True
        add_log("🚀 Acquisition started", "INFO")
        st.rerun()

with col4:
    if st.button("⏹️ Stop", disabled=not st.session_state.acquisition_running, use_container_width=True):
        st.session_state.acquisition_running = False
        add_log("⏸️ Acquisition stopped", "INFO")
        st.rerun()

if st.sidebar.button("📸 Single Scan", disabled=not st.session_state.hardware_connected, use_container_width=True):
    add_log("Capturing single scan...", "INFO")
    time_axis, signal = generate_synthetic_ascan()
    st.session_state.a_scan_data = (time_axis, signal)
    add_log("✅ Single scan captured", "INFO")
    st.rerun()

if st.sidebar.button("💾 Save Data", use_container_width=True):
    add_log("Saving data to HDF5...", "INFO")
    # In real implementation, save data here
    add_log("✅ Data saved to gpr_scan_001.h5", "INFO")

# Main content area
# Three columns layout
col_left, col_middle, col_right = st.columns([1, 1, 1])

# Left Column - System Status
with col_left:
    st.subheader("📊 System Status")
    
    # Status indicators
    status_container = st.container()
    with status_container:
        if st.session_state.hardware_connected:
            st.markdown("🟢 **Hardware:** <span class='status-good'>Connected</span>", unsafe_allow_html=True)
        else:
            st.markdown("🔴 **Hardware:** <span class='status-error'>Disconnected</span>", unsafe_allow_html=True)
        
        if st.session_state.acquisition_running:
            st.markdown("🟢 **Acquisition:** <span class='status-good'>Running</span>", unsafe_allow_html=True)
        else:
            st.markdown("⚪ **Acquisition:** <span class='status-warning'>Idle</span>", unsafe_allow_html=True)
        
        # Simulate GPS lock
        gps_locked = np.random.random() > 0.3
        if gps_locked:
            st.markdown("🟢 **GPS:** <span class='status-good'>Locked</span>", unsafe_allow_html=True)
        else:
            st.markdown("🟡 **GPS:** <span class='status-warning'>Searching</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # System metrics
    st.subheader("📈 Metrics")
    
    # Simulate metrics
    snr_value = np.random.uniform(15, 25)
    fps_value = np.random.uniform(8, 12)
    temp_value = np.random.uniform(40, 50)
    
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("SNR", f"{snr_value:.1f} dB", delta=f"{np.random.uniform(-1, 1):.1f} dB")
        st.metric("Temperature", f"{temp_value:.1f} °C", delta=f"{np.random.uniform(-0.5, 0.5):.1f} °C")
    
    with metric_col2:
        st.metric("Processing FPS", f"{fps_value:.1f}", delta=f"{np.random.uniform(-0.5, 0.5):.1f}")
        st.metric("Buffer", f"{np.random.randint(70, 95)}%", delta=f"{np.random.randint(-5, 5)}%")

# Middle Column - A-Scan Display
with col_middle:
    st.subheader("📉 A-Scan (Live)")
    
    # Generate or use existing data
    if st.session_state.acquisition_running or st.session_state.a_scan_data is not None:
        if st.session_state.acquisition_running:
            time_axis, signal = generate_synthetic_ascan()
            st.session_state.a_scan_data = (time_axis, signal)
        else:
            time_axis, signal = st.session_state.a_scan_data
        
        # Convert to depth
        depth_axis = (velocity * time_axis) / 2  # Two-way travel time
        
        # Create plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_axis,
            y=signal,
            mode='lines',
            name='Amplitude',
            line=dict(color='#00ff00', width=2)
        ))
        
        # Mark detected targets (simple peak detection)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(signal, height=0.3, distance=50)
        
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(
                x=time_axis[peaks],
                y=signal[peaks],
                mode='markers',
                name='Targets',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig.update_layout(
            xaxis_title="Time (ns)",
            yaxis_title="Amplitude",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True,
            hovermode='x unified',
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Depth plot
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            y=depth_axis,
            x=signal,
            mode='lines',
            name='Amplitude',
            line=dict(color='#00ff00', width=2)
        ))
        
        if len(peaks) > 0:
            fig2.add_trace(go.Scatter(
                y=depth_axis[peaks],
                x=signal[peaks],
                mode='markers',
                name='Targets',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig2.update_layout(
            xaxis_title="Amplitude",
            yaxis_title="Depth (m)",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(autorange='reversed'),
            showlegend=False,
            hovermode='y unified',
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
    else:
        st.info("👆 Click 'Single Scan' or 'Start' to begin acquisition")

# Right Column - B-Scan Display
with col_right:
    st.subheader("🗺️ B-Scan (Radargram)")
    
    # Generate B-scan data
    if st.session_state.acquisition_running:
        b_scan_data = generate_synthetic_bscan(n_traces=50, n_samples=1000)
        st.session_state.b_scan_data = b_scan_data
    elif len(st.session_state.b_scan_data) > 0:
        b_scan_data = st.session_state.b_scan_data
    else:
        b_scan_data = None
    
    if b_scan_data is not None:
        # Create heatmap
        distance_axis = np.arange(b_scan_data.shape[0]) * 0.1  # 0.1m spacing
        time_axis = np.linspace(0, 100, b_scan_data.shape[1])
        depth_axis = (velocity * time_axis) / 2
        
        fig = go.Figure(data=go.Heatmap(
            z=b_scan_data.T,
            x=distance_axis,
            y=depth_axis,
            colorscale='Gray',
            reversescale=True,
            hovertemplate='Distance: %{x:.2f} m<br>Depth: %{y:.2f} m<br>Amplitude: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            xaxis_title="Distance (m)",
            yaxis_title="Depth (m)",
            height=650,
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(autorange='reversed'),
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Start acquisition to generate B-scan")

# Bottom section - Log viewer
st.divider()
st.subheader("📋 System Log")

log_container = st.container()
with log_container:
    if len(st.session_state.log_messages) > 0:
        # Create DataFrame from log messages
        log_df = pd.DataFrame(st.session_state.log_messages)
        
        # Color code by level
        def color_level(val):
            if val == 'ERROR':
                return 'background-color: #ff4444'
            elif val == 'WARNING':
                return 'background-color: #ffaa00'
            else:
                return ''
        
        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True,
            height=150
        )
    else:
        st.info("No log messages yet")

# Auto-refresh when acquisition is running
if st.session_state.acquisition_running:
    time.sleep(0.1)  # 10 FPS refresh rate
    st.rerun()


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    450 MHz SFCW GPR System | Powered by Streamlit + GNU Radio + ANTSDR E316
</div>
""", unsafe_allow_html=True)

