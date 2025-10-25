# ANTSDR E316 Hardware Overview and Configuration

## 📋 Table of Contents
- [Hardware Specifications](#hardware-specifications)
- [Physical Components](#physical-components)
- [Button and Jumper Configuration](#button-and-jumper-configuration)
- [LED Indicators](#led-indicators)
- [Connection Interfaces](#connection-interfaces)
- [Power Requirements](#power-requirements)

---

## Hardware Specifications

### ANTSDR E316 Key Specifications

| Specification | Details |
|--------------|---------|
| **RF Chipset** | Analog Devices AD9364 |
| **Frequency Range** | 70 MHz - 6 GHz |
| **Channel Bandwidth** | 200 kHz - 56 MHz |
| **Sample Rate** | Up to 61.44 MSPS |
| **TX Channels** | 1 (single transmit) |
| **RX Channels** | 1 (single receive) |
| **TX Power** | -89.75 to 0 dBm (programmable) |
| **RX Noise Figure** | < 3 dB |
| **ADC/DAC Resolution** | 12-bit |
| **FPGA** | Xilinx Zynq-7020 (XC7Z020) |
| **RAM** | 512 MB DDR3 |
| **Flash** | 256 MB QSPI Flash |
| **Connectivity** | Gigabit Ethernet, USB 2.0 OTG |
| **GPS** | MAX-M8Q GNSS module |
| **Power Input** | 12V DC, 2A (24W max) |

---

## Physical Components

### Board Layout

```
   ┌─────────────────────────────────────────────────────────┐
   │                    ANTSDR E316 Board                     │
   │                                                           │
   │  ┌────┐     ┌──────┐              ┌────┐    ┌────┐     │
   │  │USB │     │ LAN  │              │GPS │    │PWR │     │
   │  │    │     │      │              │ANT │    │LED │     │
   │  └────┘     └──────┘              └────┘    └────┘     │
   │                                                           │
   │  ┌──────────┐                    ┌─────────┐            │
   │  │  RX SMA  │                    │  TX SMA │            │
   │  └──────────┘                    └─────────┘            │
   │                                                           │
   │           ┌────────────────┐                             │
   │           │   AD9364 RF    │      [BTN1] [BTN2]         │
   │           │   Transceiver  │                             │
   │           └────────────────┘      ┌──────────┐          │
   │                                   │ JP1 JP2  │          │
   │  ┌───────────────────┐            │ Jumpers  │          │
   │  │  Zynq-7020 FPGA   │            └──────────┘          │
   │  │  + ARM Cortex-A9  │                                   │
   │  └───────────────────┘            ┌──────────┐          │
   │                                   │   12V    │          │
   │                                   │   DC IN  │          │
   │                                   └──────────┘          │
   └─────────────────────────────────────────────────────────┘
```

### Component Locations

1. **Top Side (Component Side)**:
   - RF Transceiver (AD9364) - Center of board
   - FPGA (Zynq-7020) - Below RF transceiver
   - SMA Connectors (TX/RX) - Left and right sides
   - GPS Antenna Connector - Top right corner
   - Status LEDs - Top right corner
   - Configuration Buttons - Right side
   - Jumpers - Right side, near buttons

2. **Back Side**:
   - Ethernet (RJ45) connector - Left edge
   - USB OTG connector - Left edge
   - Power input (barrel jack) - Bottom right
   - MicroSD card slot (optional)

---

## Button and Jumper Configuration

### ⚙️ Button Configuration

The ANTSDR E316 has **2 configuration buttons** located on the right side of the board:

#### **BTN1 (Reset Button)** 🔴
- **Location**: Upper button on right edge
- **Function**: System reset
- **Usage**:
  - **Short press (< 1 second)**: Soft reset (restart Linux system)
  - **Long press (> 5 seconds)**: Hard reset (reload FPGA bitstream)
  
**When to use**:
- System becomes unresponsive
- Network configuration changes
- After firmware update
- Boot mode changes

#### **BTN2 (Boot Mode Button)** 🔵
- **Location**: Lower button on right edge
- **Function**: Boot mode selection
- **Usage**:
  - **Pressed during power-on**: Boot from SD card (if present)
  - **Not pressed**: Boot from QSPI flash (normal operation)

**Boot Mode Selection**:
```
Power OFF → Hold BTN2 → Apply Power → Wait 3 seconds → Release BTN2
                ↓
         Boot from SD Card
         
Power OFF → Apply Power (BTN2 not pressed)
                ↓
         Boot from QSPI Flash (Default)
```

### 🔌 Jumper Configuration

The ANTSDR E316 has **2 jumper blocks** for hardware configuration:

#### **JP1 (Power Source Selection)**
- **Location**: Right side, above power input
- **Options**:
  ```
  Position 1-2: USB Power (5V from USB)
  Position 2-3: External Power (12V DC input) ← DEFAULT
  ```

**⚠️ IMPORTANT**:
- For **LAN connection**: Set JP1 to position 2-3 (12V DC)
- For **USB-only operation**: Can use position 1-2 (USB power)
- **Never connect both 12V and USB power simultaneously**

**Configuration Table**:
| Connection Type | JP1 Setting | Power Source |
|----------------|-------------|--------------|
| **Ethernet + USB** | 2-3 | 12V DC Required |
| **Ethernet Only** | 2-3 | 12V DC Required |
| **USB Only** | 1-2 or 2-3 | USB or 12V DC |

#### **JP2 (Ethernet/USB Mode Selection)**
- **Location**: Right side, below JP1
- **Options**:
  ```
  Position 1-2: Ethernet Mode ← DEFAULT for our application
  Position 2-3: USB Gadget Mode
  ```

**Mode Descriptions**:

**Ethernet Mode (1-2)** - **USE THIS FOR GPR**:
- Device acts as Ethernet peripheral
- IP address: 192.168.1.10 (default)
- Access via: `iio_info -u ip:192.168.1.10`
- Requires: Gigabit Ethernet connection + 12V power
- **✅ Recommended for GPR system**

**USB Gadget Mode (2-3)**:
- Device acts as USB peripheral
- Shows as USB network device on host
- IP address: 192.168.2.1 (default)
- Access via: `iio_info -u usb:`
- Can be powered by USB (with JP1 in 1-2)

### 📸 Jumper Visual Guide

```
┌─────────────────┐
│   JP1 (Power)   │
│                 │
│  [1] o-o [2]    │  ← Position 2-3 for 12V DC
│      o   [3]    │     (Default for Ethernet)
│                 │
└─────────────────┘

┌─────────────────┐
│ JP2 (Interface) │
│                 │
│  [1] o-o [2]    │  ← Position 1-2 for Ethernet
│      o   [3]    │     (Recommended)
│                 │
└─────────────────┘
```

---

## LED Indicators

The ANTSDR E316 has **4 status LEDs** located on the top right corner:

### LED Functions

| LED | Color | Name | Indicates |
|-----|-------|------|-----------|
| **LED1** | 🟢 Green | Power | Power supply OK |
| **LED2** | 🟡 Yellow | FPGA Done | FPGA configuration complete |
| **LED3** | 🔵 Blue | Ethernet Link | Network connection active |
| **LED4** | 🔴 Red | Activity | Data transmission/reception |

### LED Status Interpretation

#### Normal Operation (Ethernet Mode):
```
LED1: 🟢 Solid ON       - Power good
LED2: 🟡 Solid ON       - FPGA configured
LED3: 🔵 Solid ON       - Ethernet connected
LED4: 🔴 Blinking       - Data transfer active
```

#### Boot Sequence:
```
1. Power on:
   LED1: 🟢 ON
   
2. FPGA loading (2-5 seconds):
   LED2: 🟡 OFF → Blinking → ON
   
3. Linux booting (10-20 seconds):
   LED4: 🔴 Rapid blinking
   
4. Network ready:
   LED3: 🔵 ON (if Ethernet cable connected)
   
5. System ready:
   All LEDs stable, LED4 blinks on activity
```

#### Troubleshooting with LEDs:

| LED Pattern | Problem | Solution |
|-------------|---------|----------|
| LED1 OFF | No power | Check 12V supply, JP1 position |
| LED2 OFF | FPGA not configured | Press BTN1, check firmware |
| LED2 Blinking | FPGA configuration error | Reload firmware, check SD card |
| LED3 OFF | No Ethernet link | Check cable, switch, link speed |
| LED4 Not blinking | No activity | Check IIO connection, drivers |

---

## Connection Interfaces

### 🌐 Ethernet Interface (Primary for GPR)

**Connector**: RJ45 Gigabit Ethernet (left side of board)

**Default Network Configuration**:
```
IP Address:    192.168.1.10
Subnet Mask:   255.255.255.0
Gateway:       192.168.1.1 (not used)
MAC Address:   Unique per device
```

**Cable Requirements**:
- CAT5e or CAT6 Ethernet cable
- Straight-through (not crossover)
- Maximum length: 100m
- Gigabit capable switch/port recommended

**Host Computer Configuration**:
```
IP Address:    192.168.1.100 (or any .1 to .254 except .10)
Subnet Mask:   255.255.255.0
Gateway:       Leave blank (direct connection)
```

### 🔌 USB Interface (Alternative)

**Connector**: Micro-USB OTG (left side of board)

**USB Modes**:
1. **USB Host Mode** (default): Device can control USB peripherals
2. **USB Gadget Mode** (with JP2=2-3): Appears as USB network device

**USB Gadget Network Configuration**:
```
Device IP:     192.168.2.1
Host IP:       192.168.2.2 (auto-assigned)
Interface:     usb0 or similar
```

### 📡 RF Connectors

**TX Output** (Right SMA):
- Frequency: 70 MHz - 6 GHz
- Power: -89.75 to 0 dBm
- Impedance: 50Ω
- Connector: SMA female

**RX Input** (Left SMA):
- Frequency: 70 MHz - 6 GHz
- Gain: 0-76 dB (programmable)
- Impedance: 50Ω
- Connector: SMA female
- Max input: -10 dBm (without damage)

**⚠️ RF Safety**:
- Always use 50Ω termination or antenna
- Never leave RF ports open during transmission
- Use attenuators for loopback testing

### 🛰️ GPS Connector

**Connector**: U.FL (top right corner)

**GPS Module**: MAX-M8Q
- Frequency: 1575.42 MHz (L1 band)
- Sensitivity: -160 dBm
- Time to first fix: ~29 seconds (cold start)
- Accuracy: 2.5m CEP

**GPS Antenna Requirements**:
- Active GPS antenna (3.3V powered)
- U.FL connector
- Gain: 15-30 dB
- Cable length: < 5m recommended

---

## Power Requirements

### 🔋 Power Specifications

**Input Voltage**: 12V DC ±10% (10.8V - 13.2V)
**Input Current**: 
- Idle: ~500 mA (6W)
- Normal operation: ~1 A (12W)
- Maximum: ~2 A (24W) with GPS and full TX power

**Power Consumption by Mode**:
```
Idle (no RF):           6W
RX only:                8W
TX + RX (low power):    12W
TX + RX (full power):   18W
With GPS:               +2W
```

### 🔌 Power Supply Requirements

**Recommended Power Supply**:
- Voltage: 12V DC regulated
- Current: ≥ 2A (2.5A recommended for margin)
- Connector: 5.5mm × 2.1mm barrel jack (center positive)
- Regulation: ± 5% or better
- Ripple: < 100mV pk-pk

**⚠️ Power Supply Warnings**:
- ❌ Do NOT use unregulated/poorly filtered supplies
- ❌ Do NOT use supplies < 1.5A rating
- ❌ Do NOT exceed 13.2V input
- ✅ Use quality switching or linear regulated supply
- ✅ Keep supply physically close to device (< 1m)

### Power Connector Pinout

```
  Barrel Jack (5.5mm × 2.1mm)
  
   ┌─────┐
   │  +  │  ← Center pin: +12V
   └──┬──┘
      │
   ───┴───  ← Outer sleeve: GND
```

---

## Pre-Connection Checklist

Before connecting ANTSDR E316 to Xubuntu:

### Hardware Checklist
- [ ] **JP1** set to position 2-3 (12V external power)
- [ ] **JP2** set to position 1-2 (Ethernet mode)
- [ ] 12V/2A power supply connected (not powered yet)
- [ ] Ethernet cable connected to board
- [ ] Ethernet cable connected to computer or switch
- [ ] RF antennas or terminators on TX/RX ports
- [ ] GPS antenna connected (optional but recommended)

### Initial Power-On Test
1. Apply 12V power
2. Check LED sequence:
   - LED1 (Green): Should turn ON immediately
   - LED2 (Yellow): Should blink then turn solid ON (2-5 sec)
   - LED3 (Blue): Should turn ON if Ethernet connected (15-30 sec)
   - LED4 (Red): Should blink occasionally
3. Wait 30 seconds for full boot
4. Verify all LEDs are in expected state

### Safety Checklist
- [ ] RF connectors have proper loads (antennas or terminators)
- [ ] Power supply is rated 12V, ≥2A
- [ ] No metal objects near RF circuits
- [ ] Adequate ventilation around device
- [ ] ESD precautions taken (wrist strap if available)

---

## Quick Reference Card

### Default Settings (Out of Box)
```
Mode:           Ethernet (JP2 = 1-2)
Power:          12V External (JP1 = 2-3)
IP Address:     192.168.1.10
Subnet:         255.255.255.0
Boot Source:    QSPI Flash
```

### Common Configurations

#### Configuration 1: Ethernet (GPR System) ✅
```
JP1:    2-3 (12V DC)
JP2:    1-2 (Ethernet)
Power:  12V/2A external supply
Cable:  Gigabit Ethernet
Host IP: 192.168.1.100
```

#### Configuration 2: USB Only
```
JP1:    1-2 (USB power)
JP2:    2-3 (USB Gadget)
Power:  USB cable (5V from host)
Cable:  Micro-USB
Host IP: 192.168.2.2 (auto)
```

---

## Additional Resources

- **ANTSDR Wiki**: https://wiki.antsdr.com/
- **AD9364 Datasheet**: https://www.analog.com/en/products/ad9364.html
- **Zynq-7020 Documentation**: https://www.xilinx.com/products/silicon-devices/soc/zynq-7000.html
- **IIO Documentation**: https://wiki.analog.com/software/linux/docs/iio/iio

---

**Next Steps**: Proceed to `02_XUBUNTU_NETWORK_SETUP.md` for host computer configuration.

**Document Version**: 1.0  
**Last Updated**: 2025-10-24  
**Tested With**: ANTSDR E316 Rev 1.0, Xubuntu 22.04 LTS

