#include <Wire.h> // Enable this line if using Arduino Uno, Mega, etc.
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"
#include "Time.h"﻿
#include <Adafruit_RGBLCDShield.h>
#include <utility/Adafruit_MCP23017.h>
#include "city_state.h"

//setting up pins
Adafruit_7segment matrix = Adafruit_7segment();
Adafruit_RGBLCDShield lcd = Adafruit_RGBLCDShield();

#define RED 0x1
#define YELLOW 0x3
#define GREEN 0x2
#define TEAL 0x6
#define BLUE 0x4
#define VIOLET 0x5
#define WHITE 0x7

const int num_pin = 3;
const int move_pin = 4;
const int dirPin = 7; 
const int stepperPin1 = 6;
int digit[] = {1,8,1,2,4};
int time_digit[] = {0,0,1,0,0};
int change_p = 0;     
int i =0;
int mov;

unsigned long nextTime = 0;

unsigned long lastDebounceTime_move = 0;
unsigned long lastDebounceTime_plus = 0;
unsigned long lastDebounceTime_dir_but = 0;
int debounceDelay = 250;

boolean display_time;
boolean cur_blink_status;
boolean time_setup;

int arr_length = 20;
char city_name1[30];
char city_name2[30];
char weather[20];
char precip[20];
char city[20];
char temp[20];
char inData[20]; // Allocate some space for the string
char inChar; // Where to store the character read
byte index = 0; // Index into array; where to store the character
boolean start_printing = false;

int buttons = 0;
int state_count = 0;
int city_count = -2;
int cur_city_count = 0;
int city_n = 0;
boolean select_state = false;
boolean select_city = false;
unsigned long lastDebounceTime_but = 0;

void setup() {
#ifndef __AVR_ATtiny85__
  Serial.begin(9600);
  //Serial.println("7 Segment Backpack Test");
#endif
  matrix.begin(0x70);
  Serial.begin(9600);
  pinMode(num_pin,INPUT_PULLUP);
  pinMode(move_pin,INPUT_PULLUP);
  pinMode(dirPin, OUTPUT);
  pinMode(stepperPin1, OUTPUT);
  display_time = true;
  time_setup = false;
  lcd.begin(16, 2);
  lcd.setBacklight(GREEN);
  Serial.println("ready to go");
}

void loop() {
  if(Serial.available()){
    if(index < arr_length){
      inChar = Serial.read(); // Read a character
      inData[index] = inChar; // Store it
      if(inData[index] == '!'){ //check terminater
        update_info(inData[0],index);
        clear_inData();
        index = 0;
      }else{ index++;}
    }
  }
  
  if(start_printing){
    print_current_weather();
    start_printing = false;
  }
  
  mov = digitalRead(move_pin);
  if(mov ==0 && millis()>lastDebounceTime_move && display_time){   //enter the time setting mode 
    display_time = false;
    lastDebounceTime_plus = millis();
    lastDebounceTime_move = millis() + debounceDelay;
  }
  
  if(display_time){
    matrix_display(time_digit);
    matrix.writeDisplay();     //normal time display
  }else{
    change_digit(change_p);
    blink_digit(change_p);
    mov = digitalRead(move_pin);
    if(mov ==0 && millis()>lastDebounceTime_move){ //debouncing 
      change_p += 1;
      if(change_p == 2) change_p = 3;
      if(change_p == 5){
        display_time = true;
        time_setup = true;
        change_p = 0;
      }
      lastDebounceTime_move = millis() + debounceDelay;
    }
    matrix.writeDisplay();
  }
  buttons = lcd.readButtons();
  if(buttons == 1 && millis()>lastDebounceTime_but && !select_state && !select_state){
      //Serial.println(33);
      select_state = true;
      select_city = false;
      lastDebounceTime_but = millis() + debounceDelay;
  }
  if(select_state && millis() > lastDebounceTime_dir_but && !select_city){
    state_count = choose_state(state_count);
    state_print(state_count);
    if(buttons == 1 &&  millis()>lastDebounceTime_but){
      select_state = false;
      select_city = true;
      lcd.clear();
      Serial.println("selecting cities");
      lastDebounceTime_but = millis() + debounceDelay;
    }
    lastDebounceTime_dir_but = millis() + debounceDelay;
  }
  
  if(!select_state && select_city && millis() > lastDebounceTime_dir_but){
    if(cur_city_count- city_count> 1 || cur_city_count<city_count){
      lcd.clear();
      city_count = cur_city_count;
      if(cur_city_count<city_count) city_count -=1;
      city_n = get_city_num(state_count, city_count);
      Serial.print('#');
      Serial.println(city_n);
    }
    cur_city_count = choose_city(cur_city_count);
    city_print(cur_city_count);
    if(buttons == 1 &&  millis()>lastDebounceTime_but){
      select_city = false;
      city_n = get_city_num(state_count, cur_city_count);
      Serial.print('@');
      Serial.println(city_n);
      lastDebounceTime_but = millis() + debounceDelay;
    }
    lastDebounceTime_dir_but = millis() + debounceDelay;
  }
  
  if(compare_time(time_digit, digit) && time_setup){
    Serial.println("working");
    step(true,500);
  } 
}

