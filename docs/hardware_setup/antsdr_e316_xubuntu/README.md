# ANTSDR E316 Setup Guide for Xubuntu 22.04

Complete step-by-step guide for connecting and testing ANTSDR E316 with Xubuntu Linux platform.

## 📚 Documentation Index

Follow these documents in order for a complete setup:

### 1️⃣ [Hardware Overview](01_HARDWARE_OVERVIEW.md)
**Read this first!**
- Hardware specifications and components
- **Button configuration** (BTN1, BTN2)
- **Jumper settings** (JP1, JP2) - Critical for connection mode
- LED indicators and their meanings
- Power requirements and safety
- Pre-connection checklist

**Key Topics**:
- Setting JP1 for power source (USB vs 12V)
- Setting JP2 for interface mode (Ethernet vs USB)
- Understanding LED status during boot
- RF connector safety

---

### 2️⃣ [Network Configuration](02_XUBUNTU_NETWORK_SETUP.md)
**Network setup for Ethernet and USB connections**
- Ethernet connection setup (recommended for GPR)
- USB connection setup (alternative)
- Multiple configuration methods (GUI, netplan, ifconfig)
- Connectivity testing
- Comprehensive troubleshooting

**Key Topics**:
- Configuring static IP (192.168.1.100)
- Testing ping connectivity
- Ethernet vs USB comparison
- Network diagnostic commands

---

### 3️⃣ [Software Installation](03_SOFTWARE_INSTALLATION.md)
**Install all required software packages**
- libiio (IIO library for hardware access)
- GNU Radio (signal processing framework)
- gr-iio (GNU Radio IIO blocks)
- Python dependencies
- Optional tools (IIO Oscilloscope, GQRX, etc.)

**Key Topics**:
- Installing from repositories vs building from source
- Environment variable configuration
- Verification tests
- Troubleshooting installation issues

---

### 4️⃣ [Testing Procedures](04_TESTING_PROCEDURES.md)
**Comprehensive hardware and software testing**
- Basic connectivity tests
- Hardware functionality tests (frequency, gain, power)
- RF performance tests (loopback)
- GNU Radio integration tests
- Python API tests
- GPS tests (optional)
- Performance benchmarks
- Automated test scripts

**Key Topics**:
- Step-by-step test procedures
- Pass/fail criteria
- Test result documentation
- Performance benchmarking

---

## 🚀 Quick Start

If you're experienced with SDR and Linux, here's the fast track:

```bash
# 1. Hardware Setup
#    - Set JP1 to 2-3 (12V power)
#    - Set JP2 to 1-2 (Ethernet mode)
#    - Connect Ethernet cable
#    - Connect 12V power

# 2. Network Configuration
sudo nmcli connection add type ethernet con-name ANTSDR_E316 \
    ifname enp3s0 ipv4.method manual ipv4.addresses 192.168.1.100/24

# 3. Test Connection
ping -c 4 192.168.1.10

# 4. Install Software
sudo apt update
sudo apt install -y libiio-utils libiio0 gnuradio gr-iio python3-libiio

# 5. Verify IIO
iio_info -u ip:192.168.1.10

# 6. Run Tests
./run_all_tests.sh
```

## 🎯 Connection Quick Reference

### Ethernet Connection (Recommended for GPR)
```
Hardware:
  JP1: Position 2-3 (12V external power)
  JP2: Position 1-2 (Ethernet mode)
  Power: 12V/2A DC supply
  Cable: Gigabit Ethernet to computer

Network:
  E316 IP: 192.168.1.10
  Host IP: 192.168.1.100
  Subnet:  255.255.255.0

Test:
  ping 192.168.1.10
  iio_info -u ip:192.168.1.10
```

### USB Connection (Alternative)
```
Hardware:
  JP1: Position 1-2 or 2-3
  JP2: Position 2-3 (USB Gadget mode)
  Cable: Micro-USB to computer

Network:
  E316 IP: 192.168.2.1
  Host IP: 192.168.2.2 (auto)
  Interface: usb0

Test:
  ping 192.168.2.1
  iio_info -u usb:
```

## ⚠️ Critical Information

### MUST READ Before Connecting

1. **Jumper Settings**:
   - **JP2 must be set correctly** for your connection type
   - Ethernet mode: JP2 = 1-2 (default)
   - USB mode: JP2 = 2-3

2. **Power Requirements**:
   - Ethernet mode **requires 12V external power**
   - JP1 = 2-3 for Ethernet with 12V supply
   - Never connect both USB and 12V simultaneously

3. **RF Safety**:
   - **Always** connect antennas or terminators to TX/RX ports
   - Never transmit into open/shorted RF connectors
   - Use ≥30 dB attenuation for loopback tests

