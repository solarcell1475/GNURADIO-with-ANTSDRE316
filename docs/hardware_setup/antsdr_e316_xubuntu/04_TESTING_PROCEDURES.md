# ANTSDR E316 Testing Procedures on Xubuntu 22.04

## 📋 Table of Contents
- [Pre-Testing Checklist](#pre-testing-checklist)
- [Basic Connectivity Tests](#basic-connectivity-tests)
- [Hardware Functionality Tests](#hardware-functionality-tests)
- [RF Performance Tests](#rf-performance-tests)
- [GNU Radio Integration Tests](#gnu-radio-integration-tests)
- [Python API Tests](#python-api-tests)
- [GPS Tests](#gps-tests)
- [Performance Benchmarks](#performance-benchmarks)
- [Automated Test Script](#automated-test-script)

---

## Pre-Testing Checklist

Before running tests, verify:

- [ ] E316 powered on with all LEDs in correct state
- [ ] Network connection established (ping works)
- [ ] All software installed (libiio, GNU Radio, etc.)
- [ ] RF antennas or terminators connected to TX/RX
- [ ] GPS antenna connected (for GPS tests)
- [ ] No other applications using the E316

---

## Basic Connectivity Tests

### Test 1.1: Network Ping Test

**Purpose**: Verify basic network connectivity

```bash
# Test ping latency
ping -c 20 192.168.1.10

# Check results:
# - 0% packet loss ✅
# - Average RTT < 1ms ✅
# - No duplicates ✅
```

**Expected Output**:
```
20 packets transmitted, 20 received, 0% packet loss
rtt min/avg/max/mdev = 0.3/0.5/1.2/0.2 ms
```

**✅ PASS** if: Packet loss = 0%, Average RTT < 2ms  
**❌ FAIL** if: Any packet loss or RTT > 5ms

---

### Test 1.2: IIO Context Creation

**Purpose**: Verify IIO library can connect to E316

```bash
# List IIO devices
iio_info -u ip:192.168.1.10 | head -n 30
```

**Expected Output**:
```
Library version: 0.23
IIO context created with network backend.
Backend version: 0.23
Backend description string: 192.168.1.10 Linux ...
IIO context has X attributes:
...
IIO context has 4 devices:
    iio:device0: ad9361-phy
    iio:device1: xadc
    iio:device2: cf-ad9361-lpc
    iio:device3: cf-ad9361-dds-core-lpc
```

**✅ PASS** if: Shows "IIO context created" and lists ad9361-phy  
**❌ FAIL** if: Timeout or connection error

---

### Test 1.3: Device Attribute Access

**Purpose**: Verify we can read/write device attributes

```bash
# Read RX frequency
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i frequency

# Read TX frequency
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -o frequency

# Read RX gain
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i hardwaregain
```

**Expected Output**: Should return numeric values without errors

**✅ PASS** if: All commands return values  
**❌ FAIL** if: Any command fails or times out

---

## Hardware Functionality Tests

### Test 2.1: Set RX Frequency

**Purpose**: Test frequency tuning capability

```bash
# Set RX frequency to 450 MHz (our GPR frequency)
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i frequency 450000000

# Verify setting
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i frequency
```

**Expected Output**: `450000000`

**Test multiple frequencies**:
```bash
#!/bin/bash
for freq in 400000000 450000000 500000000; do
    echo "Testing frequency: $freq Hz"
    iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i frequency $freq
    actual=$(iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i frequency)
    if [ "$actual" = "$freq" ]; then
        echo "✅ PASS: $freq Hz"
    else
        echo "❌ FAIL: Expected $freq, got $actual"
    fi
done
```

**✅ PASS** if: All frequencies set correctly  
**❌ FAIL** if: Any frequency setting fails

---

### Test 2.2: Set RX Gain

**Purpose**: Test gain control

```bash
# Test RX gain range (0-70 dB)
for gain in 0 30 60 70; do
    echo "Testing RX gain: $gain dB"
    iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i hardwaregain $gain
    actual=$(iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i hardwaregain)
    echo "Actual: $actual dB"
done
```

**✅ PASS** if: Gain values set correctly  
**❌ FAIL** if: Gain setting fails or out of range

---

### Test 2.3: Set TX Power

**Purpose**: Test transmit power control

```bash
# Test TX power (attenuation in dB, 0 = max power, -89 = min power)
for power in 0 -10 -20 -40; do
    echo "Testing TX power: $power dBm"
    iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -o hardwaregain $power
    actual=$(iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -o hardwaregain)
    echo "Actual: $actual dBm"
done
```

**⚠️ Safety**: Ensure antenna or terminator is connected before enabling TX

**✅ PASS** if: TX power levels set correctly  
**❌ FAIL** if: TX power setting fails

---

### Test 2.4: Sample Rate Configuration

**Purpose**: Test various sample rates

```bash
# Test sample rates (in Hz)
for rate in 1000000 5000000 10000000 20000000; do
    echo "Testing sample rate: $rate sps"
    iio_attr -u ip:192.168.1.10 -d ad9361-phy sampling_frequency $rate
    actual=$(iio_attr -u ip:192.168.1.10 -d ad9361-phy sampling_frequency)
    echo "Actual: $actual sps"
done
```

**✅ PASS** if: Sample rates set correctly  
**❌ FAIL** if: Sample rate outside valid range

---

## RF Performance Tests

### Test 3.1: RX Data Capture

**Purpose**: Verify we can capture IQ data

```bash
# Capture 1024 samples from RX
iio_readdev -u ip:192.168.1.10 -s 1024 cf-ad9361-lpc | hexdump -C | head -n 20

# Capture to file
iio_readdev -u ip:192.168.1.10 -s 100000 cf-ad9361-lpc > rx_test.dat

# Check file size
ls -lh rx_test.dat

# Should be ~400KB (100000 samples × 4 bytes/sample)
```

**✅ PASS** if: Data captured successfully, file size correct  
**❌ FAIL** if: No data or read error

---

### Test 3.2: TX Signal Generation

**Purpose**: Verify TX DDS (Direct Digital Synthesis) works

```bash
# Configure TX DDS to generate 1 MHz tone
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 frequency 1000000
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 scale 0.5
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 raw 1

# Enable TX
iio_attr -u ip:192.168.1.10 -d ad9361-phy altvoltage1 powerdown 0
```

**⚠️ Safety**: Only do this with proper RF load (antenna or attenuator)

**✅ PASS** if: TX enabled without errors  
**❌ FAIL** if: TX enable fails

---

### Test 3.3: Loopback Test

**Purpose**: Verify TX → RX signal chain

**Hardware Setup**:
```
TX SMA → 30 dB Attenuator → RX SMA
```

**⚠️ IMPORTANT**: Use at least 30 dB attenuation to avoid saturating RX

**Test Script**:
```bash
# Set known frequency
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 frequency 450000000

# Set moderate RX gain
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i hardwaregain 40

# Enable TX DDS at 1 MHz offset
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 frequency 1000000
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 scale 0.5
iio_attr -u ip:192.168.1.10 -d cf-ad9361-dds-core-lpc -c voltage0 raw 1

# Capture data
iio_readdev -u ip:192.168.1.10 -s 100000 cf-ad9361-lpc > loopback_test.dat

# Analyze with Python (see below)
```

**Python Analysis**:
```python
import numpy as np
import matplotlib.pyplot as plt

# Read IQ data
data = np.fromfile('loopback_test.dat', dtype=np.int16)
iq = data[0::2] + 1j * data[1::2]

# FFT
fft = np.fft.fftshift(np.fft.fft(iq))
freq = np.fft.fftshift(np.fft.fftfreq(len(iq), 1/10e6))  # 10 MHz sample rate

# Plot
plt.figure(figsize=(12, 6))
plt.plot(freq/1e6, 20*np.log10(np.abs(fft)))
plt.xlabel('Frequency (MHz)')
plt.ylabel('Magnitude (dB)')
plt.title('Loopback Test - Should see peak at 1 MHz offset')
plt.grid(True)
plt.savefig('loopback_fft.png')
print("✅ Plot saved to loopback_fft.png")

# Find peak
peak_idx = np.argmax(np.abs(fft))
peak_freq = freq[peak_idx]
print(f"Peak at: {peak_freq/1e6:.2f} MHz (expected: 1.00 MHz)")
```

**✅ PASS** if: Clear peak visible at 1 MHz offset  
**❌ FAIL** if: No peak or peak at wrong frequency

---

## GNU Radio Integration Tests

### Test 4.1: Import gr-iio

**Purpose**: Verify GNU Radio can access IIO blocks

```python
#!/usr/bin/env python3
from gnuradio import gr, blocks, iio
print("✅ gr-iio imported successfully")

# List available IIO sources
print("\nAvailable IIO blocks:")
print("- iio.fmcomms2_source")
print("- iio.fmcomms2_sink")
print("- iio.pluto_source")  # Alternative name
print("- iio.pluto_sink")
```

**✅ PASS** if: No import errors  
**❌ FAIL** if: ImportError

---

### Test 4.2: Simple GNU Radio Flowgraph

**Purpose**: Create minimal RX flowgraph

```python
#!/usr/bin/env python3
"""
Simple GNU Radio flowgraph to test E316
"""
from gnuradio import gr, blocks, iio
import time

class test_flowgraph(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "ANTSDR E316 Test")
        
        # IIO Source (RX)
        self.iio_source = iio.fmcomms2_source_fc32(
            "ip:192.168.1.10",
            [True, False],  # Enable RX1, disable RX2
            32768  # Buffer size
        )
        self.iio_source.set_params(
            450000000,  # Frequency: 450 MHz
            10000000,   # Sample rate: 10 MSPS
            10000000,   # Bandwidth: 10 MHz
            True,       # Quadrature
            True,       # RF DC
            True,       # BB DC
            "manual",   # Gain mode
            60,         # Gain: 60 dB
            "",         # Filter
            True        # Auto filter
        )
        
        # File Sink
        self.file_sink = blocks.file_sink(
            gr.sizeof_gr_complex,
            "test_capture.dat",
            False
        )
        
        # Connect blocks
        self.connect((self.iio_source, 0), (self.file_sink, 0))

if __name__ == '__main__':
    print("Creating flowgraph...")
    tb = test_flowgraph()
    
    print("Starting capture (5 seconds)...")
    tb.start()
    time.sleep(5)
    tb.stop()
    tb.wait()
    
    print("✅ Test complete! Data saved to test_capture.dat")
    
    # Check file size
    import os
    size = os.path.getsize("test_capture.dat")
    expected = 5 * 10e6 * 8  # 5 sec × 10 MSPS × 8 bytes
    print(f"File size: {size/1e6:.1f} MB (expected ~{expected/1e6:.1f} MB)")
    
    if size > expected * 0.9:  # Within 90% of expected
        print("✅ PASS: Correct amount of data captured")
    else:
        print("❌ FAIL: Not enough data captured")
```

**Run Test**:
```bash
python3 test_flowgraph.py
```

**✅ PASS** if: File created with correct size  
**❌ FAIL** if: Error or file too small

---

## Python API Tests

### Test 5.1: Python IIO Context

**Purpose**: Test Python libiio bindings

```python
#!/usr/bin/env python3
import iio

# Create context
ctx = iio.Context("ip:192.168.1.10")
print(f"✅ Connected to: {ctx.name}")
print(f"   Description: {ctx.description}")

# List devices
print(f"\n📡 Found {len(ctx.devices)} devices:")
for dev in ctx.devices:
    print(f"   - {dev.name} ({dev.id})")

# Get AD9361 device
phy = ctx.find_device("ad9361-phy")
if phy:
    print(f"\n✅ Found AD9361 PHY")
    print(f"   Channels: {len(phy.channels)}")
else:
    print("❌ AD9361 PHY not found!")

# Test channel access
rx_chan = phy.find_channel("voltage0", False)  # RX channel
if rx_chan:
    freq = rx_chan.attrs["frequency"].value
    print(f"   RX Frequency: {int(freq)/1e6:.1f} MHz")
else:
    print("❌ RX channel not found!")
```

**✅ PASS** if: All devices found and attributes readable  
**❌ FAIL** if: Any errors or missing devices

---

### Test 5.2: Set Parameters via Python

**Purpose**: Test complete Python control

```python
#!/usr/bin/env python3
import iio
import sys

def configure_e316(freq_mhz=450, rx_gain=60, tx_power=-10):
    """Configure ANTSDR E316 via Python"""
    try:
        # Connect
        ctx = iio.Context("ip:192.168.1.10")
        phy = ctx.find_device("ad9361-phy")
        
        # Get channels
        rx = phy.find_channel("voltage0", False)  # RX
        tx = phy.find_channel("voltage0", True)   # TX
        
        # Set RX frequency
        rx.attrs["frequency"].value = str(int(freq_mhz * 1e6))
        # Set RX gain
        rx.attrs["hardwaregain"].value = str(int(rx_gain))
        
        # Set TX frequency
        tx.attrs["frequency"].value = str(int(freq_mhz * 1e6))
        # Set TX power
        tx.attrs["hardwaregain"].value = str(int(tx_power))
        
        # Verify
        print(f"✅ Configuration applied:")
        print(f"   RX Freq: {int(rx.attrs['frequency'].value)/1e6:.1f} MHz")
        print(f"   RX Gain: {rx.attrs['hardwaregain'].value} dB")
        print(f"   TX Freq: {int(tx.attrs['frequency'].value)/1e6:.1f} MHz")
        print(f"   TX Power: {tx.attrs['hardwaregain'].value} dBm")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = configure_e316(freq_mhz=450, rx_gain=60, tx_power=-10)
    sys.exit(0 if success else 1)
```

**✅ PASS** if: Configuration succeeds  
**❌ FAIL** if: Any exception raised

---

## GPS Tests

### Test 6.1: GPS Detection

**Purpose**: Verify GPS module is accessible

```bash
# Check for GPS device
iio_attr -u ip:192.168.1.10 | grep -i gps

# If GPS is available, read position
iio_attr -u ip:192.168.1.10 -d gps
```

**Note**: GPS requires external antenna and clear sky view

**✅ PASS** if: GPS device listed  
**❌ FAIL** if: No GPS device found

---

### Test 6.2: GPS Lock Test

**Purpose**: Test GPS acquisition

```bash
# This requires GPS antenna with sky view
# May take 30-120 seconds for first fix

# Monitor GPS status
watch -n 1 'iio_attr -u ip:192.168.1.10 -d gps 2>/dev/null | grep -E "(latitude|longitude|altitude)"'
```

**✅ PASS** if: GPS coordinates acquired  
**⚠️ SKIP** if: No GPS antenna or indoor

---

## Performance Benchmarks

### Test 7.1: Throughput Test

**Purpose**: Measure maximum sustainable data rate

```bash
# Capture 100M samples (~800 MB) and measure time
time iio_readdev -u ip:192.168.1.10 -s 100000000 cf-ad9361-lpc > /dev/null

# Calculate throughput:
# 100M samples × 4 bytes = 400 MB
# Throughput = 400 MB / elapsed_time
```

**Expected**: > 50 MB/s (400 Mbps)

**✅ PASS** if: > 30 MB/s  
**⚠️ MARGINAL** if: 20-30 MB/s  
**❌ FAIL** if: < 20 MB/s

---

### Test 7.2: Latency Test

**Purpose**: Measure command latency

```python
#!/usr/bin/env python3
import iio
import time

ctx = iio.Context("ip:192.168.1.10")
phy = ctx.find_device("ad9361-phy")
rx = phy.find_channel("voltage0", False)

# Measure read latency
latencies = []
for i in range(100):
    start = time.time()
    freq = rx.attrs["frequency"].value
    latency = (time.time() - start) * 1000  # ms
    latencies.append(latency)

import numpy as np
print(f"Latency statistics (ms):")
print(f"  Min: {np.min(latencies):.2f}")
print(f"  Avg: {np.mean(latencies):.2f}")
print(f"  Max: {np.max(latencies):.2f}")

if np.mean(latencies) < 5:
    print("✅ PASS: Low latency")
else:
    print("⚠️ MARGINAL: High latency")
```

**✅ PASS** if: Average < 5ms  
**❌ FAIL** if: Average > 10ms

---

## Automated Test Script

Complete automated test script:

```bash
#!/bin/bash
# save as: run_all_tests.sh

E316_IP="192.168.1.10"
IIO_URI="ip:$E316_IP"

echo "========================================"
echo "ANTSDR E316 Complete Test Suite"
echo "========================================"

# Test 1: Network
echo -e "\n[Test 1] Network Connectivity"
if ping -c 3 -W 2 $E316_IP > /dev/null 2>&1; then
    echo "✅ PASS: E316 reachable"
else
    echo "❌ FAIL: Cannot ping E316"
    exit 1
fi

# Test 2: IIO Context
echo -e "\n[Test 2] IIO Context Creation"
if timeout 5 iio_info -u $IIO_URI > /dev/null 2>&1; then
    echo "✅ PASS: IIO connection OK"
else
    echo "❌ FAIL: IIO connection failed"
    exit 1
fi

# Test 3: Device Detection
echo -e "\n[Test 3] Device Detection"
if iio_info -u $IIO_URI | grep -q "ad9361-phy"; then
    echo "✅ PASS: AD9361 detected"
else
    echo "❌ FAIL: AD9361 not found"
    exit 1
fi

# Test 4: Frequency Setting
echo -e "\n[Test 4] Frequency Control"
iio_attr -u $IIO_URI -d ad9361-phy -c voltage0 -i frequency 450000000 > /dev/null 2>&1
actual=$(iio_attr -u $IIO_URI -d ad9361-phy -c voltage0 -i frequency 2>/dev/null)
if [ "$actual" = "450000000" ]; then
    echo "✅ PASS: Frequency set to 450 MHz"
else
    echo "❌ FAIL: Frequency setting failed"
    exit 1
fi

# Test 5: Data Capture
echo -e "\n[Test 5] Data Capture"
if timeout 10 iio_readdev -u $IIO_URI -s 1000 cf-ad9361-lpc > /tmp/test.dat 2>/dev/null; then
    size=$(stat -f%z /tmp/test.dat 2>/dev/null || stat -c%s /tmp/test.dat 2>/dev/null)
    if [ "$size" -gt 1000 ]; then
        echo "✅ PASS: Data captured ($size bytes)"
    else
        echo "❌ FAIL: Insufficient data"
        exit 1
    fi
else
    echo "❌ FAIL: Data capture failed"
    exit 1
fi

echo -e "\n========================================"
echo "✅ ALL TESTS PASSED"
echo "========================================"
```

**Run All Tests**:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## Test Results Template

Use this template to record your test results:

```markdown
# ANTSDR E316 Test Results

**Date**: YYYY-MM-DD
**Operator**: [Your Name]
**E316 S/N**: [Serial Number]
**Xubuntu Version**: 22.04

## Test Results

| Test | Description | Result | Notes |
|------|-------------|--------|-------|
| 1.1 | Network Ping | ✅ PASS | 0% loss, 0.5ms avg |
| 1.2 | IIO Context | ✅ PASS | |
| 1.3 | Device Attributes | ✅ PASS | |
| 2.1 | RX Frequency | ✅ PASS | 400-500 MHz OK |
| 2.2 | RX Gain | ✅ PASS | 0-70 dB OK |
| 2.3 | TX Power | ✅ PASS | |
| 2.4 | Sample Rate | ✅ PASS | Up to 20 MSPS |
| 3.1 | RX Data Capture | ✅ PASS | |
| 3.2 | TX Generation | ✅ PASS | |
| 3.3 | Loopback | ✅ PASS | Peak at 1 MHz |
| 4.1 | gr-iio Import | ✅ PASS | |
| 4.2 | GRC Flowgraph | ✅ PASS | |
| 5.1 | Python IIO | ✅ PASS | |
| 5.2 | Python Control | ✅ PASS | |
| 6.1 | GPS Detection | ⚠️ SKIP | No antenna |
| 7.1 | Throughput | ✅ PASS | 45 MB/s |
| 7.2 | Latency | ✅ PASS | 2.1 ms avg |

## Summary

- **Total Tests**: 17
- **Passed**: 15
- **Failed**: 0
- **Skipped**: 2

## Conclusion

System is fully operational and ready for GPR application.

**Approved by**: [Signature]
```

---

## Next Steps

✅ Once all tests pass, proceed to:
- **05_GPR_PROJECT_SETUP.md** - Configure GPR project
- **../../../README.md** - Run the full GPR system

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-24  
**Tested With**: Xubuntu 22.04 LTS, ANTSDR E316

