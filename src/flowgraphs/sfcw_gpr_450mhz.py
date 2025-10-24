#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GNU Radio SFCW GPR Flowgraph for 450 MHz
Stepped Frequency Continuous Wave Ground Penetrating Radar

This flowgraph implements:
- SFCW signal generation (400-500 MHz, 50 steps)
- TX/RX with ANTSDR E316 via IIO
- Dechirping and matched filtering
- FFT processing for range bins
- Data logging to HDF5
"""

from gnuradio import gr, blocks, filter, fft, analog, iio
from gnuradio.filter import firdes
import numpy as np
import h5py
import time
from datetime import datetime
from typing import Optional
import pmt


class SFCWFrequencyStepper(gr.sync_block):
    """
    Custom block to generate SFCW frequency steps.
    Outputs frequency control messages for the signal source.
    """
    
    def __init__(self, freq_start, freq_stop, num_steps, dwell_samples):
        """
        Args:
            freq_start: Start frequency (Hz)
            freq_stop: Stop frequency (Hz)
            num_steps: Number of frequency steps
            dwell_samples: Number of samples per frequency step
        """
        gr.sync_block.__init__(
            self,
            name="SFCW Frequency Stepper",
            in_sig=None,
            out_sig=[np.float32]
        )
        
        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.num_steps = num_steps
        self.dwell_samples = dwell_samples
        
        # Generate frequency list
        self.frequencies = np.linspace(freq_start, freq_stop, num_steps)
        self.current_step = 0
        self.sample_count = 0
        
        # Message port for frequency control
        self.message_port_register_out(pmt.intern("freq"))
    
    def work(self, input_items, output_items):
        """Process samples and generate frequency steps"""
        out = output_items[0]
        n_samples = len(out)
        
        for i in range(n_samples):
            if self.sample_count >= self.dwell_samples:
                # Time to step to next frequency
                self.current_step = (self.current_step + 1) % self.num_steps
                freq = self.frequencies[self.current_step]
                
                # Send frequency update message
                freq_msg = pmt.from_double(freq)
                self.message_port_pub(pmt.intern("freq"), freq_msg)
                
                self.sample_count = 0
            
            # Output current frequency
            out[i] = self.frequencies[self.current_step]
            self.sample_count += 1
        
        return n_samples


class sfcw_gpr_450mhz(gr.top_block):
    """
    SFCW GPR Top Block
    Complete flowgraph for 450 MHz ground penetrating radar
    """
    
    def __init__(self, use_hardware=False, data_file="gpr_data.h5"):
        """
        Initialize SFCW GPR flowgraph.
        
        Args:
            use_hardware: If True, use ANTSDR E316. If False, use simulation.
            data_file: Output HDF5 file path
        """
        gr.top_block.__init__(self, "SFCW GPR 450MHz")
        
        # ===========================================
        # Parameters
        # ===========================================
        self.sample_rate = 10e6  # 10 MSPS
        self.freq_start = 400e6  # 400 MHz
        self.freq_stop = 500e6   # 500 MHz
        self.freq_step = 2e6     # 2 MHz
        self.num_steps = int((self.freq_stop - self.freq_start) / self.freq_step) + 1
        self.center_freq = (self.freq_start + self.freq_stop) / 2  # 450 MHz
        self.dwell_time = 1e-3   # 1 ms per frequency
        self.dwell_samples = int(self.sample_rate * self.dwell_time)
        
        self.tx_power = -10  # dBm
        self.rx_gain = 60    # dB
        self.bandwidth = 10e6  # 10 MHz
        
        self.use_hardware = use_hardware
        self.data_file = data_file
        
        # ===========================================
        # Blocks
        # ===========================================
        
        if use_hardware:
            # ANTSDR E316 IIO Source/Sink
            try:
                self.iio_pluto_source = iio.fmcomms2_source_fc32(
                    "ip:192.168.1.10",
                    [True, False],  # Enable RX1, disable RX2
                    32768  # Buffer size
                )
                self.iio_pluto_source.set_params(
                    int(self.center_freq),
                    int(self.sample_rate),
                    int(self.bandwidth),
                    True,  # Quadrature
                    True,  # RF DC
                    True,  # BB DC
                    "manual",  # Gain mode
                    self.rx_gain,
                    "",  # Filter
                    True  # Auto filter
                )
                
                self.iio_pluto_sink = iio.fmcomms2_sink_fc32(
                    "ip:192.168.1.10",
                    [True, False],  # Enable TX1, disable TX2
                    32768,  # Buffer size
                    False  # Cyclic
                )
                self.iio_pluto_sink.set_params(
                    int(self.center_freq),
                    int(self.sample_rate),
                    int(self.bandwidth),
                    self.tx_power,
                    ""  # Filter
                )
                
                print("✅ Hardware mode: Using ANTSDR E316")
            except Exception as e:
                print(f"❌ Failed to initialize hardware: {e}")
                print("   Falling back to simulation mode")
                use_hardware = False
                self.use_hardware = False
        
        if not use_hardware:
            # Simulation mode: Use noise source
            self.noise_source = analog.noise_source_c(analog.GR_GAUSSIAN, 0.1, 0)
            print("⚙️  Simulation mode: Using noise source")
        
        # SFCW Frequency Stepper
        self.freq_stepper = SFCWFrequencyStepper(
            self.freq_start,
            self.freq_stop,
            self.num_steps,
            self.dwell_samples
        )
        
        # Signal Source for TX (or reference for dechirping)
        self.signal_source = analog.sig_source_c(
            self.sample_rate,
            analog.GR_COS_WAVE,
            0,  # Will be controlled by freq_stepper
            1.0,  # Amplitude
            0  # Offset
        )
        
        # Multiply for dechirping (mix RX with TX reference)
        self.multiply = blocks.multiply_vcc(1)
        
        # Complex conjugate for proper mixing
        self.conjugate = blocks.conjugate_cc()
        
        # Low-pass filter to extract baseband
        lpf_taps = firdes.low_pass(
            1.0,
            self.sample_rate,
            self.bandwidth / 2,
            self.bandwidth / 10,
            window=fft.window.WIN_HAMMING,
            param=6.76
        )
        self.lpf = filter.fir_filter_ccf(1, lpf_taps)
        
        # Decimation to reduce data rate
        self.decimator = filter.fir_filter_ccf(
            10,  # Decimation factor
            firdes.low_pass(1.0, self.sample_rate, self.bandwidth/2, self.bandwidth/10)
        )
        
        # Stream to vector for FFT processing
        self.stream_to_vector = blocks.stream_to_vector(
            gr.sizeof_gr_complex,
            self.dwell_samples // 10  # After decimation
        )
        
        # FFT for range processing
        self.fft_block = fft.fft_vcc(
            self.dwell_samples // 10,
            True,  # Forward FFT
            window.blackmanharris(self.dwell_samples // 10),
            True,  # Shift
            1  # Threads
        )
        
        # Complex to magnitude
        self.complex_to_mag = blocks.complex_to_mag(self.dwell_samples // 10)
        
        # Vector sink to capture processed data
        self.vector_sink = blocks.vector_sink_f(self.dwell_samples // 10)
        
        # File sinks for logging
        self.file_sink_raw = blocks.file_sink(
            gr.sizeof_gr_complex,
            "gpr_raw_iq.dat",
            False
        )
        self.file_sink_raw.set_unbuffered(False)
        
        self.file_sink_processed = blocks.vector_sink_f(self.dwell_samples // 10)
        
        # Throttle for simulation mode
        if not use_hardware:
            self.throttle = blocks.throttle(gr.sizeof_gr_complex, self.sample_rate, True)
        
        # ===========================================
        # Connections
        # ===========================================
        
        # TX path
        if use_hardware:
            self.connect((self.signal_source, 0), (self.iio_pluto_sink, 0))
            rx_source = (self.iio_pluto_source, 0)
        else:
            self.connect((self.signal_source, 0), (self.throttle, 0))
            # In simulation, add signal to noise
            self.adder = blocks.add_vcc(1)
            self.connect((self.throttle, 0), (self.adder, 0))
            self.connect((self.noise_source, 0), (self.adder, 1))
            rx_source = (self.adder, 0)
        
        # RX path
        # Save raw IQ
        self.connect(rx_source, (self.file_sink_raw, 0))
        
        # Dechirping chain
        self.connect(rx_source, (self.multiply, 0))
        self.connect((self.signal_source, 0), (self.conjugate, 0))
        self.connect((self.conjugate, 0), (self.multiply, 1))
        
        # Filtering and decimation
        self.connect((self.multiply, 0), (self.lpf, 0))
        self.connect((self.lpf, 0), (self.decimator, 0))
        
        # FFT processing
        self.connect((self.decimator, 0), (self.stream_to_vector, 0))
        self.connect((self.stream_to_vector, 0), (self.fft_block, 0))
        self.connect((self.fft_block, 0), (self.complex_to_mag, 0))
        self.connect((self.complex_to_mag, 0), (self.file_sink_processed, 0))
        
        # Frequency stepping control
        self.msg_connect((self.freq_stepper, "freq"), (self.signal_source, "freq"))
    
    def get_data(self):
        """
        Retrieve captured data from vector sinks.
        
        Returns:
            Dictionary with raw and processed data
        """
        processed_data = np.array(self.file_sink_processed.data())
        
        # Reshape into A-scans (one per frequency step)
        n_range_bins = self.dwell_samples // 10
        n_scans = len(processed_data) // n_range_bins
        
        if n_scans > 0:
            a_scans = processed_data[:n_scans * n_range_bins].reshape((n_scans, n_range_bins))
        else:
            a_scans = np.array([])
        
        return {
            'a_scans': a_scans,
            'frequencies': np.linspace(self.freq_start, self.freq_stop, self.num_steps),
            'sample_rate': self.sample_rate,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_to_hdf5(self, filepath: Optional[str] = None):
        """
        Save captured data to HDF5 file.
        
        Args:
            filepath: Output file path (uses default if None)
        """
        if filepath is None:
            filepath = self.data_file
        
        data = self.get_data()
        
        with h5py.File(filepath, 'w') as f:
            # Create groups
            raw_grp = f.create_group('raw_data')
            proc_grp = f.create_group('processed_data')
            meta_grp = f.create_group('metadata')
            
            # Save processed data
            if len(data['a_scans']) > 0:
                proc_grp.create_dataset('a_scans', data=data['a_scans'])
            proc_grp.create_dataset('frequencies', data=data['frequencies'])
            
            # Save metadata
            meta_grp.attrs['sample_rate'] = self.sample_rate
            meta_grp.attrs['center_freq'] = self.center_freq
            meta_grp.attrs['freq_start'] = self.freq_start
            meta_grp.attrs['freq_stop'] = self.freq_stop
            meta_grp.attrs['num_steps'] = self.num_steps
            meta_grp.attrs['dwell_time'] = self.dwell_time
            meta_grp.attrs['tx_power'] = self.tx_power
            meta_grp.attrs['rx_gain'] = self.rx_gain
            meta_grp.attrs['timestamp'] = data['timestamp']
        
        print(f"✅ Data saved to {filepath}")


def main():
    """Example usage"""
    print("=" * 60)
    print("SFCW GPR 450MHz Flowgraph")
    print("=" * 60)
    
    # Create flowgraph in simulation mode
    tb = sfcw_gpr_450mhz(use_hardware=False, data_file="test_gpr_data.h5")
    
    print("\nFlowgraph Parameters:")
    print(f"  Frequency Range: {tb.freq_start/1e6:.1f} - {tb.freq_stop/1e6:.1f} MHz")
    print(f"  Number of Steps: {tb.num_steps}")
    print(f"  Frequency Step: {tb.freq_step/1e6:.1f} MHz")
    print(f"  Dwell Time: {tb.dwell_time*1e3:.1f} ms")
    print(f"  Sample Rate: {tb.sample_rate/1e6:.1f} MSPS")
    print(f"  Mode: {'Hardware' if tb.use_hardware else 'Simulation'}")
    
    # Run for 5 seconds
    print("\nStarting acquisition...")
    tb.start()
    time.sleep(5.0)
    tb.stop()
    tb.wait()
    print("✅ Acquisition complete")
    
    # Save data
    tb.save_to_hdf5()
    
    # Display data info
    data = tb.get_data()
    if len(data['a_scans']) > 0:
        print(f"\nCaptured {len(data['a_scans'])} A-scans")
        print(f"Range bins per scan: {data['a_scans'].shape[1]}")
    else:
        print("\nNo data captured")


if __name__ == '__main__':
    main()

