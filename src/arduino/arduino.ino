//#define ledPin 13
int ledPin = 13;
void setup() {
  Serial.begin(9600);
  pinMode(A15, INPUT);
  pinMode(ledPin, OUTPUT);
}

int ledState = LOW;
unsigned long previousMillis = 0;

int last = 0;
int last2 = 0;

void loop() {
  int a3 = analogRead(A14);
  
  Serial.println((a3+last)/2);
//  Serial.println(a3);
  last2 = last;
  last = a3;

  unsigned long currentMillis = millis();
  // Comment

  if (currentMillis - previousMillis >= 1000) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }

    // set the LED with the ledState of the variable:
    digitalWrite(ledPin, ledState);
  }
}