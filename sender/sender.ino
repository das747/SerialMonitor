byte a = 0;

void setup() {
  Serial.begin(9600);

}

void loop() {
  if(Serial.available()){
    a = Serial.read();
  }
  Serial.println((String) (millis() / 1000) + ';' + (millis() / 1000) + ';' +"test" + ';' + a);
  delay(100);
}
