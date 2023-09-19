#include <MPU6050_2.h>
#include <MPU6050_1.h>
#include <Wire.h>
#include <PMW3389.h>
#include <SPI.h> 

//Initializing MPU's from libraries 
MPU6050 mpu6050_1(Wire);
MPU60502 mpu6050_2(Wire); //Addressed at 0x69 and 5V on sensor is connected to AD0 

/*
# PIN CONNECTION for PMW3389 with reference to Arduino MEGA 2560 
  * MI = MISO Pin 50 
  * MO = MOSI Pin 51 
  * SS = Slave Select / Chip Select depends on PMW3389 see code below 
  * SC = SPI Clock Pin 52 
  * MT = Motion (active low interrupt line) not necessary in this code 
  * RS = Reset not necessary 
  * GD = Ground 
  * VI = Voltage in up to +5.5V
*/
long timer = millis();

long prevTimeSinceStart = millis();

//Initializing PMW3389's from the library 
PMW3389 sensor1; //uses SS at pin 53 
float x1=0;
float y1=0;  

PMW3389 sensor2; //uses SS at Pin 40 
float x2=0; 
float y2=0; 

float force = 0;

float L_pitch = 0;
float L_yaw = 0;

float R_pitch = 0;
float R_yaw = 0;


float L_PMW_X = 0;
float L_PMW_X_vel = 0;
float L_PMW_X_acc = 0;
float L_PMW_Y = 0;
float L_PMW_Y_vel = 0;
float L_PMW_Y_acc = 0;

float R_PMW_X = 0;
float R_PMW_X_vel = 0;
float R_PMW_X_acc = 0;
float R_PMW_Y = 0;
float R_PMW_Y_vel = 0;
float R_PMW_Y_acc = 0;

float L_yawVel = 0;
float L_yawAcc = 0;
float L_pitchVel = 0;
float L_pitchAcc = 0;
float prev_L_yaw = 0;
float prev_L_yawVel = 0;
float prev_L_pitch = 0;
float prev_L_pitchVel = 0;

float R_yawVel = 0;
float R_yawAcc = 0;
float R_pitchVel = 0;
float R_pitchAcc = 0;
float prev_R_yaw = 0;
float prev_R_yawVel = 0;
float prev_R_pitch = 0;
float prev_R_pitchVel = 0;

float prev_L_PMW_X = 0;
float prev_L_PMW_Y = 0;
float prev_L_PMW_X_vel = 0;
float prev_L_PMW_Y_vel = 0;
float prev_R_PMW_X = 0;
float prev_R_PMW_Y = 0;
float prev_R_PMW_X_vel = 0;
float prev_R_PMW_Y_vel = 0;


void setup() {
  Serial.begin(38400);
//MPU portion 
  Wire.begin();
  mpu6050_1.begin();
  mpu6050_1.calcGyroOffsets(true);
  mpu6050_2.begin(); 
  mpu6050_2.calcGyroOffsets(true); 

   while (!Serial);

  sensor1.begin(53, 16000); // to set CPI (Count per Inch), pass it as the //52 is right ss
  sensor2.begin(40,16000); //40 is left ss

}

