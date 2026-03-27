#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
//final code
const char* ssid = "HP14fs";
const char* password = "12345678";
const char* serverUrl = "http://10.141.144.63:5000/sync";

// Single unit mapping for both emulated rooms
struct PinMap { String key; int pin; };
PinMap myPins[] = {
  {"0e0", 21}, {"0e1", 22}, {"0e2", 23}, // Emulated Room 0
  {"1e0", 16}, {"1e1", 17}, {"1e2", 18}, {"1e3", 19} // Emulated Room 1
};
const int totalPins = 7;

void setup() {
  Serial.begin(115200);
  
  // Initialize all 7 pins as outputs
  for(int i=0; i < totalPins; i++) {
    pinMode(myPins[i].pin, OUTPUT);
    digitalWrite(myPins[i].pin, LOW); 
  }

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nSingle-Unit Controller Ready");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Sending an empty POST to request the shared JSON
    int httpResponseCode = http.POST("{}"); 

    if (httpResponseCode == 200) {
      String response = http.getString();
      StaticJsonDocument<512> doc;
      deserializeJson(doc, response);

      // Loop through the shared JSON and apply to all 7 pins
      for (int i = 0; i < totalPins; i++) {
        if (doc.containsKey(myPins[i].key)) {
          int targetState = doc[myPins[i].key];
          digitalWrite(myPins[i].pin, (targetState == 1) ? HIGH : LOW);
        }
      }
    }
    http.end();
  }
  delay(1000); // Ping once per second
}