int choose_state(int st_count){
  switch(buttons){
    case 2:  //right
      Serial.print("right");
      st_count = st_count + 1;
      if(st_count>54) st_count = 54;
      Serial.println(st_count);
      break;
    case 16:  //
      Serial.print("left");
      st_count = st_count - 1;
      if(st_count <0) st_count = 0;
      Serial.println(st_count);
      break;
    case 8:  //up
      Serial.print("up");
      st_count = st_count - 5;
      if(st_count <0) st_count = 0;
      Serial.println(st_count);
      break;
    case 4:  //down
      Serial.print("down");
      st_count = st_count + 5;
      if(st_count>54) st_count = 54;
      Serial.println(st_count);
      break;
  }
  return st_count;
}

void state_print(int st_count){
  int stat_pos = (st_count/10)*10;
  for(int i = stat_pos;i<stat_pos+10;i++){
    if(i<=54){
      lcd.print(" ");
      lcd.print(state_str[i]);
      if(i == stat_pos+4) lcd.setCursor(0, 1);
    }
    if(i== 54) lcd.print("                ");
  }
  lcd.setCursor((st_count%5)*3, (st_count/5)%2);
  lcd.print("*");
  lcd.setCursor(0,0); //back to initial
}

int choose_city(int ct_count){
  int m = state_city_num[state_count]-1;
  switch(buttons){
    case 4:  //right
      //Serial.print("right");
      ct_count = ct_count + 1;
      if(ct_count> m) ct_count = m;
      //Serial.println(ct_count);
      break;
    case 8:  //
      //Serial.print("left");
      ct_count = ct_count - 1;
      if(ct_count <0) ct_count = 0;
      //Serial.println(ct_count);
      break;
  }
  return ct_count;
}

int get_city_num(int st_count, int ct_count){
  int result = 0;
  for(int i=0;i<st_count;i++){
    result = result + state_city_num[i];
  }
  result = result + ct_count;
  return result;
}

void city_print(int cur_city_c){
  lcd.print(" ");
  print_arr(city_name1);
  lcd.setCursor(0,1);
  lcd.print(" ");
  print_arr(city_name2);
  lcd.setCursor(0,cur_city_c%2);
  lcd.print("*");
  lcd.setCursor(0,0); //back to initial
  clear_all();
}

void print_arr(char arr[]){
  int i = 0;
  for(i = 0;i<20;i++){
    if(arr[i]!=0){
      Serial.print(arr[i]);
      lcd.print(arr[i]);
    }
  }
}

