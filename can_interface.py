"""
IXXAT USB-to-CAN - Windows baglanysy
Thread-safe CAN okamak we ibermek

Demo mode: Realistic car physics simulation
- Acceleration/braking from user commands → speed change
- Natural deceleration (engine braking + friction)
- RPM linked to speed via gear ratios
- Steering angle follows torque commands
"""
import can
import threading
import time
import math
import random
import socket
import struct
import config


# ======================================================================
#  NETWORK CAN (UDP) - Wireless ESP32 Bridge
# ======================================================================
class UDPBus:
    """
    Custom CAN bus class that communicates with an ESP32 bridge via UDP.
    Protocol: [ID(4), Len(1), Data(8)]
    """
    def __init__(self, ip, port, on_message):
        self.ip   = ip
        self.port = port
        self.on_message = on_message
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        self._stop = False
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def _recv_loop(self):
        while not self._stop:
            try:
                data, addr = self.sock.recvfrom(64)
                if len(data) >= 5:
                    # Parse mini-packet: [ID_low, ID_mid, ID_high, ID_ext, Len, Data...]
                    msg_id = struct.unpack("<I", data[0:4])[0]
                    dlc    = data[4]
                    payload = data[5:5+dlc]
                    
                    msg = can.Message(
                        arbitration_id=msg_id,
                        data=payload,
                        is_extended_id=False,
                        timestamp=time.time()
                    )
                    if self.on_message:
                        self.on_message(msg)
            except socket.timeout:
                continue
            except Exception as e:
                if not self._stop:
                    print(f"UDP Recv Error: {e}")
                break

    def send(self, msg):
        """Send CAN message to ESP32 via UDP"""
        # Packet: [ID(4), Len(1), Data(8)]
        packet = struct.pack("<IB", msg.arbitration_id, len(msg.data)) + msg.data
        try:
            self.sock.sendto(packet, (self.ip, self.port))
        except Exception as e:
            print(f"UDP Send Error: {e}")

    def shutdown(self):
        self._stop = True
        self.sock.close()


