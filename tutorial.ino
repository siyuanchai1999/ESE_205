int r = 1;
void setup(){
  Serial.begin(9600);
}

void loop(){
  /*Serial.println("Hello World!");
  delay(2000);*/
  if(Serial.available()){
    r = r * (Serial.read() - '0');
    Serial.println(r);
  }
}

