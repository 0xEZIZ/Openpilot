# 🏴‍☠️ ADU OpenPilot | Advanced Car Hacking & CAN Protocol Toolkit

<div align="center">
  <img src="logo (2).jpg" alt="ADU OpenPilot Logo" width="200"/>
  
  **An aggressive, red-team-oriented toolkit for automotive penetration testing, CAN bus manipulation, and vehicle reverse engineering.**
</div>

## 📌 Overview
**ADU OpenPilot** is a specialized framework developed for **Automotive Red Teaming, Black-box Testing, and CAN Protocol Exploitation**. Designed to interface directly with modern vehicle networks, it allows security researchers to sniff, decode, manipulate, and forcefully inject control packets (Steering, Throttle, Braking) into the OBD-II port or internal vehicle CAN buses.

With built-in parser targets for major manufacturers—such as **Toyota, Honda, Hyundai, Subaru, and Nissan**—and an extensive collection of decoded `.dbc` files, this tool is intended to demonstrate vulnerabilities in vehicular networks and study proprietary automotive communication protocols.

---

## ⚡ Red Team Features (Attack Vectors)
- 💉 **Active Payload Injection:** Bypass standard vehicle control units to inject custom torque, steering angle, and acceleration demands directly into the driving systems.
- 📡 **CAN Traffic Sniffing & Parsing:** Decode live proprietary manufacturer packets on the fly using a robust internal `.dbc` decoding engine.
- 🔧 **Hardware Agnostic & Malicious Bridges:** 
  - Compatible with professional grade **IXXAT USB-to-CAN** adapters.
  - Supports clandestine, low-cost **ESP32 & MCP2515** CAN bridges (embedded `.ino` payloads included in the repo) for covert, remote deployment.
- 🛡️ **Safety Layer Analysis:** Built-in `safety_layer.py` module to study, emulate, and potentially identify bypasses for modern ADAS (Advanced Driver Assistance Systems) limiters.
- 🚦 **Real-time Vehicle Domination:** Fully interactive graphical C2 (Command & Control) dashboard to monitor 4-wheel telemetry and assert live physical constraints over the drivetrain.

---

## 📁 Toolkit Architecture
```text
ADU_OpenPilot/
 ├── main.py              ← Core execution engine / Splash Screen
 ├── gui.py               ← C2 Dashboard / Control Interface
 ├── can_interface.py     ← Hardware bridging (IXXAT / Serial CAN)
 ├── can_parser.py        ← Generic CAN sniffer & decoder
 ├── toyota_parser.py     ← Toyota-specific protocol dissection
 ├── toyota_commands.py   ← Exploitation payloads (Steering, Throttle)
 ├── safety_layer.py      ← Parameter boundary emulation / restrictions
 ├── esp32_can_bridge.ino ← Covert microcontroller exploit firmware
 └── dbc_files/           ← 30+ Decoded automotive databases (Crown Jewels)
```

---

## 🛠️ Weaponization & Setup

### Prerequisites
Deploy the required dependencies on your penetration testing machine (Python 3.10+ recommended):
```bash
pip install -r requirements.txt
# Core necessities: python-can, cantools, pillow
```

### Execution
1. Connect your CAN interface (IXXAT or custom ESP32 implant) to the target vehicle's CAN-H and CAN-L lines.
2. Launch the C2 Dashboard:
```bash
# Initialize active connection with hardware
python main.py

# Offline analysis and UI practice (Simulation Mode)
python main.py --demo
```

### Emulated Controls (Live Engagement)
When actively bridged to a vulnerable CAN bus and target systems are primed:
- **Steering Takeover:** `◀◀` and `▶▶` arrows or arbitrary slider values (`-1500` to `+1500` torque/angle).
- **Throttle / Override:** `▲` and `▼` for direct acceleration parameter manipulation (`-3.5` to `+2.0` accel mapping).

---

## ⚠️ Legal Disclaimer (Must Read)
> **FOR EDUCATIONAL AND AUTHORIZED PENTESTING ONLY.**
> This software is strictly provided for security researchers, red teams, and automotive cybersecurity professionals working on **authorized targets**.
> 
> **WARNING:** Injecting packets into a moving vehicle's CAN bus is **extremely dangerous** and can lead to loss of life or catastrophic hardware failure. **DO NOT** use this software on public roads or vehicles you do not explicitly own or have written, legally binding permission to test. 
> 
> The creator, contributors, and repository owners assume **zero liability** for any damage, injury, legal repercussions, or property loss resulting from the use or misuse of this code. Use responsibly in closed, controlled environments.

---

**© 2026 ADU OpenPilot Development. All Rights Reserved.**
