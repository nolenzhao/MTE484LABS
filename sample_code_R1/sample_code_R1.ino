#include <Arduino.h>
#include "geeWhiz.h"

// ================== Pins ==================
int MOT_PIN = A0;   // motor angle sensor
int BAL_PIN = A1;   // ball position sensor


// ================== Setup ==================
void setup() {

  pinMode(A5, OUTPUT);   // A5 can be used to measure cycle time using an oscilloscope by connecting the scope to the Arduino Box Motor Leads
  Serial.begin(115200);
  delay(300);

  geeWhizBegin();
  set_control_interval_ms(100); // 100 ms loop
  setMotorVoltage(0.0f);

  Serial.println("geeWhiz Started");
}

// ================== Loop ==================

static constexpr float Kp = 18.0f;
static constexpr float pi = 3.141592;
static constexpr float m = - pi/ 228;
static constexpr float x = 7.03;
static constexpr float target = 0;


void  loop() {

  float motor_val = analogRead(MOT_PIN);
  float motor_pos = m * motor_val + x; 
  float err = motor_pos - target;
  // Proportional Controller
  float u_z = Kp * err; 

  if(motor_pos > 0.7){
    motor_pos = 0.7;
  }

  if(motor_pos < -0.7){
    motor_pos = -0.7;
  }

  if(u_z > 0){
    setMotorVoltage(u_z + 0.26);
  }
  else{
    setMotorVoltage(u_z - 0.21);    
  }


  Serial.print(millis());
  Serial.print(","); 
  Serial.println(motor_pos);
}

// ================== Control ISR ==================
void interval_control_code(void) {
  // ---- Read sensors ----
  // int motor = analogRead(MOT_PIN);
  // int ball  = analogRead(BAL_PIN);

  // digitalWrite(A5,HIGH);   // A5 can be used to measure cycle time using an oscilloscope by connecting the scope to the Arduino Box Motor Leads
  // Serial.print(ball);
  // Serial.print(",");
  // Serial.println(motor);
  // digitalWrite(A5,LOW);   // A5 can be used to measure cycle time using an oscilloscope by connecting the scope to the Arduino Box Motor Leads
 
}