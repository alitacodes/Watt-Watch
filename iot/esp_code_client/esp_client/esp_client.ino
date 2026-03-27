#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// --- FIX: DECLARE THESE AT THE TOP ---
const char* ssid = "HP14fs";
const char* password = "12345678";
const char* server_host = "10.141.144.63"; 
const uint16_t server_port = 8765;
//

WebSocketsClient webSocket;

struct Device { const char* id; int pin; };
Device list[] = { {"e0", 19}, {"e1", 18}, {"e2", 17}, {"e3", 16} };

void sendReport(const char* id, int pin) {
  StaticJsonDocument<128> doc;
  doc["room"] = 0;
  doc["appliance"] = id;
  doc["state"] = (digitalRead(pin) == HIGH) ? 1 : 0; // Using integers
  String out;
  serializeJson(doc, out);
  webSocket.sendTXT(out);
}

void onMessage(String payload) {
  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload);
  if (doc.containsKey("state")) {
    const char* target = doc["appliance"];
    int newState = doc["state"]; // Receive integer 1 or 0
    for (int i = 0; i < 4; i++) {
      if (strcmp(target, list[i].id) == 0) {
        digitalWrite(list[i].pin, (newState == 1) ? HIGH : LOW);
        sendReport(list[i].id, list[i].pin);
        break;
      }
    }
  }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) onMessage((char*)payload);
  else if (type == WStype_CONNECTED) {
    for(int i=0; i<4; i++) sendReport(list[i].id, list[i].pin);
  }
}

void setup() {
  Serial.begin(115200);
  for(int i=0; i<4; i++) pinMode(list[i].pin, OUTPUT);
  
  WiFi.begin(ssid, password); //
  while (WiFi.status() != WL_CONNECTED) delay(500);

  webSocket.onEvent(webSocketEvent);
  webSocket.begin(server_host, server_port, "/"); //
}

void loop() { webSocket.loop(); }