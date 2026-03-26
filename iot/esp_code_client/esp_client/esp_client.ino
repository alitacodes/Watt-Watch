#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "FrostHack AP_L4";
const char* password = "AotL4@169#2026";

// Replace with the IP address of the computer running your Python script
const char* server_host = "192.168.0.144"; 
const uint16_t server_port = 8765;

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WSc] Disconnected!");
      break;
    case WStype_CONNECTED:
      Serial.printf("[WSc] Connected to url: %s\n", payload);
      // Send a greeting to the Python server
      webSocket.sendTXT("Hello from ESP32!");
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] Message from Server: %s\n", payload);
      break;
    case WStype_BIN:
      Serial.printf("[WSc] Received binary length: %u\n", length);
      break;
    case WStype_ERROR:      
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
      break;
  }
}

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[WiFi] Connected!");
  Serial.print("[IP] ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Server address, port, and URL path
  webSocket.begin(server_host, server_port, "/");

  // Event handler for messages/connection status
  webSocket.onEvent(webSocketEvent);

  // Reconnect if connection fails
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();
}