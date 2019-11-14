String a;

void setup() {
  Serial.begin(9600);

}

void loop() {
  if(Serial.available()){
    a = Serial.readString();
  }
  Serial.println((String) (millis() / 1000)  + ';' +"test" + ';' + a);
  delay(100);
}
