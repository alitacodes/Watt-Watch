#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "FrostHack AP_L4";
const char* password = "AotL4@169#2026";
const char* serverUrl = "http://192.168.0.144:5000/sync";

struct PinMap { String key; int pin; };
// Your NEW Mapping
PinMap myPins[] = {
  {"1e0", 16}, {"1e1", 17}, {"1e6", 18},
  {"2e2", 21}, {"2e4", 22}, {"2e5", 23}
};
const int totalPins = 6;

void setup() {
  Serial.begin(115200);
  for(int i=0; i < totalPins; i++) {
    pinMode(myPins[i].pin, OUTPUT);
    digitalWrite(myPins[i].pin, LOW); // Start all OFF
  }

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi Connected - yex Mapping Active");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST("{}"); 

    if (httpResponseCode == 200) {
      String response = http.getString();
      StaticJsonDocument<512> doc;
      deserializeJson(doc, response);

      for (int i = 0; i < totalPins; i++) {
        if (doc.containsKey(myPins[i].key)) {
          int targetState = doc[myPins[i].key];
          // Use a flag check to only toggle if needed
          if (digitalRead(myPins[i].pin) != targetState) {
             digitalWrite(myPins[i].pin, (targetState == 1) ? HIGH : LOW);
             Serial.println("Updated " + myPins[i].key);
          }
        }
      }
    }
    http.end();
  }
  delay(1000); 
}