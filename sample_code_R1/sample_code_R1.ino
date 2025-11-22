#include <Arduino.h>
#include "geeWhiz.h"

// ================== Pins ==================
int MOT_PIN = A0;   // motor angle sensor
int BAL_PIN = A1;   // ball position sensor

static constexpr int num_size_outer = 10;
static constexpr int denom_size_outer = 11;
static constexpr int num_size_inner = 6;
static constexpr int denom_size_inner = 7;
double numerator_inner[num_size_inner] = {2.191042856736779 , -1.244715000739053,  0.892620562448263,   0.306902605622103,   0.234368769132498,  -0.197167582568173}; 
double denominator_inner[denom_size_inner] = {  1.000000000000000,  -0.568099999998879 ,  0.341651128008823 ,  0.028556296287117 ,  0.051161768362048  , 0.029203276104001,   0.008172368274057};
// double numerator_outer[num_size_outer] = {1, -2.013, -0.3267, 3.473, -2.199, -2.214, 3.83, -0.3601, -2.328, 1.138}; 
// double denominator_outer[denom_size_outer] = {1, -1.782, -0.75, 2.797, -0.4785, -1.442, 0.4939, 0.2962, -0.1165, -0.02184, 0.0057};
double numerator_outer[num_size_outer] = {1, 1.562, -0.9023, -3.541, -2.237, 1.848, 3.283, 0.7058, -1.133, -0.5824}; 
double denominator_outer[denom_size_outer] = { 1, 1.616, -0.6473, -2.095, -0.6567, 0.2275, 0.1043, 0.1864, 0.2443, 0.1313, 0.026};
// double numerator[num_size] = {5.221, 2.1935, 3.0126, -1.9452}; 
// double denominator[denom_size] = {1.0f, 0.4237, 0.4461, 0.2606, 0.0789};
float errors_inner[num_size_inner] = {0, 0, 0, 0, 0, 0};
float cont_output_inner[denom_size_inner - 1] = {0, 0, 0, 0, 0, 0};
float errors_outer[num_size_outer] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
float cont_output_outer[denom_size_outer - 1] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

float voltage;

// ================== Setup ==================
void setup() {

  pinMode(A5, OUTPUT);   // A5 can be used to measure cycle time using an oscilloscope by connecting the scope to the Arduino Box Motor Leads
  Serial.begin(115200);
  delay(300);

  geeWhizBegin();
  set_control_interval_ms(100); // 100 ms loop
  setMotorVoltage(0.0f);

  Serial.println("geeWhiz Started");

  voltage = 0;
}

// ================== Loop ==================

static constexpr float Kp = 16.0f;
static constexpr float pi = 3.141592;
static constexpr float m = - pi/ 228;
static constexpr float x = 7.03;
static constexpr float cw_stiction = 0.26;
static constexpr float ccw_stiction = -0.21;

static int outerCnter = 0;

static constexpr float cw_stiction_beam = 0.12;
static constexpr float ccw_stiction_beam = -0.6;
float target = 0.2085;
static constexpr float BEAM_LEN = 0.417;
static constexpr float lever_len = 0.12;
static constexpr float beam_slope = 0.001064;
static constexpr float beam_intercept = -0.33088;
static constexpr float K2 = lever_len / BEAM_LEN;
static constexpr int inner_sampling = 21;
static constexpr int outer_sampling = 10 * inner_sampling;
float angle_output = 0;

void graph_k3(){
  Serial.print(millis());
  Serial.print(",");
  Serial.println(calc_ball_pos(), 3);

}

float calc_ball_pos(){
  int ball = analogRead(BAL_PIN);
  float ball_position = beam_slope * ball + beam_intercept;
  return ball_position;
}

float target_angle = 0;
int loop_cnter = 0;

void  loop() {

  // Proportional Controller
  // float u_z = Kp * err;





  // make sure angle_outputisnt being set in innner loop to 0 after updating // sepearted when the inner lop reads from angle_output

  // if(outerCnter == 30){
  //   angle_output = 0;
  //   for(int i = num_size_outer - 1; i > 0; i--){
  //     errors_outer[i] = errors_outer[i-1];
  //   }
  //   float err = target-calc_ball_pos();

  //   Serial.print("Error: "); 
  //   Serial.print(err);
  //   // Update front of errors array 
  //   errors_outer[0] = err;


  //   for(int i = denom_size_outer - 2; i > 0; i--){
  //     cont_output_outer[i] = cont_output_outer[i-1];
  //   }

  //   for(int i = 0; i < num_size_outer; i++){
  //     angle_output += numerator_outer[i] * errors_outer[i];
  //   }
  //   for(int i = 1; i < denom_size_outer; i++){
  //     angle_output -= denominator_outer[i] * cont_output_outer[i];
  //   }

  //   angle_output /= denominator_outer[0];
  //   cont_output_outer[0] = angle_output;
  //   outerCnter = 0;

  //   Serial.print("angle output: ");
  //   Serial.print(angle_output);
    
  // } 
  float err = 0;

  float motor_val = analogRead(MOT_PIN);
  float motor_pos = m * motor_val + x; 

  target_angle = motor_pos + 0.001 * loop_cnter;

    
  // Serial.print("Current angle: ");
  Serial.print(millis());
  Serial.print(",");
  Serial.print(motor_pos, 5);
  Serial.print(","); 
  // Serial.print("target_angle: "); 
  Serial.print(target_angle, 5);
  Serial.print(","); 
  


  err = motor_pos - target_angle;
  Serial.print(err, 5);

  Serial.println(",");
  


  float clamped_angle = angle_output;
  if (clamped_angle > 0.7) {
    clamped_angle = 0.7;
  }
  else if(clamped_angle < -0.7){
    clamped_angle = -0.7;
  }
  // Serial.print("clamped angle");
  // Serial.print(clamped_angle);

  // Remember to uncomment this 
  // // // Calculate motor_encoder value, and corresponding motor position
  // float motor_val = analogRead(MOT_PIN);
  // float motor_pos = m * motor_val + x; 

  // // Calculate Error 
  // float err = motor_pos - clamped_angle;

  // Move errors back 
  for(int i = num_size_inner - 1; i > 0; i--){
    errors_inner[i] = errors_inner[i-1];
  }
  // Update front of errors array 
  errors_inner[0] = err;


  for(int i = denom_size_inner - 2; i > 0; i--){
    cont_output_inner[i] = cont_output_inner[i-1];
  }


  float curr_cont_output = 0;

  for(int i = 0; i < num_size_inner; i++){
    curr_cont_output += numerator_inner[i] * errors_inner[i];
  }
  for(int i = 1; i < denom_size_inner; i++){
    curr_cont_output -= denominator_inner[i] * cont_output_inner[i];
  }

  curr_cont_output /= denominator_inner[0];

  if(abs(err) <= 0.02){
    setMotorVoltage(0);
  }
  else{
    if(curr_cont_output > 0){
      setMotorVoltage(curr_cont_output + cw_stiction_beam);
    }
    else{
      setMotorVoltage(curr_cont_output + ccw_stiction_beam);    
    }
  }

  cont_output_inner[0] = curr_cont_output;

  delay(inner_sampling);
  outerCnter++;

  // Serial.println("");

  loop_cnter++;
  delay(500);

  // float b_pos = calc_ball_pos();
  // Serial.print(millis()); 
  // Serial.print(",");
  // Serial.print(err);
  // Serial.print(",");
  // Serial.print(curr_cont_output);
  // Serial.print(","); 
  // Serial.print(motor_pos);
  // Serial.print(",");
  // Serial.println(b_pos);
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