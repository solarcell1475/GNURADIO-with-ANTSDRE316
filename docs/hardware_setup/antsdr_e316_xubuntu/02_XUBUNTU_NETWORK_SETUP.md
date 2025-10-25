# Xubuntu 22.04 Network Configuration for ANTSDR E316

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Ethernet Connection Setup](#ethernet-connection-setup)
- [USB Connection Setup](#usb-connection-setup)
- [Network Configuration Methods](#network-configuration-methods)
- [Testing Connectivity](#testing-connectivity)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum System Requirements
- **OS**: Xubuntu 22.04 LTS (64-bit)
- **RAM**: 4 GB (8 GB recommended)
- **Processor**: Intel Core i3 or AMD equivalent (i5/i7 recommended)
- **Network**: Gigabit Ethernet port
- **USB**: USB 2.0 port (for USB connection)
- **Disk Space**: 10 GB free for software installation

### Required Software Packages
```bash
# Core packages
- libiio-utils (IIO tools)
- libiio0 (IIO library)
- python3-libiio (Python bindings)
- iiod (IIO daemon)
- network-manager (Network management)
```

---

## Ethernet Connection Setup (Recommended)

### Step-by-Step Ethernet Configuration

#### Method 1: Using Network Manager GUI (Easiest)

**Step 1: Connect Hardware**
```
1. Ensure ANTSDR E316 is powered OFF
2. Set JP1 to position 2-3 (12V external power)
3. Set JP2 to position 1-2 (Ethernet mode)
4. Connect Ethernet cable from E316 to computer
5. Connect 12V power supply (don't power on yet)
```

**Step 2: Configure Network Interface**

1. Click the **Network Manager icon** in system tray (top right)
2. Click **"Edit Connections..."**

   ![Network Manager Menu](images/network_manager_menu.png)

3. Click **"+ Add"** button to add new connection

4. Select **"Ethernet"** connection type, click **"Create..."**

5. Configure the connection:

   **General Tab**:
   - ✓ Check "Automatically connect to this network"
   - Connection name: `ANTSDR_E316`
   
   **Ethernet Tab**:
   - Device: Select your Ethernet interface (e.g., `enp3s0`, `eth0`)
   
   **IPv4 Settings Tab**:
   ```
   Method: Manual
   
   Addresses:
   ┌────────────────┬──────────┬─────────┐
   │ Address        │ Netmask  │ Gateway │
   ├────────────────┼──────────┼─────────┤
   │ 192.168.1.100  │    24    │ (empty) │
   └────────────────┴──────────┴─────────┘
   
   DNS servers: (leave empty)
   
   ☐ Require IPv4 addressing for this connection
   ```
   
   **IPv6 Settings Tab**:
   ```
   Method: Disabled
   ```

6. Click **"Save"**

7. Activate the connection:
   - Click Network Manager icon
   - Select "ANTSDR_E316"
   - Wait for connection (should connect immediately)

**Step 3: Power On ANTSDR E316**
```
1. Apply 12V power to E316
2. Watch LED sequence:
   - LED1 (Power): ON immediately
   - LED2 (FPGA): Blinks then solid (2-5 sec)
   - LED3 (Eth Link): ON after ~15-30 seconds
   - LED4 (Activity): Occasional blinks
3. Wait 30 seconds for full boot
```

**Step 4: Verify Connection**
```bash
# Check network interface is up
ip addr show

# Should see something like:
# 3: enp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
#     inet 192.168.1.100/24 brd 192.168.1.255 scope global enp3s0

# Ping the E316
ping -c 4 192.168.1.10

# Expected output:
# 64 bytes from 192.168.1.10: icmp_seq=1 ttl=64 time=0.5 ms
```

#### Method 2: Using Command Line (netplan)

**Step 1: Identify Network Interface**
```bash
# List network interfaces
ip link show

# Output example:
# 1: lo: <LOOPBACK,UP,LOWER_UP>...
# 2: wlp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP>...  ← WiFi
# 3: enp3s0: <BROADCAST,MULTICAST>...              ← Ethernet (this one!)
```

Note the Ethernet interface name (e.g., `enp3s0`, `eth0`, `eno1`)

**Step 2: Create Netplan Configuration**

```bash
# Create/edit netplan config file
sudo nano /etc/netplan/02-antsdr-ethernet.yaml
```

Add the following content:
```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    enp3s0:  # ← Replace with YOUR interface name
      dhcp4: no
      dhcp6: no
      addresses:
        - 192.168.1.100/24
      optional: true
```

**Step 3: Apply Configuration**
```bash
# Test configuration (doesn't apply changes)
sudo netplan try

# If test succeeds, apply permanently
sudo netplan apply

# Verify interface is configured
ip addr show enp3s0
```

**Step 4: Power On E316 and Test**
```bash
# Power on E316 (LED sequence should complete)

# Test connectivity
ping -c 4 192.168.1.10
```

#### Method 3: Using ifconfig (Legacy, but quick)

```bash
# Identify interface
ip link show

# Configure interface (temporary, lost on reboot)
sudo ifconfig enp3s0 192.168.1.100 netmask 255.255.255.0 up

# Verify
ifconfig enp3s0

# Power on E316 and test
ping -c 4 192.168.1.10
```

**To make permanent**:
```bash
# Edit interfaces file
sudo nano /etc/network/interfaces

# Add:
auto enp3s0
iface enp3s0 inet static
    address 192.168.1.100
    netmask 255.255.255.0

# Restart networking
sudo systemctl restart networking
```

---

## USB Connection Setup (Alternative)

### USB Gadget Mode Configuration

**Step 1: Configure E316 for USB Mode**
```
Hardware setup:
1. Power OFF E316
2. Set JP1 to position 1-2 (USB power) or 2-3 (12V)
3. Set JP2 to position 2-3 (USB Gadget mode)  ← IMPORTANT!
4. Connect Micro-USB cable (E316 to computer)
5. If JP1=2-3, also connect 12V power
```

**Step 2: Detect USB Device**
```bash
# Connect USB cable to E316

# Check USB detection
lsusb

# Should see Analog Devices device:
# Bus 001 Device 005: ID 0456:b673 Analog Devices Inc.

# Check kernel messages
dmesg | tail -n 20

# Should see messages about new USB device and network interface
```

**Step 3: Configure USB Network Interface**

The E316 will appear as a USB network device (e.g., `usb0`, `enx...`)

```bash
# Find the USB network interface
ip link show | grep usb

# Example output:
# 4: usb0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN

# Configure USB interface
sudo ifconfig usb0 192.168.2.2 netmask 255.255.255.0 up

# Verify
ifconfig usb0
```

**Step 4: Test USB Connection**
```bash
# Ping E316 over USB
ping -c 4 192.168.2.1

# Expected: replies from 192.168.2.1
```

### USB vs Ethernet Comparison

| Feature | Ethernet (JP2=1-2) | USB Gadget (JP2=2-3) |
|---------|-------------------|---------------------|
| **Speed** | Up to 1 Gbps | Up to 480 Mbps |
| **Latency** | Lower (~0.5ms) | Higher (~2ms) |
| **Power** | Requires 12V supply | Can use USB power |
| **Stability** | More stable | May have dropouts |
| **Setup** | Slightly complex | Plug and play |
| **Recommended for GPR** | ✅ Yes | ⚠️ For testing only |

**Recommendation**: Use **Ethernet mode** for the GPR system due to better performance and stability.

---

## Network Configuration Methods Summary

### Quick Reference Table

| Method | Difficulty | Persistence | Best For |
|--------|-----------|-------------|----------|
| **Network Manager GUI** | Easy | Permanent | Beginners |
| **netplan** | Medium | Permanent | Clean configuration |
| **ifconfig** | Easy | Temporary | Quick testing |
| **nmcli** | Medium | Permanent | Automation/scripts |

### Using nmcli (Command Line Network Manager)

```bash
# List connections
nmcli connection show

# Create new connection for E316
nmcli connection add \
    type ethernet \
    con-name ANTSDR_E316 \
    ifname enp3s0 \
    ipv4.method manual \
    ipv4.addresses 192.168.1.100/24

# Activate connection
nmcli connection up ANTSDR_E316

# Verify
nmcli device status
```

---

## Testing Connectivity

### Basic Connectivity Tests

#### Test 1: Ping Test
```bash
# Continuous ping (Ctrl+C to stop)
ping 192.168.1.10

# Expected output:
# 64 bytes from 192.168.1.10: icmp_seq=1 ttl=64 time=0.5 ms
# 64 bytes from 192.168.1.10: icmp_seq=2 ttl=64 time=0.4 ms
# 64 bytes from 192.168.1.10: icmp_seq=3 ttl=64 time=0.6 ms

# Check statistics:
# - 0% packet loss ✅
# - RTT min/avg/max < 5ms ✅
```

#### Test 2: ARP Table Check
```bash
# Check ARP resolution
arp -a | grep 192.168.1.10

# Should show MAC address:
# ? (192.168.1.10) at xx:xx:xx:xx:xx:xx [ether] on enp3s0
```

#### Test 3: Routing Table
```bash
# Verify route to E316
ip route get 192.168.1.10

# Should show direct route via your interface:
# 192.168.1.10 dev enp3s0 src 192.168.1.100 uid 1000
```

### IIO Connectivity Tests

#### Test 4: IIO Device Detection
```bash
# List IIO devices over network
iio_info -u ip:192.168.1.10

# Expected output (partial):
# Library version: 0.23 (git tag: v0.23)
# Compiled with backends: local xml ip usb
# IIO context created with network backend.
# Backend version: 0.23 (git tag: v0.23)
# Backend description string: 192.168.1.10 Linux ...
# IIO context has 2 attributes:
# ...
# IIO context has 4 devices:
#     iio:device0: ad9361-phy
#     iio:device1: xadc
#     ...
```

**✅ Success indicators**:
- Shows "IIO context created"
- Lists ad9361-phy device
- No timeout errors

#### Test 5: Read Device Attributes
```bash
# Read AD9361 RF frequency
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 frequency

# Should return a frequency value:
# 2400000000 (2.4 GHz default)

# Read RX gain
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 -i hardwaregain

# Should return gain value:
# 60.000000 dB (or similar)
```

#### Test 6: Simple IIO Read
```bash
# Capture a small amount of data
iio_readdev -u ip:192.168.1.10 -s 1024 cf-ad9361-lpc-rx | hexdump -C | head

# Should show IQ data samples
# If you see hex data output, IIO is working! ✅
```

### Performance Tests

#### Test 7: Bandwidth Test
```bash
# Use iperf3 to test network throughput (if iperf3 is installed on E316)
# This is advanced and optional

# For basic throughput test, use iio_readdev:
iio_readdev -u ip:192.168.1.10 -s 10000000 cf-ad9361-lpc-rx > /dev/null

# Monitor network traffic:
# - Should sustain > 100 Mbps for normal operation
# - Watch for dropped packets (should be 0)
```

#### Test 8: Latency Test
```bash
# Measure ping latency statistics
ping -c 100 192.168.1.10 | tail -n 5

# Expected statistics:
# rtt min/avg/max/mdev = 0.3/0.5/2.0/0.2 ms
#
# Good values:
# - Average: < 1 ms
# - Max: < 5 ms
# - Packet loss: 0%
```

---

## Troubleshooting

### Problem 1: Cannot Ping 192.168.1.10

**Symptoms**:
```bash
ping 192.168.1.10
# Destination Host Unreachable
```

**Diagnosis Steps**:

1. **Check E316 Power and LEDs**:
   ```bash
   # Verify:
   # - LED1 (Power) is ON
   # - LED2 (FPGA) is solid ON (not blinking)
   # - LED3 (Ethernet) is ON
   ```
   If LED3 is OFF → Cable or link problem

2. **Check Physical Connection**:
   ```bash
   # Check link status
   ethtool enp3s0 | grep "Link detected"
   
   # Should show: Link detected: yes
   ```

3. **Verify IP Configuration**:
   ```bash
   # Check your IP address
   ip addr show enp3s0
   
   # Should show: 192.168.1.100/24
   ```

4. **Check Jumper Settings**:
   - JP2 must be in position 1-2 for Ethernet mode
   - Verify visually on the board

5. **Try Different Cable**:
   - Use known-good Ethernet cable
   - Try different Ethernet port on computer

**Solutions**:
```bash
# Solution A: Restart network interface
sudo ip link set enp3s0 down
sudo ip link set enp3s0 up
sudo ip addr add 192.168.1.100/24 dev enp3s0

# Solution B: Reset E316
# Press BTN1 (reset button) for 1 second

# Solution C: Power cycle E316
# Disconnect 12V power, wait 10 seconds, reconnect

# Solution D: Disable firewall temporarily
sudo ufw disable
# Try ping again, then re-enable: sudo ufw enable
```

### Problem 2: IIO Tools Cannot Connect

**Symptoms**:
```bash
iio_info -u ip:192.168.1.10
# Timeout error or "No IIO context"
```

**Diagnosis**:

1. **Verify Ping Works**:
   ```bash
   ping -c 4 192.168.1.10
   # Must succeed before IIO will work
   ```

2. **Check iiod Service on E316**:
   ```bash
   # Try to connect to iiod port
   telnet 192.168.1.10 30431
   
   # Should connect (Ctrl+] then 'quit' to exit)
   ```

3. **Check Firewall**:
   ```bash
   # List firewall rules
   sudo iptables -L -n | grep 30431
   
   # Temporarily disable firewall
   sudo ufw disable
   ```

**Solutions**:
```bash
# Solution A: Reinstall IIO tools
sudo apt update
sudo apt install --reinstall libiio-utils libiio0

# Solution B: Allow IIO port through firewall
sudo ufw allow from 192.168.1.0/24 to any port 30431

# Solution C: Reset E316 (press BTN1)

# Solution D: Use USB connection instead (change JP2)
```

### Problem 3: Slow or Unstable Connection

**Symptoms**:
- High ping times (> 5ms)
- Packet loss
- Intermittent disconnections

**Diagnosis**:
```bash
# Monitor ping continuously
ping 192.168.1.10

# Check for errors on interface
ip -s link show enp3s0
# Look at RX errors, TX errors (should be 0)

# Check network speed negotiation
ethtool enp3s0 | grep Speed
# Should show: Speed: 1000Mb/s
```

**Solutions**:
```bash
# Solution A: Force gigabit speed
sudo ethtool -s enp3s0 speed 1000 duplex full autoneg off

# Solution B: Disable power saving
sudo ethtool -s enp3s0 wol d
sudo iw dev wlp2s0 set power_save off  # If WiFi interferes

# Solution C: Use quality Ethernet cable (CAT6)

# Solution D: Direct connection (no switch between devices)
```

### Problem 4: Connection Works but No Data

**Symptoms**:
- Ping works
- iio_info works
- But iio_readdev returns no data or errors

**Solutions**:
```bash
# Check device attributes
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0

# Ensure sampling is enabled
iio_attr -u ip:192.168.1.10 -d ad9361-phy -c voltage0 sampling_frequency 10000000

# Check buffer size
iio_attr -u ip:192.168.1.10 -d iio:device2 buffer/length

# Try Python test script (see next section)
```

### Problem 5: USB Connection Not Detected

**Symptoms**:
- USB cable connected
- No usb0 interface appears

**Solutions**:
```bash
# Verify JP2 is in position 2-3 (USB Gadget mode)

# Check USB detection
lsusb | grep -i analog
dmesg | grep -i usb | tail -n 20

# Load USB ethernet drivers (if needed)
sudo modprobe rndis_host
sudo modprobe cdc_ether

# Check for usb interface
ip link show | grep -E "(usb|enx)"
```

---

## Network Diagnostic Commands Cheat Sheet

```bash
# Interface status
ip addr show              # Show all interfaces and IPs
ip link show             # Show link status
ethtool enp3s0           # Show detailed interface info

# Connectivity
ping 192.168.1.10        # Basic connectivity test
traceroute 192.168.1.10  # Route tracing
arp -a                   # ARP table (MAC addresses)

# Network statistics
netstat -i               # Interface statistics
ss -s                    # Socket statistics
iftop                    # Real-time bandwidth monitor

# IIO specific
iio_info -u ip:192.168.1.10                    # List IIO devices
iio_attr -u ip:192.168.1.10                    # List all attributes
iio_readdev -u ip:192.168.1.10 -s 1024 ...    # Read data

# Firewall
sudo ufw status          # Check firewall status
sudo iptables -L -n      # List firewall rules

# System logs
dmesg | grep eth         # Ethernet kernel messages
journalctl -xe           # System journal
```

---

## Next Steps

✅ Once all connectivity tests pass, proceed to:
- **03_SOFTWARE_INSTALLATION.md** - Install required software packages
- **04_TESTING_PROCEDURES.md** - Run comprehensive hardware tests

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-24  
**Tested With**: Xubuntu 22.04 LTS, ANTSDR E316 Rev 1.0

