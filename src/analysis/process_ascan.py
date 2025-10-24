"""
GPR Data Analysis Module
Processes raw IQ data into A-scans and B-scans for ground penetrating radar
"""

import numpy as np
import h5py
from scipy import signal
from scipy.fft import fft, ifft, fftfreq
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict
import matplotlib.pyplot as plt
from datetime import datetime


@dataclass
class GPRProcessingParams:
    """Parameters for GPR signal processing"""
    velocity: float = 0.1  # m/ns, typical soil
    time_zero_offset: float = 0.0  # ns
    filter_low: float = 100e6  # Hz
    filter_high: float = 400e6  # Hz
    snr_threshold: float = 10.0  # dB
    apply_agc: bool = True
    agc_window: int = 50  # samples
    envelope_detection: bool = True


class GPRDataProcessor:
    """
    Processes GPR data from raw IQ to calibrated radargrams.
    Implements time-zero correction, filtering, envelope detection, and target detection.
    """
    
    def __init__(self, params: Optional[GPRProcessingParams] = None):
        """
        Initialize GPR data processor.
        
        Args:
            params: Processing parameters
        """
        self.params = params or GPRProcessingParams()
    
    def load_hdf5(self, filepath: str) -> Dict:
        """
        Load GPR data from HDF5 file.
        
        Args:
            filepath: Path to HDF5 file
            
        Returns:
            Dictionary with data and metadata
        """
        data = {}
        
        with h5py.File(filepath, 'r') as f:
            # Load processed data
            if 'processed_data/a_scans' in f:
                data['a_scans'] = f['processed_data/a_scans'][:]
            
            if 'processed_data/frequencies' in f:
                data['frequencies'] = f['processed_data/frequencies'][:]
            
            # Load metadata
            if 'metadata' in f:
                meta = f['metadata']
                data['sample_rate'] = meta.attrs.get('sample_rate', 10e6)
                data['center_freq'] = meta.attrs.get('center_freq', 450e6)
                data['freq_start'] = meta.attrs.get('freq_start', 400e6)
                data['freq_stop'] = meta.attrs.get('freq_stop', 500e6)
                data['num_steps'] = meta.attrs.get('num_steps', 50)
                data['timestamp'] = meta.attrs.get('timestamp', 'unknown')
        
        return data
    
    def remove_dc_offset(self, data: np.ndarray) -> np.ndarray:
        """
        Remove DC offset from each trace.
        
        Args:
            data: Input data array (n_traces, n_samples)
            
        Returns:
            DC-corrected data
        """
        if data.ndim == 1:
            return data - np.mean(data)
        else:
            return data - np.mean(data, axis=1, keepdims=True)
    
    def bandpass_filter(self, data: np.ndarray, sample_rate: float) -> np.ndarray:
        """
        Apply bandpass filter to remove noise.
        
        Args:
            data: Input data
            sample_rate: Sample rate (Hz)
            
        Returns:
            Filtered data
        """
        nyquist = sample_rate / 2
        low = self.params.filter_low / nyquist
        high = self.params.filter_high / nyquist
        
        # Ensure filter parameters are valid
        low = max(0.01, min(low, 0.99))
        high = max(low + 0.01, min(high, 0.99))
        
        # Design Butterworth bandpass filter
        sos = signal.butter(4, [low, high], btype='band', output='sos')
        
        if data.ndim == 1:
            filtered = signal.sosfilt(sos, data)
        else:
            filtered = np.array([signal.sosfilt(sos, trace) for trace in data])
        
        return filtered
    
    def time_zero_correction(self, data: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Find and correct time-zero (direct wave arrival).
        
        Args:
            data: Input data
            
        Returns:
            Tuple of (corrected data, time-zero index)
        """
        if data.ndim == 1:
            # Find first strong peak (direct wave)
            envelope = np.abs(signal.hilbert(data))
            threshold = 0.5 * np.max(envelope)
            time_zero_idx = np.argmax(envelope > threshold)
        else:
            # Average across all traces
            avg_trace = np.mean(np.abs(data), axis=0)
            envelope = np.abs(signal.hilbert(avg_trace))
            threshold = 0.5 * np.max(envelope)
            time_zero_idx = np.argmax(envelope > threshold)
        
        # Apply offset from parameters
        offset_samples = int(self.params.time_zero_offset * 1e-9 * self.params.velocity * 3e8)
        time_zero_idx += offset_samples
        
        # Shift data to align time-zero
        if data.ndim == 1:
            corrected = np.roll(data, -time_zero_idx)
            corrected[:time_zero_idx] = 0
        else:
            corrected = np.roll(data, -time_zero_idx, axis=1)
            corrected[:, :time_zero_idx] = 0
        
        return corrected, time_zero_idx
    
    def envelope_detection(self, data: np.ndarray) -> np.ndarray:
        """
        Extract envelope using Hilbert transform.
        
        Args:
            data: Input data
            
        Returns:
            Envelope (amplitude)
        """
        if data.ndim == 1:
            analytic = signal.hilbert(data)
            envelope = np.abs(analytic)
        else:
            envelope = np.array([np.abs(signal.hilbert(trace)) for trace in data])
        
        return envelope
    
    def apply_agc(self, data: np.ndarray) -> np.ndarray:
        """
        Apply Automatic Gain Control to enhance weak signals.
        
        Args:
            data: Input data
            
        Returns:
            AGC-corrected data
        """
        window = self.params.agc_window
        
        if data.ndim == 1:
            # Compute running RMS
            rms = np.sqrt(np.convolve(data**2, np.ones(window)/window, mode='same'))
            rms = np.maximum(rms, 1e-6)  # Avoid division by zero
            agc_data = data / rms
        else:
            agc_data = np.zeros_like(data)
            for i, trace in enumerate(data):
                rms = np.sqrt(np.convolve(trace**2, np.ones(window)/window, mode='same'))
                rms = np.maximum(rms, 1e-6)
                agc_data[i] = trace / rms
        
        return agc_data
    
    def calculate_snr(self, data: np.ndarray) -> float:
        """
        Calculate signal-to-noise ratio.
        
        Args:
            data: Input data
            
        Returns:
            SNR in dB
        """
        if data.ndim == 1:
            trace = data
        else:
            trace = np.mean(data, axis=0)
        
        # Assume first 10% is noise, rest contains signal
        noise_end = len(trace) // 10
        noise = trace[:noise_end]
        signal_region = trace[noise_end:]
        
        noise_power = np.var(noise)
        signal_power = np.var(signal_region)
        
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
        else:
            snr_db = 100.0  # Very high SNR
        
        return snr_db
    
    def detect_targets(self, data: np.ndarray, sample_rate: float) -> List[Dict]:
        """
        Detect targets using peak detection and SNR thresholding.
        
        Args:
            data: Processed A-scan data
            sample_rate: Sample rate (Hz)
            
        Returns:
            List of detected targets with depths and amplitudes
        """
        if data.ndim == 1:
            trace = data
        else:
            trace = np.mean(data, axis=0)
        
        # Find peaks
        peaks, properties = signal.find_peaks(
            trace,
            height=np.max(trace) * 0.1,  # At least 10% of max
            distance=int(sample_rate * 0.5e-9 / self.params.velocity)  # Minimum 0.5m separation
        )
        
        targets = []
        for i, peak_idx in enumerate(peaks):
            # Convert time to depth
            time_ns = peak_idx / sample_rate * 1e9
            depth_m = (self.params.velocity * time_ns) / 2  # Two-way travel time
            
            # Calculate local SNR
            window_start = max(0, peak_idx - 50)
            window_end = min(len(trace), peak_idx + 50)
            local_signal = trace[peak_idx]
            local_noise = np.std(trace[window_start:window_end])
            
            if local_noise > 0:
                local_snr = 20 * np.log10(local_signal / local_noise)
            else:
                local_snr = 100.0
            
            if local_snr > self.params.snr_threshold:
                targets.append({
                    'index': peak_idx,
                    'time_ns': time_ns,
                    'depth_m': depth_m,
                    'amplitude': local_signal,
                    'snr_db': local_snr
                })
        
        return targets
    
    def process_ascan(self, data: np.ndarray, sample_rate: float) -> Tuple[np.ndarray, List[Dict]]:
        """
        Complete A-scan processing pipeline.
        
        Args:
            data: Raw A-scan data
            sample_rate: Sample rate (Hz)
            
        Returns:
            Tuple of (processed A-scan, detected targets)
        """
        # Processing pipeline
        processed = self.remove_dc_offset(data)
        processed = self.bandpass_filter(processed, sample_rate)
        processed, time_zero = self.time_zero_correction(processed)
        
        if self.params.envelope_detection:
            processed = self.envelope_detection(processed)
        
        if self.params.apply_agc:
            processed = self.apply_agc(processed)
        
        # Detect targets
        targets = self.detect_targets(processed, sample_rate)
        
        return processed, targets
    
    def create_bscan(self, a_scans: np.ndarray, trace_spacing: float = 0.1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Create B-scan (radargram) from multiple A-scans.
        
        Args:
            a_scans: Array of A-scans (n_traces, n_samples)
            trace_spacing: Spacing between traces (meters)
            
        Returns:
            Tuple of (B-scan, distance_axis, depth_axis)
        """
        n_traces, n_samples = a_scans.shape
        
        # Distance axis
        distance_axis = np.arange(n_traces) * trace_spacing
        
        # Depth axis (assuming sample rate from params)
        # Note: This is an approximation; actual sample_rate should be passed
        sample_rate = 1e6  # 1 MSPS after decimation
        time_axis_ns = np.arange(n_samples) / sample_rate * 1e9
        depth_axis = (self.params.velocity * time_axis_ns) / 2
        
        return a_scans, distance_axis, depth_axis
    
    def save_segy(self, b_scan: np.ndarray, filepath: str, metadata: Dict):
        """
        Save B-scan to SEG-Y format.
        
        Args:
            b_scan: B-scan data
            filepath: Output file path
            metadata: Survey metadata
        """
        # Note: Full SEG-Y implementation requires segysak or similar library
        # This is a placeholder showing the structure
        print(f"⚠️  SEG-Y export not fully implemented. Would save to {filepath}")
        print(f"   B-scan shape: {b_scan.shape}")
        print(f"   Metadata: {metadata}")
    
    def plot_ascan(self, a_scan: np.ndarray, sample_rate: float, targets: Optional[List[Dict]] = None):
        """
        Plot A-scan with detected targets.
        
        Args:
            a_scan: A-scan data
            sample_rate: Sample rate (Hz)
            targets: List of detected targets
        """
        time_ns = np.arange(len(a_scan)) / sample_rate * 1e9
        depth_m = (self.params.velocity * time_ns) / 2
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Plot vs time
        ax1.plot(time_ns, a_scan)
        ax1.set_xlabel('Time (ns)')
        ax1.set_ylabel('Amplitude')
        ax1.set_title('A-Scan (Time Domain)')
        ax1.grid(True)
        
        if targets:
            for target in targets:
                ax1.axvline(target['time_ns'], color='r', linestyle='--', alpha=0.7)
                ax1.text(target['time_ns'], np.max(a_scan) * 0.9, 
                        f"{target['depth_m']:.2f}m", rotation=90)
        
        # Plot vs depth
        ax2.plot(a_scan, depth_m)
        ax2.set_xlabel('Amplitude')
        ax2.set_ylabel('Depth (m)')
        ax2.set_title('A-Scan (Depth Domain)')
        ax2.invert_yaxis()
        ax2.grid(True)
        
        if targets:
            for target in targets:
                ax2.axhline(target['depth_m'], color='r', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig('ascan_plot.png', dpi=150)
        print("✅ A-scan plot saved to ascan_plot.png")
        plt.close()
    
    def plot_bscan(self, b_scan: np.ndarray, distance_axis: np.ndarray, depth_axis: np.ndarray):
        """
        Plot B-scan radargram.
        
        Args:
            b_scan: B-scan data
            distance_axis: Distance axis (m)
            depth_axis: Depth axis (m)
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot as heatmap
        im = ax.imshow(
            b_scan.T,
            aspect='auto',
            cmap='gray',
            extent=[distance_axis[0], distance_axis[-1], depth_axis[-1], depth_axis[0]],
            interpolation='bilinear'
        )
        
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Depth (m)')
        ax.set_title('B-Scan Radargram')
        
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Amplitude')
        
        plt.tight_layout()
        plt.savefig('bscan_plot.png', dpi=150)
        print("✅ B-scan plot saved to bscan_plot.png")
        plt.close()


def main():
    """Example usage"""
    print("=" * 60)
    print("GPR Data Analysis - Test Script")
    print("=" * 60)
    
    # Create processor
    params = GPRProcessingParams(
        velocity=0.1,  # m/ns
        time_zero_offset=0.0,
        filter_low=100e6,
        filter_high=400e6,
        snr_threshold=10.0,
        apply_agc=True,
        envelope_detection=True
    )
    processor = GPRDataProcessor(params)
    
    # Generate synthetic test data
    print("\nGenerating synthetic GPR data for testing...")
    sample_rate = 1e6  # 1 MSPS
    duration = 100e-6  # 100 µs
    n_samples = int(sample_rate * duration)
    time = np.arange(n_samples) / sample_rate
    
    # Simulate GPR signal with targets at different depths
    signal_data = np.zeros(n_samples)
    
    # Target at 1m (6.67 ns two-way time at v=0.15 m/ns)
    target1_time = 1.0 / 0.1 * 2 / 1e9  # Two-way travel time
    target1_idx = int(target1_time * sample_rate)
    if target1_idx < n_samples:
        signal_data[target1_idx] = 1.0
    
    # Target at 2m
    target2_time = 2.0 / 0.1 * 2 / 1e9
    target2_idx = int(target2_time * sample_rate)
    if target2_idx < n_samples:
        signal_data[target2_idx] = 0.7
    
    # Add noise
    noise = np.random.normal(0, 0.1, n_samples)
    test_data = signal_data + noise
    
    # Process
    print("\nProcessing A-scan...")
    processed, targets = processor.process_ascan(test_data, sample_rate)
    
    # Calculate SNR
    snr = processor.calculate_snr(processed)
    print(f"\nSignal-to-Noise Ratio: {snr:.1f} dB")
    
    # Display detected targets
    print(f"\nDetected {len(targets)} target(s):")
    for i, target in enumerate(targets, 1):
        print(f"  Target {i}:")
        print(f"    Depth: {target['depth_m']:.2f} m")
        print(f"    Time: {target['time_ns']:.1f} ns")
        print(f"    SNR: {target['snr_db']:.1f} dB")
    
    # Plot
    processor.plot_ascan(processed, sample_rate, targets)
    
    # Create B-scan from multiple A-scans
    print("\nCreating B-scan from 10 traces...")
    n_traces = 10
    a_scans = np.array([test_data + np.random.normal(0, 0.05, n_samples) for _ in range(n_traces)])
    
    # Process all traces
    processed_scans = np.array([processor.process_ascan(scan, sample_rate)[0] for scan in a_scans])
    
    # Create B-scan
    b_scan, distance_axis, depth_axis = processor.create_bscan(processed_scans, trace_spacing=0.1)
    processor.plot_bscan(b_scan, distance_axis, depth_axis)
    
    print("\n✅ Processing complete")


if __name__ == "__main__":
    main()

