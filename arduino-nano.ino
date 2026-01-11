#include <Keypad.h>

// Pinlänge und Pincode festlegen
const byte PINLENGTH = 4;
char pinCode[PINLENGTH+1] = {'9','1','1','1'};
char keyBuffer[PINLENGTH+1] = {'-','-','-','-'};

// 4x4 Keypad Definition
const byte ROWS = 4;
const byte COLS = 4;

char hexaKeys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};

// LEDs
const int greenPin = 11;
const int redPin = 10;
const int openDelay = 3000;
const int sensePin = 13;

// Button Pin für Capture / Switch
const int buttonPin = 12;

// Zustände merken
bool pinIsCorrect = false;
bool locked = true;
bool lastButtonState = HIGH; // assume pullup
unsigned long closeStart = 0; // wann Switch geschlossen wurde
const unsigned long autoLockTime = 1800000UL; // 30 min in ms (30*60*1000)

// Keypad
Keypad customKeypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);

void setup() {
  Serial.begin(115200);
  pinMode(greenPin, OUTPUT);
  pinMode(redPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); // Taster/Switch nach GND
  digitalWrite(greenPin, LOW);
  digitalWrite(redPin, LOW);
}

void loop() {
  // --- Keypad-Abfrage ---
  char customKey = customKeypad.getKey();

  if (customKey) {
    if ((customKey >= '0') && (customKey <= '9')) {
      addToKeyBuffer(customKey);
    }
    else if (customKey == '#') {
      checkKey();
    }
    else if (customKey == 'D' && pinIsCorrect) {
      // Schloss sperren
      lockSystem();
    }
    else if (customKey == '*' || customKey == 'C') {
      clearBuffer();  // Eingabe löschen
    }
  }

  // --- Button/Switch-Abfrage ---
  bool buttonState = digitalRead(buttonPin);

  // Kante erkennen: Button losgelassen
  if (lastButtonState == LOW && buttonState == HIGH) {
    if (!pinIsCorrect) {
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
    } else if (pinIsCorrect && locked) {
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
      Serial.println("START");
    }
  }

  // Wenn Schloss offen UND Switch geschlossen -> Timer starten
  if (pinIsCorrect && !locked) {
    if (buttonState == LOW) {
      // Switch geschlossen
      if (closeStart == 0) {
        closeStart = millis(); // Startzeit merken
      } else {
        // prüfen ob schon 30 Min rum sind
        if (millis() - closeStart >= autoLockTime) {
          Serial.println("AUTO LOCKED (30min timeout)");
          lockSystem();
          closeStart = 0;
        }
      }
    } else {
      // Switch wieder offen -> Timer zurücksetzen
      closeStart = 0;
    }
  }

  lastButtonState = buttonState;
}

// ------------------- Funktionen -------------------
void addToKeyBuffer(char inkey) {
  Serial.print(inkey);
  Serial.print(" > ");
  for (int i=1; i<PINLENGTH; i++) {
    keyBuffer[i-1] = keyBuffer[i];
  }
  keyBuffer[PINLENGTH-1] = inkey;
  Serial.println(keyBuffer);
}

void checkKey() {
  if (strcmp(keyBuffer, pinCode) == 0) {
    Serial.println("CORRECT");
    pinCorrect();
  } else {
    Serial.println("WRONG!");
    pinWrong();
  }
  clearBuffer(); // nach Eingabe automatisch wieder löschen
}

void pinCorrect() {
  pinIsCorrect = true;
  locked = false;
  Serial.println("ACCESS GRANTED");
  digitalWrite(greenPin, HIGH);
  delay(openDelay);
  digitalWrite(greenPin, LOW);
}

void pinWrong() {
  for (int i=0; i<3; i++) {
    digitalWrite(redPin, HIGH);
    delay(50);
    digitalWrite(redPin, LOW);  
    delay(20);
  }
  pinIsCorrect = false;
}

void clearBuffer() {
  for (int i=0; i < PINLENGTH; i++) {
    keyBuffer[i] = '-';
  }
  Serial.println("CLEARED");
}

void lockSystem() {
  Serial.println("LOCKED");
  pinIsCorrect = false;
  locked = true;
  digitalWrite(greenPin, LOW);
}
