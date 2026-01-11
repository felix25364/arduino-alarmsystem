# Smart Security Keypad & Intrusion Alert System

This project is a multi-device security system that combines an Arduino Nano-based keypad, an ESP32-CAM, and a Python-driven backend to provide physical access control and remote monitoring.

The system detects unauthorized access attempts or door activity, captures images via the ESP32-CAM, uploads them to a local FTP server, and triggers email notifications and automated phone calls.
🛠 System Overview

The system consists of three main layers:

    Access Control (Arduino Nano): Manages the 4x4 Keypad and a door switch. It communicates with the ESP32-CAM via Serial.

    Imaging (ESP32-CAM): Captures 10 images upon receiving a trigger and uploads them to an FTP server.

    Alert Engine (Python/Raspberry Pi): Hosts the FTP server, monitors for new images, sends emails with attachments, and initiates SIP phone calls.

📂 File Structure & Descriptions
1. arduino-nano.ino

The "brain" of the physical lock.

    Keypad Management: Handles input from a 4x4 matrix keypad.

    Security Logic: Compares entered pins against a hardcoded code (9111).

    Auto-Lock: Features a 30-minute auto-lock timer if the door switch is closed.

Trigger: Sends a "START" signal via Serial to the ESP32-CAM when the door is opened or a pin is entered.

2. esp32-cam.ino

The imaging module.

    WiFi & Camera: Connects to WiFi via WiFiManager and initializes the AI-Thinker camera module.

    Image Capture: Upon receiving "START" from Serial, it captures 10 JPEG images.

    Storage & Transfer: Saves images to an SD card and simultaneously uploads them to a specified FTP server.

3. alarm.py

The backend monitoring script (intended for a Linux environment like a Raspberry Pi).

    FTP Server: Hosts a local FTP server to receive images from the ESP32-CAM.

    Email Notifications: Sends an email via Gmail SMTP with the captured images attached when activity is detected.

    Phone Alerts: Executes a shell script to trigger SIP calls if intruders are detected.

4. call.sh

A Bash script using baresip to automate outgoing SIP calls to a list of predefined phone numbers.
🚀 Setup Instructions
Hardware Connections

    Keypad: Connect to Arduino Pins 9, 8, 7, 6 (Rows) and 5, 4, 3, 2 (Cols).

    LEDs: Green Pin 11, Red Pin 10.

    Serial Link: Connect Arduino TX to ESP32-CAM RX (ensure logic level shifting if necessary, as ESP32 is 3.3V).

Software Configuration

    Arduino/ESP32: * Flash arduino-nano.ino to your Arduino.

        Update FTP credentials in esp32-cam.ino (FTP_SERVER, FTP_USER, FTP_PASS).

        Flash esp32-cam.ino to the ESP32-CAM.

Python Backend:

        Install dependencies: pip install pyftpdlib.

        Update alarm.py with your SMTP settings and destination phone numbers.

        Ensure baresip is installed and configured on your system for the calling feature.

Running the System

    Start the Python script:
    Bash

    python3 alarm.py

    The script will start the FTP server and begin monitoring the ./foto-usent directory.

    Enter the correct PIN on the Keypad to unlock, or trigger the door switch to start the capture sequence.

🛡 Security Features

    Visual Evidence: 10-image burst capture for every event.

    Redundancy: Images are stored on both the local SD card and a remote FTP server.

    Multi-Channel Alert: Instant notification via Email and Phone Call.

    Auto-Timeout: System automatically re-arms after 30 minutes of inactivity.