4. **Network Configuration**:
   - Host must be on 192.168.1.x subnet
   - Host IP cannot be .10 (E316's address)
   - Disable DHCP on Ethernet interface

## 📋 Hardware Checklist

Before starting:
- [ ] ANTSDR E316 board
- [ ] 12V/2A power supply (5.5mm × 2.1mm barrel jack)
- [ ] Ethernet cable (CAT5e or better)
- [ ] RF antennas or 50Ω terminators
- [ ] GPS antenna with U.FL connector (optional)
- [ ] Computer with Xubuntu 22.04 installed
- [ ] Small screwdriver (for jumper adjustment)

## 🔧 Troubleshooting Quick Links

**Cannot ping E316**:
- Check LED3 (Ethernet Link) - should be ON
- Verify JP2 is in position 1-2
- Confirm host IP is 192.168.1.x (not .10)
- See [Network Setup - Troubleshooting](02_XUBUNTU_NETWORK_SETUP.md#troubleshooting)

**IIO tools cannot connect**:
- Verify ping works first
- Check firewall: `sudo ufw status`
- Test with: `telnet 192.168.1.10 30431`
- See [Software Installation - Troubleshooting](03_SOFTWARE_INSTALLATION.md#troubleshooting-installation)

**No data from device**:
- Verify device attributes are readable
- Check sample rate is set
- Run loopback test
- See [Testing Procedures - Test 3.1](04_TESTING_PROCEDURES.md#test-31-rx-data-capture)

## 📊 LED Status Reference

Normal operation:
```
LED1 (Green):   🟢 Solid ON  - Power good
LED2 (Yellow):  🟡 Solid ON  - FPGA configured
LED3 (Blue):    🔵 Solid ON  - Ethernet connected
LED4 (Red):     🔴 Blinking  - Data activity
```

Boot sequence takes 20-30 seconds. See [Hardware Overview](01_HARDWARE_OVERVIEW.md#led-indicators) for details.

## 🎓 Learning Path

### For Beginners
1. Read all 4 documents in order
2. Follow every step carefully
3. Run all tests to verify setup
4. Keep documents open for reference

### For Experienced Users
1. Review Hardware Overview (jumpers!)
2. Skim Network Configuration
3. Install software
4. Run automated test script
5. Refer back as needed

## 📦 Software Versions

This guide is tested with:
- **OS**: Xubuntu 22.04 LTS
- **libiio**: 0.23+
- **GNU Radio**: 3.10.x
- **gr-iio**: 0.3+
- **Python**: 3.10+

Other versions may work but are untested.

## 🔗 Additional Resources

### Official Documentation
- **ANTSDR Wiki**: https://wiki.antsdr.com/
- **AD9361 Datasheet**: https://www.analog.com/en/products/ad9364.html
- **GNU Radio Manual**: https://wiki.gnuradio.org/
- **libiio Documentation**: https://wiki.analog.com/resources/tools-software/linux-software/libiio

### Community Resources
- **ANTSDR GitHub**: https://github.com/MicroPhase/antsdr
- **GNU Radio Discourse**: https://discourse.gnuradio.org/
- **SDR Reddit**: r/RTLSDR, r/amateurradio

### Project Specific
- [Main Project README](../../../README.md)
- [Calibration Procedures](../../calibration_procedures.md)
- [User Manual](../../user_manual.md)

## 📝 Documentation Notes

### Document Maintenance
- **Created**: 2025-10-24
- **Version**: 1.0
- **Tested Platform**: Xubuntu 22.04 LTS
- **Hardware**: ANTSDR E316 Rev 1.0

### Contributing
If you find errors or have improvements:
1. Test your changes thoroughly
2. Document what you changed
3. Submit a pull request or issue

### Feedback
Found these docs helpful? Have suggestions? Let us know!

## ✅ Completion Checklist

After completing all setup steps, you should have:

- [ ] E316 powered on with all LEDs in correct state
- [ ] Network connection working (ping succeeds)
- [ ] IIO tools installed and can connect to device
- [ ] GNU Radio installed with gr-iio blocks
- [ ] Python environment configured
- [ ] All connectivity tests passing
- [ ] Hardware functionality tests passing
- [ ] RF performance tests passing (loopback)
- [ ] Can capture IQ data successfully
- [ ] Can control frequency, gain, and power

Once complete, you're ready to run the GPR system!

---

## 🎯 Next Steps

After completing this setup guide:

1. **Configure GPR Project**
   ```bash
   cd /path/to/GNURADIO
   python init_project.py
   ```

2. **Test Hardware Control**
   ```bash
   python src/hardware/antsdr_control.py
   ```

3. **Launch Dashboard**
   ```bash
   streamlit run src/dashboard/gpr_dashboard.py
   ```

4. **Run Calibration**
   ```bash
   python src/testing/run_calibration_tests.py --mode quick
   ```

See the main [Project README](../../../README.md) for full GPR system operation.

---

**Happy SDR-ing! 📡**

*For questions or issues, refer to the troubleshooting sections in each document or check the project issues page.*

