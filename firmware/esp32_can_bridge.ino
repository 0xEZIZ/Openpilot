/*
 * ESP32 Wireless CAN Bridge (UDP)
 * Toyota Corolla 2017 - DSU Intercept
 * 
 * Hardware:
 * - ESP32 (e.g. NodeMCU)
 * - MCP2551 / SN65HVD230 CAN Transceiver
 * 
 * Connections:
 * - ESP32 GPIO 16 -> Transceiver TXD
 * - ESP32 GPIO 17 -> Transceiver RXD
 * - Transceiver CAN_H/L -> Car DSU CAN Bus
 *
 * Note: GPIO 5 is reserved for MCP2515 CS (SPI)
 */

#include <WiFi.h>
#include <WiFiUDP.h>
#include "driver/twai.h"

// --- Configuration ---
const char* ssid     = "ADU_OpenPilot_Testing"; // ESP32 creates this AP
const char* password = "toyota_control";
const int   port     = 12345;

// TWAI (CAN) Pins
#define CAN_TX_PIN GPIO_NUM_16
#define CAN_RX_PIN GPIO_NUM_17

WiFiUDP udp;
IPAddress remoteIP;
bool remoteConnected = false;

void setup() {
  Serial.begin(115200);
  
  // 1. Start Wi-Fi AP
  WiFi.softAP(ssid, password);
  Serial.println("Wi-Fi AP Started");
  Serial.print("IP: "); Serial.println(WiFi.softAPIP());

  // 2. Initialize TWAI (CAN) - 500kbps for Toyota
  twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
  twai_timing_config_t  t_config = TWAI_TIMING_CONFIG_500KBITS();
  twai_filter_config_t  f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

  if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
    Serial.println("CAN Driver Installed");
  }
  if (twai_start() == ESP_OK) {
    Serial.println("CAN Started");
  }

  udp.begin(port);
}

void loop() {
  // --- Receive from CAN and Forward to UDP ---
  twai_message_t rx_msg;
  if (twai_receive(&rx_msg, 0) == ESP_OK) {
    if (remoteConnected) {
      // Packet format: [ID_low, ID_mid, ID_high, ID_ext, Len, Data...]
      uint8_t packet[13];
      packet[0] = rx_msg.identifier & 0xFF;
      packet[1] = (rx_msg.identifier >> 8) & 0xFF;
      packet[2] = (rx_msg.identifier >> 16) & 0xFF;
      packet[3] = (rx_msg.identifier >> 24) & 0xFF;
      packet[4] = rx_msg.data_length_code;
      for (int i=0; i<rx_msg.data_length_code; i++) {
        packet[5+i] = rx_msg.data[i];
      }
      udp.beginPacket(remoteIP, port);
      udp.write(packet, 5 + rx_msg.data_length_code);
      udp.endPacket();
    }
  }

  // --- Receive from UDP and Forward to CAN ---
  int packetSize = udp.parsePacket();
  if (packetSize >= 5) {
    uint8_t packet[13];
    udp.read(packet, packetSize);
    
    // Store remote IP from first incoming packet
    if (!remoteConnected) {
      remoteIP = udp.remoteIP();
      remoteConnected = true;
      Serial.print("Python Controller Connected: ");
      Serial.println(remoteIP);
    }

    twai_message_t tx_msg;
    tx_msg.identifier = packet[0] | (packet[1] << 8) | (packet[2] << 16) | (packet[3] << 24);
    tx_msg.data_length_code = packet[4];
    tx_msg.extd = 0;
    for (int i=0; i<tx_msg.data_length_code; i++) {
      tx_msg.data[i] = packet[5+i];
    }
    
    twai_transmit(&tx_msg, pdMS_TO_TICKS(10));
  }
}
