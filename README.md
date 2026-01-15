# Arduino Intrusionn Detection System
This is a alarm/intrusion detection system I made with a ESP32-CAM and some other easy to get components

## components:
    ESP32-CAM
    Arduino Nano
    4x4 Matrix Keypad
    2 different color LEDs (red and green recommended)
    push button or similar
    optinal: 3D-printer for the case

## setup:
1. set-up the python script and note down the IP of that computer (should be something thats online 24/7)
2. configure FTP-Server IP, login data and pin code in the esp32-cam.ino file
3. flash the files to the microcontrollers
4. setup baresip and add phone numbers to the python script 
