#include <Arduino.h>
#include "geeWhiz.h"

// ================== Pins ==================
int MOT_PIN = A0;   // motor angle sensor
int BAL_PIN = A1;   // ball position sensor

static constexpr int num_size = 4;
static constexpr int denom_size = 5;
double numerator[num_size] = {5.220991266182068, 2.19347716081792, 3.01262904487014, -1.945180614295883}; 
double denominator[denom_size] = {1.0f, 0.4237, 0.446101301973525, 0.260556510434016, 0.078940914984297};
// double numerator[num_size] = {5.221, 2.1935, 3.0126, -1.9452}; 
// double denominator[denom_size] = {1.0f, 0.4237, 0.4461, 0.2606, 0.0789};
float errors[num_size] = {0, 0, 0, 0};
float cont_output[denom_size - 1] = {0, 0, 0, 0};
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

static constexpr float Kp = 16.0f;
static constexpr float pi = 3.141592;
static constexpr float m = - pi/ 228;
static constexpr float x = 7.03;
static float target = 0.7;
static constexpr float cw_stiction = 0.26;
static constexpr float ccw_stiction = -0.21;
static int cnter = 0;


void  loop() {

  // Proportional Controller
  // float u_z = Kp * err; 

  float clamped_target = target;
  if (clamped_target > 0.7) {
    clamped_target = 0.7;
  }

  if(cnter >= 128){
    target = -target;
    cnter = 0;
  }
  cnter++;


  // Calculate motor_encoder value, and corresponding motor position
  float motor_val = analogRead(MOT_PIN);
  float motor_pos = m * motor_val + x; 

  // Calculate Error 
  float err = motor_pos - clamped_target;


  // Move errors back 
  for(int i = num_size - 1; i > 0; i--){
    errors[i] = errors[i-1];
  }
  // Update front of errors array 
  errors[0] = err;

  for(int i = denom_size -1; i > 0; i--){
    cont_output[i] = cont_output[i-1];
  }


  float curr_cont_output = 0;

  for(int i = 0; i < num_size; i++){
    curr_cont_output += numerator[i] * errors[i];
  }
  for(int i = 1; i < denom_size; i++){
    curr_cont_output -= denominator[i] * cont_output[i];
  }

  curr_cont_output /= denominator[0];
  if(abs(err) <= 0.018){
    setMotorVoltage(0);
  }
  else{
    if(curr_cont_output > 0){
      setMotorVoltage(curr_cont_output + cw_stiction);
    }
    else{
      setMotorVoltage(curr_cont_output + ccw_stiction);    
    }
  }


  cont_output[0] = curr_cont_output;



  delay(21);
  
  Serial.print(millis()); 
  Serial.print(",");
  Serial.print(err);
  Serial.print(",");
  Serial.print(curr_cont_output);
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