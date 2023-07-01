#include <Arduino.h>

// Get MeteoFrance API JSON
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// Infrastructure
#include <NTPClient.h>
#include <Syslog.h>
#include <WiFiManager.h>
#include <WiFiUdp.h>

#define LED_PIN D4

#define LED_ON LOW
#define LED_OFF HIGH

// Get Time
WiFiUDP ntpUDP;
NTPClient ntp(ntpUDP, NTP_SERVER);

WiFiUDP logUDP;
Syslog syslog(logUDP, SYSLOG_PROTO_IETF);


void setup() {
  WiFi.mode(WIFI_STA);
  WiFi.hostname(HOSTNAME);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LED_ON);

  Serial.begin(SERIAL_SPEED);
  Serial.println("\nStarting " PROGNAME " v" VERSION " " __DATE__ " " __TIME__);

  // Syslog setup
  syslog.server(SYSLOG_SERVER, SYSLOG_PORT);
  syslog.deviceHostname(HOSTNAME);
  syslog.appName("Joba1");
  syslog.defaultPriority(LOG_KERN);

  digitalWrite(LED_PIN, LED_OFF);

  WiFiManager wm;
  // wm.resetSettings();
  if (!wm.autoConnect()) {
    Serial.println("Failed to connect WLAN");
    for (int i = 0; i < 1000; i += 200) {
      digitalWrite(LED_PIN, LED_ON);
      delay(100);
      digitalWrite(LED_PIN, LED_OFF);
      delay(100);
    }
    ESP.deepSleep(60 * 1000000);
    while (true)
      ;
  }

  digitalWrite(LED_PIN, LED_ON);
  ntp.begin();
  char msg[80];
  snprintf(msg, sizeof(msg), "%s Version %s, WLAN IP is %s", PROGNAME, VERSION,
           WiFi.localIP().toString().c_str());
  Serial.printf(msg);
  syslog.logf(LOG_NOTICE, msg);
}


bool check_ntptime() {
  static bool have_time = false;
  if (!have_time && ntp.getEpochTime() > 30UL * 365 * 24 * 3600) {
    have_time = true;
    time_t now = time(NULL);
    char start_time[30];
    strftime(start_time, sizeof(start_time), "%FT%T%Z", localtime(&now));
    syslog.logf(LOG_NOTICE, "Booted at %s", start_time);
  }
  return have_time;
}


// Get data from MeteoFrance API
bool get_data() {
  static const char uri[] = "http://api.open-meteo.com/v1/meteofrance?latitude=" LATITUDE "&longitude=" LONGITUDE 
    "&hourly=direct_radiation,diffuse_radiation,terrestrial_radiation&daily=sunrise,sunset&timezone=Europe%%2FBerlin";

  WiFiClient client;
  HTTPClient http;
  http.begin(client, uri);
  http.setUserAgent(PROGNAME);
  int status = http.GET();
  String json = http.getString();
  http.end();
  
  if (status < 200 || status > 299) {
    syslog.logf(LOG_ERR, "Get %s status=%d response='%s'", uri, status, json.c_str());
  }
  else {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, json.c_str());
    if( error ) {
      syslog.logf(LOG_ERR, "Got invalid json '%s': %s", json.c_str(), error.c_str());
    }
    else {
      const char *first = doc["hourly"]["time"][0];
      syslog.logf(LOG_INFO, "Got data for %s", first);

      // TODO now find intervals of 1, 2, 3, 4 and 5 hours of most radiation
      
      return true;
    }
  }
  return false;
}


void loop() {
  ntp.update();
  if (check_ntptime()) {
    uint64_t wait_us;
    if( get_data() ) {
      time_t now = time(NULL);
      struct tm *t = localtime(&now);
      wait_us = (3600UL - t->tm_min * 60 - t->tm_sec) * 1000000;
    }
    else {
      wait_us = 10UL * 60 * 1000000;  // retry in 10 minutes
    }
    digitalWrite(LED_PIN, LED_OFF);
    ESP.deepSleep(wait_us);
    delay(wait_us / 1000);  // if deepsleep fails just wait
  }
  delay(1);
}
