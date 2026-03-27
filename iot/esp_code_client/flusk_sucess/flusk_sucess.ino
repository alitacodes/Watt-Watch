#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "HP14fs"; 
const char* password = "12345678"; 
const char* serverUrl = "http://10.141.144.63:5000/sync"; 

// Mapping structure matching your specific pins [cite: 3]
struct PinMap { String key; int pin; };
PinMap myPins[] = {
  {"0e0", 21}, {"0e1", 22}, {"0e2", 23},
  {"1e0", 16}, {"1e1", 17}, {"1e2", 18}, {"1e3", 19}
};
const int totalPins = 7;

void setup() {
  Serial.begin(115200);
  for(int i=0; i < totalPins; i++) {
    pinMode(myPins[i].pin, OUTPUT); 
    digitalWrite(myPins[i].pin, LOW); 
  }

  WiFi.begin(ssid, password); 
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    
    int httpCode = http.GET();
    if (httpCode == 200) {
      String payload = http.getString();
      Serial.println(payload);
      StaticJsonDocument<512> doc;
      deserializeJson(doc, payload);

      // Iterate through all mapped pins and update states [cite: 7, 8]
      for (int i = 0; i < totalPins; i++) {
        if (doc.containsKey(myPins[i].key)) {
          int targetState = doc[myPins[i].key];
          digitalWrite(myPins[i].pin, (targetState == 1) ? HIGH : LOW);
        }
      }
    }
    http.end();
  }
  delay(50); // Reduced delay to 50ms for even more rapid response
}