void print_current_weather(){
  lcd.clear();
  print_arr(city);
  lcd.print(" ");
  print_arr(temp);
  lcd.setCursor(0, 1);  
  print_arr(weather);
  lcd.setCursor(0,0);
  clear_all();
}

void clear_inData(){
  for(int i = 0; i<arr_length;i++){
    inData[i] = '/0';
  }
}

void clear_all(){
  for(int i=1;i<arr_length;i++){
       city[i] = (char) 0;
  }
  for(int i=1;i<arr_length;i++){
       weather[i] = (char) 0;
  }
  for(int i=1;i<arr_length;i++){
       precip[i] = (char) 0;
  }
  for(int i=1;i<arr_length;i++){
       city_name1[i] = (char) 0;
  }for(int i=1;i<arr_length;i++){
       city_name2[i] = (char) 0;
  }
  
}
void update_info(char first_digit, int index){
   if(first_digit == '$'){
     for(int i=1;i<index;i++){
       city[i] = inData[i];
     }
   }else if(first_digit == '%'){
     for(int i=1;i<index;i++){
       weather[i] = inData[i];
     }
   }else if(first_digit == '&'){
     
     for(int i=1;i<index;i++){
       precip[i] = inData[i];
     }
     
   }else if(first_digit == '+'){
     for(int i=1;i<index;i++){
       temp[i] = inData[i];
       start_printing = true;
     }
   }else if(first_digit == '/'){
     for(int i=1;i<index;i++){
       if(i <=2) time_digit[i-1] = int(inData[i]) - 48;
       if(i>2)   time_digit[i] = int(inData[i]) - 48;
   }
   }else if(first_digit == '('){
     for(int i=1;i<index;i++){
       city_name1[i] = inData[i];
     }
   }else if(first_digit == ')'){
     for(int i=1;i<index;i++){
       city_name2[i] = inData[i];
     }
   }
}


void step(boolean dir,int steps){
  digitalWrite(dirPin,dir);
  for(int i=0;i<steps;i++){
    digitalWrite(stepperPin1, HIGH);
    delayMicroseconds(600);
    digitalWrite(stepperPin1, LOW);
    //delayMicroseconds(100);
  }
}

void arr_display(int arr[]){
  for(int x = 0; x<=sizeof(arr);x++){
      Serial.print(arr[x]);
      Serial.print("  ");
  }
  Serial.println();
}

void matrix_display(int arr[]){
  for(int i=0;i<5;i++){
    if(i==2){
      matrix.drawColon(arr[2]);
    }else
    {
      matrix.writeDigitNum(i,arr[i]);
    }
  }
}

void blink_digit(int blink_point){
  
  int half_blink_period = 350;
  unsigned long t = millis();
  if(t>nextTime){
    cur_blink_status = !cur_blink_status;
    matrix_display(digit);
    if(cur_blink_status){
      matrix.writeDigitNum(blink_point,-1);
    }else{
      matrix.writeDigitNum(blink_point,digit[blink_point]);
    }  
    nextTime = millis()+ half_blink_period;
  }
}
  
void change_digit(int change_point){
  int plus = digitalRead(num_pin); //Serial.println(dirPinplus); //Serial.println(plus);
  if(plus == 0 && millis()>lastDebounceTime_plus){
    digit[change_point] +=1;
    if(digit[change_point]  == 10 && change_point == 4) digit[change_point] = 0;   //boundary
    if(digit[change_point]  == 7 && change_point == 3) digit[change_point] = 0;
    if(digit[change_point]  == 10 && change_point == 1) digit[change_point] = 0;
    if(digit[change_point]  == 3 && change_point == 0) digit[change_point] = 0;
    lastDebounceTime_plus = millis() + debounceDelay;
  }
}


boolean compare_time(int time_digit[], int digit[]){
  int x = 0;
  for(x=0;x<5;x++){
    if(time_digit[x] != digit[x]){
      return false;
    }
  }
  return true;
}