void loop() {
  unsigned long currentMillis = millis();
  mpu6050_1.update();
  mpu6050_2.update();
  if (currentMillis - timer > 100) {
  
    unsigned long timeSinceStart = millis();
    //MPU gets data from updates
    float L_yaw = mpu6050_2.getAngleY();
    float L_yawVel = 0;
    float L_yawAcc = 0;
    float L_pitch = mpu6050_2.getAngleX();
    float L_pitchVel = 0;
    float L_pitchAcc = 0;

    float R_yaw = mpu6050_1.getAngleY();
    float R_yawVel = 0;
    float R_yawAcc = 0;
    float R_pitch = mpu6050_1.getAngleX();
    float R_pitchVel = 0;
    float R_pitchAcc = 0;


  /* mpu6050_1.update();
    L_pitch = mpu6050_1.getAngleX();
    L_yaw = mpu6050_1.getAngleY();
    L_accX = mpu6050_1.getAccAngleX();
    L_accY = mpu6050_1.getAccAngleY();*/


    //Left MPU velocity and acceleration
    if (prev_L_yaw != 0) {
        L_yawVel = (L_yaw - prev_L_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
      }
      if (prev_L_pitch != 0) {
        L_pitchVel = (L_pitch - prev_L_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
      }

      // Accelerations
    if (prev_L_yawVel != 0) {
      L_yawAcc = (L_yawVel - prev_L_yawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_L_pitchVel != 0) {
      L_pitchAcc = (L_pitchVel - prev_L_pitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }

    //Right MPU velocity and acceleration
    if (prev_R_yaw != 0) {
        R_yawVel = (R_yaw - prev_R_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
      }
      if (prev_R_pitch != 0) {
        R_pitchVel = (R_pitch - prev_R_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
      }

      // Accelerations
    if (prev_R_yawVel != 0) {
      R_yawAcc = (R_yawVel - prev_R_yawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_R_pitchVel != 0) {
      R_pitchAcc = (R_pitchVel - prev_R_pitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }

    /*mpu6050_2.update();
    R_pitch = mpu6050_2.getAngleX();
    R_yaw = mpu6050_2.getAngleY();
    R_accX = mpu6050_2.getAccX();
    R_accY = mpu6050_2.getAccY();*/

    //Get data from PMW3389 sensors via readburst
    PMW3389_DATA data1 = sensor2.readBurst();
    PMW3389_DATA data2 = sensor1.readBurst(); 

    if (data1.isMotion || data1.isOnSurface) {
      L_PMW_X=((data1.dx)) + L_PMW_X; // converts to 1mm since 16,000 CPI 16000=32767 in two's compliment so 32767=16,000=inch=25.4mm therefore 1290=1mmm. 
      L_PMW_Y=((data1.dy)) + L_PMW_Y;  //Can measure 10cm on ruler and use that bit value to convert

    }
    if (data2.isMotion || data2.isOnSurface) {
      R_PMW_X=((data2.dx)) + R_PMW_X; // converts to 1mm since 16,000 CPI 16000=32767 in two's compliment so 32767=16,000=inch=25.4mm therefore 1290=1mmm. 
      R_PMW_Y=((data2.dy)) + R_PMW_Y;
    }

    //Left PMW velocities
    if (prev_L_PMW_X != 0) {
      L_PMW_X_vel = (L_PMW_X- prev_L_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_L_PMW_Y != 0) {
      L_PMW_Y_vel = (L_PMW_Y - prev_L_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    //Left PMW accelerations
    if (prev_L_PMW_X_vel != 0) {
      L_PMW_X_acc = (L_PMW_X_vel - prev_L_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_L_PMW_Y_vel != 0) {
      L_PMW_Y_acc = (L_PMW_Y_vel - prev_L_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }

    //Right PMW velocities
    if (prev_R_PMW_X != 0) {
      R_PMW_X_vel = (R_PMW_X- prev_R_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_R_PMW_Y != 0) {
      R_PMW_Y_vel = (R_PMW_Y - prev_R_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    //Right PMW accelerations
    if (prev_R_PMW_X_vel != 0) {
      R_PMW_X_acc = (R_PMW_X_vel - prev_R_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_R_PMW_Y_vel != 0) {
      R_PMW_Y_acc = (R_PMW_Y_vel - prev_R_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }

    //If not in motion/on surface, reset acceleration value back to zero
    if(!(data1.isMotion || data1.isOnSurface)) {
      L_PMW_X_acc = 0;
      L_PMW_Y_acc = 0;
      L_PMW_Y_vel = 0; 
      L_PMW_X_vel = 0; 
      L_PMW_Y = 0;
      L_PMW_X = 0;
    }
    if(!(data2.isMotion || data2.isOnSurface)) {
      R_PMW_X_acc = 0;
      R_PMW_Y_acc = 0;
      R_PMW_X_vel = 0;
      R_PMW_Y_vel = 0;
      R_PMW_Y = 0;
      R_PMW_X = 0;
    }

      //Force sensor read at Pin A0 
      force = (analogRead(A0)-136) * 0.011; //136 offset to try to "zero" the value

      //Trial and error 
      float xL = mpu6050_1.getAccX();
      float yL = mpu6050_1.getAccY();
      float zL = mpu6050_1.getAccZ();
      
      float xR = mpu6050_2.getAccX();
      float yR = mpu6050_2.getAccY();
      float zR = mpu6050_2.getAccZ();
  
      //Serial.println(String(R_pitch) + " " + String(R_pitchAcc) + "   " + String(R_yawAcc));

      // Division by 1000.00 to convert pitch and yaw to smaller digit value
      /*Serial.print(String(force) + "|" + String(L_pitchAcc/1000.00) + "|" + String(L_yawAcc/1000.00) + "|" + String(R_pitchAcc/1000.00) + "|" + String(R_yawAcc/1000.00) + "|" + String(L_PMW_Y_acc) + "|"
        + String(L_PMW_X_acc) + "|" + String(R_PMW_Y_acc) + "|" + String(R_PMW_X_acc) + '\n');*/
      
      /*Serial.print(String(force) + "|" + String(L_pitchAcc/1000.00) + "|" + String(L_yawAcc/1000.00) + "|" + String(R_pitchAcc/1000.00) + "|" + String(R_yawAcc/1000.00) + "|" + String(L_PMW_Y_acc) + "|"
        + String(L_PMW_X_acc) + "|" + String(R_PMW_Y_acc) + "|" + String(R_PMW_X_acc) + "|" + String(L_pitchVel/1000.00) + "|" + String(L_yawVel/1000.00) + "|" + String(R_pitchVel/1000.00) + 
        "|" + String(R_yawVel/1000.00) + "|" + String(L_PMW_Y_vel) + "|" + String(L_PMW_X_vel) + "|" + String(R_PMW_Y_vel) + "|" + String(R_PMW_X_vel) + "|" + String(L_pitch/1000.00) + 
        "|" + String(L_yaw/1000.00) + "|" + String(R_pitch/1000.00) + "|" + String(R_yaw/1000.00) + "|" + String(L_PMW_Y) + "|" + String(L_PMW_X) + "|" + String(R_PMW_Y) + "|" + String(R_PMW_X) + '\n');*/

      // Serial.print(String(force) + "|" + String(L_pitchAcc/1000) + "|" + String(L_yawAcc/1000) + "|" + String(R_pitchAcc/1000) + "|" + String(R_yawAcc/1000) + "|" + String(L_PMW_Y_acc/10) + 
      // "|" + String(L_PMW_X_acc/10) + "|" + String(R_PMW_Y_acc/10) + "|" + String(R_PMW_X_acc/10) + "|" + String(L_pitchVel) + "|" + String(L_yawVel) + "|" + String(R_pitchVel) + 
      // "|" + String(R_yawVel) + "|" + String(L_PMW_Y_vel) + "|" + String(L_PMW_X_vel) + "|" + String(R_PMW_Y_vel) + "|" + String(R_PMW_X_vel) + "|" + String(L_pitch) + 
      // "|" + String(L_yaw) + "|" + String(R_pitch) + "|" + String(R_yaw) + "|" + String(L_PMW_Y) + "|" + String(L_PMW_X) + "|" + String(R_PMW_Y) + "|" + String(R_PMW_X) + 
      // "|" + String(xR) + "|" +  String(yR) + "|" + String(zR) + "|" +  String(xL) + "|" +  String(yL) + "|" + String(zL) + "|" + String(data1.isMotion && data1.isOnSurface) + 
      // "|" + String(data2.isMotion && data2.isOnSurface) + '\n');

      Serial.println(String(force));

      //Serial.print(String(String(R_PMW_Y) + "|" + String(R_PMW_X) + '\n'));

      //Serial.print(String(data1.isMotion && data1.isOnSurface) + "|" + String(data2.isMotion && data2.isOnSurface) + '\n');

      //Serial.print(String(data1.isMotion) + "|" + String(data1.isOnSurface) +"\n");

      //Serial.print(String(force) + '\n'); 

    //Save previous values
      prevTimeSinceStart = timeSinceStart;
      prev_L_yaw = L_yaw;
      prev_L_yawVel = L_yawVel;
      prev_L_pitch = L_pitch;
      prev_L_pitchVel = L_pitchVel;

      prev_R_yaw = R_yaw;
      prev_R_yawVel = R_yawVel;
      prev_R_pitch = R_pitch;
      prev_R_pitchVel = R_pitchVel;

      prev_L_PMW_X = L_PMW_X;
      prev_L_PMW_X_vel = L_PMW_X_vel;
      prev_L_PMW_Y = L_PMW_Y;
      prev_L_PMW_Y_vel = L_PMW_Y_vel;

      prev_R_PMW_X = R_PMW_X;
      prev_R_PMW_X_vel = R_PMW_X_vel;
      prev_R_PMW_Y = R_PMW_Y;
      prev_R_PMW_Y_vel = R_PMW_Y_vel;


      //Serial.flush();
    //delay(100); 
  }

}
