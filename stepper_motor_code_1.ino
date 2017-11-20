
#include "Time.h"﻿
//setting up pins

int dirPin1= 7; 
int stepperPin1= 6;
int dirPin2 = 3;
int stepperPin2 = 2;
void setup() {
  pinMode(dirPin1, OUTPUT);
  pinMode(stepperPin1, OUTPUT);
}
//setting up whatever step is...(a method?)
void step(boolean dir,int steps){
  digitalWrite(dirPin1,dir);
  delay(50);
  for(int i=0;i<steps;i++){
    digitalWrite(stepperPin1, HIGH);
    delayMicroseconds(100);
    digitalWrite(stepperPin1, LOW);
    delayMicroseconds(100);
  }
}
//making it spin
void loop(){ //step is the method for making it spin
  step(true,1600*1000);  // false controls the directions
  delay(100); 
  //step(false,1600*1);
  //delay(100);
}


//to control another motor, see sample code and and pins to control second motor