class CANInterface:
    def __init__(self, on_message=None):
        """
        on_message: callback(msg) - her CAN habary gelanda çagyrylýar
        """
        self.bus         = None
        self.on_message  = on_message
        self.connected   = False
        self._rx_thread  = None
        self._demo_thread = None
        self._stop_event = threading.Event()

        # Demo mode: user command state (updated via send() interception)
        self._demo_lock       = threading.Lock()
        self._demo_accel_cmd  = 0.0    # m/s² from ACC_CONTROL
        self._demo_steer_cmd  = 0      # torque Nm from STEERING_LKA
        self._demo_accel_active = False
        self._demo_steer_active = False

    # ------------------------------------------------------------------
    def connect(self):
        """IXXAT ýa-da Network (ESP32) adapterine birikdir"""
        if config.DEMO_MODE:
            self._start_demo()
            return True

        self.connected = False
        iface = config.CAN_INTERFACE.lower()

        try:
            if iface == 'network' or iface == 'udp':
                # Wireless ESP32 Bridge
                self.bus = UDPBus(
                    ip=config.ESP32_IP,
                    port=config.ESP32_PORT,
                    on_message=self.on_message
                )
                self.connected = True
            else:
                # Standard python-can (ixxat, vector, etc.)
                self.bus = can.Bus(
                    interface=config.CAN_INTERFACE,
                    channel=config.CAN_CHANNEL,
                    bitrate=config.CAN_BITRATE
                )
                self.connected = True
                self._stop_event.clear()
                self._rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
                self._rx_thread.start()
            
            return True
        except Exception as e:
            raise ConnectionError(f"CAN connection failed ({iface}): {e}")

    # ------------------------------------------------------------------
    def disconnect(self):
        """Baglanysy kes"""
        self._stop_event.set()
        self.connected = False
        if self._rx_thread and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=1.0)
        self._rx_thread = None
        if self._demo_thread and self._demo_thread.is_alive():
            self._demo_thread.join(timeout=1.0)
        self._demo_thread = None
        if self.bus:
            try:
                self.bus.shutdown()
            except Exception:
                pass
            self.bus = None

        # Reset demo state
        with self._demo_lock:
            self._demo_accel_cmd = 0.0
            self._demo_steer_cmd = 0
            self._demo_accel_active = False
            self._demo_steer_active = False

    # ------------------------------------------------------------------
    def send(self, can_id, data: bytes):
        """CAN habary iber"""
        if config.DEMO_MODE:
            # Demo: intercept ACC_CONTROL and STEERING_LKA commands
            self._demo_intercept(can_id, data)
            return True
        if not self.connected or not self.bus:
            return False
        try:
            msg = can.Message(
                arbitration_id=can_id,
                data=data,
                is_extended_id=False
            )
            self.bus.send(msg)
            return True
        except Exception as e:
            print(f"CAN send error: {e}")
            return False

    # ------------------------------------------------------------------
    def _demo_intercept(self, can_id, data):
        """
        Demo mode: GUI-den iberilen buýruklary tut we simulýasiýa state-e ýaz.
        ACC_CONTROL (0x343) → accel_cmd (m/s²)
        STEERING_LKA (0x2E4) → steer_cmd (torque Nm)
        """
        with self._demo_lock:
            # ACC_CONTROL (0x343): ACCEL_CMD at bytes 0-1, signed, factor=0.001
            if can_id == config.ID_ACC_CONTROL and len(data) >= 8:
                accel_raw = (data[0] << 8) | data[1]
                if accel_raw > 32767:
                    accel_raw -= 65536
                self._demo_accel_cmd = accel_raw * 0.001  # m/s²
                # CANCEL_REQ at byte3 bit0: if cancel → no accel
                cancel = bool(data[3] & 0x01)
                permit = bool(data[3] & 0x40)
                self._demo_accel_active = permit and not cancel

            # STEERING_LKA (0x2E4): STEER_TORQUE_CMD at bytes 1-2, signed
            elif can_id == config.ID_STEERING_LKA and len(data) >= 5:
                torque_raw = (data[1] << 8) | data[2]
                if torque_raw > 32767:
                    torque_raw -= 65536
                self._demo_steer_cmd = torque_raw
                steer_request = bool(data[0] & 0x01)
                self._demo_steer_active = steer_request

    # ------------------------------------------------------------------
    def _receive_loop(self):
        """Arka planda CAN habarlaryny okamak"""
        while not self._stop_event.is_set():
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg and self.on_message:
                    self.on_message(msg)
            except can.CanError as e:
                print(f"CAN okamak yalnyslygy: {e}")
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"CAN receive yalnyslygy: {e}")
                break

    # ------------------------------------------------------------------
    # DEMO MODE — Realistic Car Physics Simulation
    # ------------------------------------------------------------------
    def _start_demo(self):
        """Ýasama CAN maglumatlary döret (synag üçin)"""
        self.connected   = True
        self._stop_event.clear()
        self._demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self._demo_thread.start()

    def _demo_loop(self):
        """
        Realistic Toyota Corolla 2017 demo simulation.

        Physics model:
        - User presses gas → positive acceleration → speed increases
        - User presses brake → negative acceleration → speed decreases
        - No input → natural deceleration (engine braking + rolling resistance)
        - Speed clamped [0, 200] km/h
        - RPM follows speed via simple gear model
        - Steering angle follows torque command with lag
        """
        # ---- state ----
        speed_mps  = 0.0    # m/s (internal simulation)
        steer_deg  = 0.0    # steering angle degrees
        gas_pct    = 0.0    # gas pedal % for display
        brake_val  = 0       # brake value for display

        dt = 0.02           # 50 Hz = 20ms step (more responsive)
        t  = 0.0

        # ---- physics constants ----
        ROLLING_RESISTANCE  = 0.25   # m/s² (engine braking + tire friction)
        AERO_COEFF          = 0.0008 # aero drag coefficient (speed² term)
        MAX_SPEED_MPS       = 200.0 / 3.6  # 200 km/h in m/s (~55.6 m/s)
        STEER_RESPONSE_RATE = 3.0    # degrees per second per Nm of torque (how fast wheel turns)
        MAX_STEER_DEG       = 540.0  # max steering angle degrees

        while not self._stop_event.is_set():
            t += dt

            # ---- read user commands (thread-safe) ----
            with self._demo_lock:
                accel_cmd    = self._demo_accel_cmd     # m/s²
                accel_active = self._demo_accel_active
                steer_cmd    = self._demo_steer_cmd     # Nm
                steer_active = self._demo_steer_active

            # ============================================
            # SPEED PHYSICS
            # ============================================
            if accel_active and accel_cmd > 0.01:
                # ---- GAS: User is accelerating ----
                # Convert accel command (m/s²) to actual acceleration
                # Toyota ACC_CONTROL range: -3.5 to +2.0 m/s²
                # Gas pedal percentage for display
                gas_pct = min(100.0, (accel_cmd / 2.0) * 100.0)
                brake_val = 0

                # Apply acceleration with slight diminishing at high speeds
                speed_factor = max(0.1, 1.0 - (speed_mps / MAX_SPEED_MPS) ** 2)
                effective_accel = accel_cmd * speed_factor

                # Subtract rolling resistance (always opposing motion)
                if speed_mps > 0.1:
                    drag = ROLLING_RESISTANCE + AERO_COEFF * speed_mps * speed_mps
                    effective_accel -= drag
                    # But if gas is strong enough, net is still positive
                    if effective_accel < 0 and accel_cmd > 0.3:
                        effective_accel = accel_cmd * 0.3  # at least some accel

                speed_mps += effective_accel * dt

            elif accel_active and accel_cmd < -0.01:
                # ---- BRAKE: User is braking ----
                gas_pct = 0.0
                brake_val = min(255, int(abs(accel_cmd) / 3.5 * 255))

                # Braking deceleration
                decel = abs(accel_cmd)
                speed_mps -= decel * dt

            else:
                # ---- NO INPUT: Natural deceleration ----
                gas_pct = max(0, gas_pct - 2.0)  # slowly release gas display
                brake_val = 0

                if speed_mps > 0.05:
                    # Engine braking + rolling resistance + aero
                    natural_decel = ROLLING_RESISTANCE + AERO_COEFF * speed_mps * speed_mps
                    speed_mps -= natural_decel * dt
                else:
                    speed_mps = 0.0

            # Clamp speed
            speed_mps = max(0.0, min(MAX_SPEED_MPS, speed_mps))

            # Convert to km/h for CAN messages
            speed_kmh = speed_mps * 3.6

            # ============================================
            # STEERING PHYSICS
            # ============================================
            if steer_active and abs(steer_cmd) > 10:
                # Torque → angular velocity → angle
                # More torque = faster turn
                target_rate = (steer_cmd / 1500.0) * 180.0  # deg/s at max torque
                steer_deg += target_rate * dt
            else:
                # Return to center gradually (self-centering)
                if abs(steer_deg) > 0.5:
                    center_rate = 60.0  # deg/s return speed
                    if steer_deg > 0:
                        steer_deg -= min(center_rate * dt, steer_deg)
                    else:
                        steer_deg += min(center_rate * dt, abs(steer_deg))
                else:
                    steer_deg = 0.0

            steer_deg = max(-MAX_STEER_DEG, min(MAX_STEER_DEG, steer_deg))

            # ============================================
            # RPM MODEL (simple gear simulation)
            # ============================================
            if speed_kmh < 0.5:
                rpm = 800.0  # idle
            else:
                # Simple automatic transmission model
                # Gear ratios approximate: lower gears = higher RPM per speed
                if speed_kmh < 20:
                    rpm = 800 + speed_kmh * 120        # 1st gear
                elif speed_kmh < 40:
                    rpm = 1200 + (speed_kmh - 20) * 80  # 2nd gear
                elif speed_kmh < 70:
                    rpm = 1200 + (speed_kmh - 40) * 55  # 3rd gear
                elif speed_kmh < 110:
                    rpm = 1200 + (speed_kmh - 70) * 42  # 4th gear
                else:
                    rpm = 1500 + (speed_kmh - 110) * 35  # 5th/6th gear

                # Gas pedal adds RPM (revving)
                if gas_pct > 5:
                    rpm += gas_pct * 8

            rpm = min(7000, max(800, rpm))

            # ============================================
            # GENERATE CAN MESSAGES
            # ============================================

            # -- SPEED (0xB4) --
            spd_raw = int(speed_kmh / 0.01)
            d = bytearray(8)
            d[5] = (spd_raw >> 8) & 0xFF
            d[6] = spd_raw & 0xFF
            self._fake_msg(0xB4, d)

            # -- STEER_ANGLE (0x25) --
            steer_for_can = steer_deg * 1.5  # Scale for display
            st_raw = int(steer_for_can / 1.5)
            if st_raw < 0:
                st_raw = st_raw & 0xFFF
            d2 = bytearray(8)
            d2[0] = (st_raw >> 8) & 0x0F
            d2[1] = st_raw & 0xFF
            self._fake_msg(0x25, d2)

            # -- GAS_PEDAL (0x2C1 = 705) --
            d3 = bytearray(8)
            d3[6] = int(gas_pct / 0.5) & 0xFF
            self._fake_msg(0x2C1, d3)

            # -- GAS_PEDAL_HYBRID (0x245 = 581) --
            d3h = bytearray(8)
            d3h[2] = min(255, int(gas_pct * 0.01 / 0.005)) & 0xFF
            self._fake_msg(0x245, d3h)

            # -- BRAKE (0xA6) --
            d4 = bytearray(8)
            d4[0] = brake_val & 0xFF
            self._fake_msg(0xA6, d4)

            # -- WHEEL_SPEEDS (0xAA) --
            # Wheel speeds = vehicle speed + small variation
            for wheel_idx in range(4):
                ws_spd = speed_kmh + random.uniform(-0.3, 0.3)
                ws_raw = int((ws_spd + 67.67) / 0.01)
                d5 = bytearray(8)
                for i in range(4):
                    ws_spd_i = speed_kmh + random.uniform(-0.2, 0.2)
                    ws_raw_i = int((ws_spd_i + 67.67) / 0.01)
                    d5[i*2]   = (ws_raw_i >> 8) & 0xFF
                    d5[i*2+1] = ws_raw_i & 0xFF
                self._fake_msg(0xAA, d5)
                break  # only send once

            # -- ENGINE_RPM (0x1C4 = 452) --
            rpm_raw = int(rpm / 0.78125)
            d6 = bytearray(8)
            d6[0] = (rpm_raw >> 8) & 0xFF
            d6[1] = rpm_raw & 0xFF
            d6[3] = 0x08  # ENGINE_RUNNING=1
            self._fake_msg(0x1C4, d6)

            # -- PCM_CRUISE (0x1D2 = 466) --
            d7 = bytearray(8)
            cruise_active = 1 if speed_kmh > 40 else 0
            d7[0] = cruise_active << 5
            cruise_state = 8 if cruise_active else 0
            d7[6] = (cruise_state & 0x0F) << 4
            self._fake_msg(0x1D2, d7)

            # -- KINEMATICS (0x24 = 36) --
            yaw = steer_deg * 0.3 * (speed_kmh / 60.0)  # yaw depends on speed+steer
            yaw_raw = max(0, min(1023, int((yaw + 125) / 0.244)))
            # Actual longitudinal accel
            if accel_active:
                ax = accel_cmd
            elif speed_mps > 0.1:
                ax = -(ROLLING_RESISTANCE + AERO_COEFF * speed_mps * speed_mps)
            else:
                ax = 0.0
            ax_raw = max(0, min(1023, int((ax + 18.375) / 0.03589)))
            d8 = bytearray(8)
            d8[0] = (yaw_raw >> 8) & 0x03
            d8[1] = yaw_raw & 0xFF
            d8[2] = (ax_raw >> 8) & 0x03
            d8[3] = ax_raw & 0xFF
            self._fake_msg(0x24, d8)

            # -- STEER_TORQUE_SENSOR (0x260 = 608) --
            driver_torq = int(steer_deg * 0.08)  # small driver torque from angle
            dt_bytes = driver_torq & 0xFFFF
            d9 = bytearray(8)
            d9[0] = 1 if abs(driver_torq) > 100 else 0
            d9[1] = (dt_bytes >> 8) & 0xFF
            d9[2] = dt_bytes & 0xFF
            self._fake_msg(0x260, d9)

            # -- EPS_STATUS (0x262 = 610) --
            d10 = bytearray(5)
            lka_st = 5 if steer_active else 1  # active when steering, standby otherwise
            d10[0] = 3 & 0x0F
            d10[3] = (lka_st << 1) & 0xFE
            self._fake_msg(0x262, d10)

            time.sleep(dt)

    def _fake_msg(self, can_id, data):
        """Ýasama habar döret we callback çagyr"""
        if self.on_message:
            msg = can.Message(
                arbitration_id=can_id,
                data=bytes(data),
                is_extended_id=False,
                timestamp=time.time()
            )
            self.on_message(msg)
