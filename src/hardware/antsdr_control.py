"""
ANTSDR E316 Hardware Control Module
Provides Python interface to configure and monitor ANTSDR E316 (AD9364) via IIO.
"""

import subprocess
import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ANTSDRConfig:
    """Configuration parameters for ANTSDR E316"""
    ip_address: str = "192.168.1.10"
    center_freq: float = 450e6  # Hz
    tx_power: float = -10.0  # dBm
    rx_gain: float = 60.0  # dB
    sample_rate: float = 10e6  # sps
    bandwidth: float = 10e6  # Hz
    tx_port: str = "TX_A"
    rx_port: str = "A_BALANCED"


class ANTSDRController:
    """
    Controller class for ANTSDR E316 hardware.
    Manages RF parameters, GPS, and data streaming.
    """
    
    def __init__(self, config: Optional[ANTSDRConfig] = None):
        """
        Initialize ANTSDR controller.
        
        Args:
            config: ANTSDRConfig object with device parameters
        """
        self.config = config or ANTSDRConfig()
        self.device_uri = f"ip:{self.config.ip_address}"
        self.device_name = "ad9364-phy"
        self.is_connected = False
        self.gps_locked = False
        
    def _run_iio_cmd(self, args: list, check: bool = True) -> Tuple[bool, str]:
        """
        Execute IIO command and return result.
        
        Args:
            args: Command arguments list
            check: Raise exception on error if True
            
        Returns:
            Tuple of (success, output)
        """
        cmd = ["iio_attr", "-u", self.device_uri] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5.0,
                check=check
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"IIO command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            return False, e.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"IIO command timeout: {' '.join(cmd)}")
            return False, "Command timeout"
        except FileNotFoundError:
            logger.error("iio_attr command not found. Please install libiio-utils.")
            return False, "iio_attr not found"
    
    def connect(self) -> bool:
        """
        Verify connection to ANTSDR E316.
        
        Returns:
            True if connected successfully
        """
        logger.info(f"Connecting to ANTSDR at {self.device_uri}...")
        
        # Try to read device name as connectivity test
        success, output = self._run_iio_cmd(["-d", self.device_name, "-c", "voltage0"], check=False)
        
        if success:
            self.is_connected = True
            logger.info("✅ Successfully connected to ANTSDR E316")
            return True
        else:
            self.is_connected = False
            logger.error("❌ Failed to connect to ANTSDR E316")
            logger.error(f"   Please verify: IP address ({self.config.ip_address}), network connection, device power")
            return False
    
    def configure_tx(self) -> bool:
        """
        Configure transmit parameters.
        
        Returns:
            True if configuration successful
        """
        if not self.is_connected:
            logger.error("Device not connected. Call connect() first.")
            return False
        
        logger.info("Configuring TX parameters...")
        
        # Set TX frequency
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-o", "frequency",
            str(int(self.config.center_freq))
        ])
        if not success:
            return False
        logger.info(f"  TX Frequency: {self.config.center_freq/1e6:.1f} MHz")
        
        # Set TX power (hardware gain)
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-o", "hardwaregain",
            str(int(self.config.tx_power))
        ])
        if not success:
            return False
        logger.info(f"  TX Power: {self.config.tx_power} dBm")
        
        # Set TX port
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-o", "rf_port_select",
            self.config.tx_port
        ])
        if not success:
            return False
        logger.info(f"  TX Port: {self.config.tx_port}")
        
        logger.info("✅ TX configuration complete")
        return True
    
    def configure_rx(self) -> bool:
        """
        Configure receive parameters.
        
        Returns:
            True if configuration successful
        """
        if not self.is_connected:
            logger.error("Device not connected. Call connect() first.")
            return False
        
        logger.info("Configuring RX parameters...")
        
        # Set RX frequency
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-i", "frequency",
            str(int(self.config.center_freq))
        ])
        if not success:
            return False
        logger.info(f"  RX Frequency: {self.config.center_freq/1e6:.1f} MHz")
        
        # Set RX gain
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-i", "hardwaregain",
            str(int(self.config.rx_gain))
        ])
        if not success:
            return False
        logger.info(f"  RX Gain: {self.config.rx_gain} dB")
        
        # Set RX port
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "-i", "rf_port_select",
            self.config.rx_port
        ])
        if not success:
            return False
        logger.info(f"  RX Port: {self.config.rx_port}")
        
        logger.info("✅ RX configuration complete")
        return True
    
    def configure_sampling(self) -> bool:
        """
        Configure sample rate and bandwidth.
        
        Returns:
            True if configuration successful
        """
        if not self.is_connected:
            logger.error("Device not connected. Call connect() first.")
            return False
        
        logger.info("Configuring sampling parameters...")
        
        # Set sample rate
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "sampling_frequency",
            str(int(self.config.sample_rate))
        ])
        if not success:
            return False
        logger.info(f"  Sample Rate: {self.config.sample_rate/1e6:.1f} MSPS")
        
        # Set RF bandwidth
        success, _ = self._run_iio_cmd([
            "-d", self.device_name,
            "-c", "voltage0",
            "rf_bandwidth",
            str(int(self.config.bandwidth))
        ])
        if not success:
            return False
        logger.info(f"  Bandwidth: {self.config.bandwidth/1e6:.1f} MHz")
        
        logger.info("✅ Sampling configuration complete")
        return True
    
    def configure_all(self) -> bool:
        """
        Configure all hardware parameters.
        
        Returns:
            True if all configurations successful
        """
        if not self.is_connected:
            if not self.connect():
                return False
        
        success = True
        success &= self.configure_sampling()
        success &= self.configure_tx()
        success &= self.configure_rx()
        
        if success:
            logger.info("🎉 All ANTSDR hardware successfully configured!")
        else:
            logger.error("❌ Hardware configuration failed")
        
        return success
    
    def check_gps(self) -> bool:
        """
        Check GPS lock status.
        
        Returns:
            True if GPS is locked
        """
        # Note: GPS check implementation depends on specific ANTSDR firmware
        # This is a placeholder that attempts to read GPS-related attributes
        logger.info("Checking GPS status...")
        
        # Try to read GPS fix attribute (implementation-specific)
        # This may need adjustment based on actual device firmware
        success, output = self._run_iio_cmd(["-d", "gps"], check=False)
        
        if success and "lock" in output.lower():
            self.gps_locked = True
            logger.info("✅ GPS locked")
            return True
        else:
            self.gps_locked = False
            logger.warning("⚠️  GPS not locked (this may be expected if GPS is not connected)")
            return False
    
    def get_status(self) -> Dict:
        """
        Get current device status and parameters.
        
        Returns:
            Dictionary with device status
        """
        status = {
            "connected": self.is_connected,
            "gps_locked": self.gps_locked,
            "config": {
                "ip_address": self.config.ip_address,
                "center_freq_mhz": self.config.center_freq / 1e6,
                "tx_power_dbm": self.config.tx_power,
                "rx_gain_db": self.config.rx_gain,
                "sample_rate_msps": self.config.sample_rate / 1e6,
                "bandwidth_mhz": self.config.bandwidth / 1e6
            }
        }
        return status
    
    def run_frequency_sweep_test(self, start_freq: float, stop_freq: float, 
                                  step_freq: float) -> bool:
        """
        Test frequency sweep capability.
        
        Args:
            start_freq: Start frequency (Hz)
            stop_freq: Stop frequency (Hz)
            step_freq: Frequency step (Hz)
            
        Returns:
            True if sweep test successful
        """
        logger.info(f"Running frequency sweep test: {start_freq/1e6:.1f} - {stop_freq/1e6:.1f} MHz")
        
        current_freq = start_freq
        step_count = 0
        
        while current_freq <= stop_freq:
            # Set frequency
            success, _ = self._run_iio_cmd([
                "-d", self.device_name,
                "-c", "voltage0",
                "-o", "frequency",
                str(int(current_freq))
            ])
            
            if not success:
                logger.error(f"  Failed at {current_freq/1e6:.1f} MHz")
                return False
            
            step_count += 1
            current_freq += step_freq
            time.sleep(0.001)  # 1 ms dwell time
        
        logger.info(f"✅ Frequency sweep complete: {step_count} steps")
        
        # Restore center frequency
        self.configure_tx()
        return True
    
    def save_config(self, filepath: str):
        """
        Save current configuration to JSON file.
        
        Args:
            filepath: Path to save configuration
        """
        config_dict = {
            "ip_address": self.config.ip_address,
            "center_freq": self.config.center_freq,
            "tx_power": self.config.tx_power,
            "rx_gain": self.config.rx_gain,
            "sample_rate": self.config.sample_rate,
            "bandwidth": self.config.bandwidth,
            "tx_port": self.config.tx_port,
            "rx_port": self.config.rx_port
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {filepath}")
    
    @classmethod
    def load_config(cls, filepath: str) -> 'ANTSDRController':
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            ANTSDRController instance with loaded configuration
        """
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        config = ANTSDRConfig(**config_dict)
        controller = cls(config)
        logger.info(f"Configuration loaded from {filepath}")
        return controller


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("ANTSDR E316 Hardware Control - Test Script")
    print("=" * 60)
    
    # Create controller with default configuration
    controller = ANTSDRController()
    
    # Connect to device
    if not controller.connect():
        print("\n⚠️  Connection failed. This is expected if hardware is not connected.")
        print("   To use with real hardware, ensure:")
        print("   1. ANTSDR E316 is powered on")
        print("   2. Connected via Ethernet")
        print("   3. IP address is configured correctly (default: 192.168.1.10)")
        return
    
    # Configure all parameters
    controller.configure_all()
    
    # Check GPS
    controller.check_gps()
    
    # Run frequency sweep test
    controller.run_frequency_sweep_test(
        start_freq=400e6,
        stop_freq=500e6,
        step_freq=2e6
    )
    
    # Display status
    status = controller.get_status()
    print("\n" + "=" * 60)
    print("Device Status:")
    print("=" * 60)
    print(json.dumps(status, indent=2))
    
    # Save configuration
    controller.save_config("antsdr_config.json")


if __name__ == "__main__":
    main()

