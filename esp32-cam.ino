#include <WiFiManager.h>      // für einfaches WLAN Setup
#include <WiFi.h>
#include <FS.h>
#include <SD_MMC.h>
#include "esp_camera.h"
#include <ESP32_FTPClient.h>   // FTP Bibliothek

// ESP32-CAM Pins (AI-Thinker)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

char data[6];  // 5 Bytes + Nullterminator

// FTP Einstellungen
#define FTP_SERVER   "192.168.178.197"   // FTP Server IP
#define FTP_USER     "felix"
#define FTP_PASS     "geheim"
#define FTP_PATH     "/"

ESP32_FTPClient ftp(FTP_SERVER, FTP_USER, FTP_PASS);

void setup() {
  Serial.begin(115200);

  // WLAN mit WiFiManager verbinden
  WiFiManager wm;
  wm.autoConnect("ESP32-CAM");

  Serial.println("WLAN verbunden: " + WiFi.localIP().toString());

  // Kamera konfigurieren
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Kamera Init fehlgeschlagen");
    return;
  }

  // SD Karte mounten
  if(!SD_MMC.begin()){
    Serial.println("SD-Karte Fehler");
    return;
  }

  Serial.println("Setup fertig – sende 5 Zeichen, z.B. START");
}

void loop() {
  if (Serial.available() >= 5) {
    int bytesRead = Serial.readBytes(data, 5);
    data[bytesRead] = '\0';  // String terminieren

    Serial.print("Empfangen: ");
    Serial.println(data);

    if (strcmp(data, "START") == 0) {  // hier Trigger-Befehl
      Serial.println("Starte Capture Sequence...");

      for(int i = 0; i < 10; i++){
        // Bild aufnehmen
        camera_fb_t * fb = esp_camera_fb_get();
        if(!fb){
          Serial.println("Kamera Fehler");
          continue;
        }

        String filename = "/image" + String(millis()) + ".jpg";
        File file = SD_MMC.open(filename.c_str(), FILE_WRITE);
        if(!file){
          Serial.println("Konnte Datei nicht öffnen");
        } else {
          file.write(fb->buf, fb->len);
          file.close();
          Serial.println("Bild gespeichert: " + filename);

          // FTP Upload
          ftp.OpenConnection();

          File fileUp = SD_MMC.open(filename.c_str());
          if(fileUp){
              ftp.InitFile("Type I");
              ftp.NewFile(filename.c_str());

              const size_t bufSize = 512;
              uint8_t buf[bufSize];
              size_t bytesReadF;

              while((bytesReadF = fileUp.read(buf, bufSize)) > 0){
                  ftp.WriteData(buf, bytesReadF);
              }

              fileUp.close();
              ftp.CloseFile();
              Serial.println("Bild hochgeladen: " + filename);
          } else {
              Serial.println("Konnte Datei für FTP nicht öffnen: " + filename);
          }

          ftp.CloseConnection();
        }
          
        esp_camera_fb_return(fb);
        delay(1000);
      }

      Serial.println("Capture Sequence abgeschlossen");
    }
  }
}
