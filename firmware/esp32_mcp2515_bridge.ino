/*
 * ESP32 + MCP2515 Wireless CAN Bridge (UDP)
 * Toyota Corolla 2017 - DSU Intercept
 * 
 * Kitaphana: "mcp_can" (Cory J. Fowler)
 */

#include <WiFi.h>
#include <WiFiUDP.h>
#include <SPI.h>
#include <mcp_can.h>

// --- Config ---
const char* ssid     = "ADU_OpenPilot_Testing";
const char* password = "toyota_control";
const int   port     = 12345;

// MCP2515 Pins (SPI)
const int SPI_CS_PIN = 5;
const int CAN_INT_PIN = 21;
MCP_CAN CAN(SPI_CS_PIN);

WiFiUDP udp;
IPAddress remoteIP;
bool remoteConnected = false;

void setup() {
  Serial.begin(115200);
  
  // 1. WiFi
  WiFi.softAP(ssid, password);
  Serial.println("Wi-Fi AP Started");

  // 2. Initialize MCP2515 - 500kbps / 8MHz (ýa-da 16MHz modula görä)
  if (CAN.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("MCP2515 Initialized Successfully!");
  } else {
    Serial.println("Error Initializing MCP2515...");
  }
  CAN.setMode(MCP_NORMAL);

  udp.begin(port);
}

void loop() {
  // --- Receive from CAN ---
  long unsigned int rxId;
  unsigned char len = 0;
  unsigned char rxBuf[8];

  if (CAN.checkReceive() == CAN_MSGAVAIL) {
    CAN.readMsgBuf(&rxId, &len, rxBuf);
    if (remoteConnected) {
      uint8_t packet[13];
      packet[0] = rxId & 0xFF;
      packet[1] = (rxId >> 8) & 0xFF;
      packet[2] = (rxId >> 16) & 0xFF;
      packet[3] = (rxId >> 24) & 0xFF;
      packet[4] = len;
      memcpy(&packet[5], rxBuf, len);

      udp.beginPacket(remoteIP, port);
      udp.write(packet, 5 + len);
      udp.endPacket();
    }
  }

  // --- Receive from UDP ---
  int packetSize = udp.parsePacket();
  if (packetSize >= 5) {
    uint8_t packet[13];
    udp.read(packet, packetSize);
    
    if (!remoteConnected) {
      remoteIP = udp.remoteIP();
      remoteConnected = true;
      Serial.print("Connected to: "); Serial.println(remoteIP);
    }

    long unsigned int txId = packet[0] | (packet[1] << 8) | (packet[2] << 16) | (packet[3] << 24);
    uint8_t dlc = packet[4];
    CAN.sendMsgBuf(txId, 0, dlc, &packet[5]);
  }
}
