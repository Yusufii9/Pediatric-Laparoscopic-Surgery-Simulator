/*********************************************************************************************
Author: Atallah Madi 
Date: October 7th, 2023
Purpose: This code is used to read data from the MPU6050, PMW3389, and Force sensors.
The data is then sent to the computer via Serial. The data is then read by Python Application
This code is for the Arduino Nano Every
*********************************************************************************************/

/* Libraries  */
// ---------------------------------------------------------------
#include <MPU6050_2.h>      // Include the library for MPU6050 sensor 2
#include <MPU6050_1.h>      // Include the library for MPU6050 sensor 1
#include <PMW3389.h>        // Include the library for PMW3389 sensor
#include <Wire.h>           // Include the Wire library for I2C communication
#include <SPI.h>            // Include the SPI library for SPI communication
// ---------------------------------------------------------------

/* Initializing Libraries */
// ---------------------------------------------------------------
// PMW3389
PMW3389 sensor1; 
PMW3389 sensor2;

// MPU6050
MPU6050 mpu6050_1(Wire); 
MPU60502 mpu6050_2(Wire); 
// ---------------------------------------------------------------

/* Constants declaration, and pins declaration */
// ---------------------------------------------------------------
const int SERIAL_BAUD_RATE = 38400; // Serial baud rate

// SPI pins, digital pins
const int MISO_PIN = 12;  // MISO Pin 12, was 50 on MEGA
const int MOSI_PIN = 11;  // MOSI Pin 11, was 51 on MEGA
const int SCK_PIN = 13;   // SCK Pin 13, was 52 on MEGA
const int SS_PIN_1 = 10;  // SS Pin 10, was 53 on MEGA
const int SS_PIN_2 = 9;   // SS Pin 9, was 40 on MEGA

// I2C pins, digital pins
const int SDA_PIN = 20;
const int SCL_PIN = 21;

// Force sensor pins, analog pins
const int FORCE_1_PIN = 14; // A0
const int FORCE_2_PIN = 15; // A1
const int FORCE_3_PIN = 16; // A2
const int FORCE_4_PIN = 17; // A3
// ---------------------------------------------------------------

/* Variables declaration */ 
// ---------------------------------------------------------------
 // timer for MPU6050
long timer = millis();

// timer for PMW3389
long prevTimeSinceStart = millis(); 

// Sensor variables
float force_1 = 0;
float force_2 = 0;
float force_3 = 0;
float force_4 = 0;
float x1=0;
float y1=0;  
float x2=0; 
float y2=0; 
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
// ---------------------------------------------------------------

void setup() {
  Serial.begin(SERIAL_BAUD_RATE); // Initialize Serial
  /* MPU portion */
  // -------------------------------------------------------------
  Wire.begin();
  mpu6050_1.begin();
  mpu6050_1.calcGyroOffsets(true);
  mpu6050_2.begin();
  mpu6050_2.calcGyroOffsets(true);
  // -------------------------------------------------------------

    while (!Serial); // Wait for serial to initialize.

  /* PMW3389 portion */
  // -------------------------------------------------------------
  Initialize SPI
  SPI.begin();                  // Initialize SPI bus
  SPI.setDataMode(SPI_MODE0);   // CPOL = 0, CPHA = 0
  SPI.setBitOrder(MSBFIRST);    // MSB first
  SPI.setClockDivider(SPI_CLOCK_DIV16); // Adjust the clock divider as needed

  // Initialize the SS pins
  pinMode(SS_PIN_1, OUTPUT);    // Set SS pins as outputs
  pinMode(SS_PIN_2, OUTPUT);    // Set SS pins as outputs

  digitalWrite(SS_PIN_1, HIGH); // Set SS pins high initially
  digitalWrite(SS_PIN_2, HIGH); // Set SS pins high initially

  sensor1.begin(SS_PIN_1, 16000); // to set CPI (Count per Inch), pass it as the
  sensor2.begin(SS_PIN_2, 16000); // second argument to the begin function
  // -------------------------------------------------------------

}

void loop() {
  unsigned long currentMillis = millis(); // current time for MPU6050 in milliseconds
  mpu6050_1.update(); // update MPU6050
  mpu6050_2.update(); // update MPU6050

  /* Read data from sensors every 100 milliseconds */
  // -------------------------------------------------------------
  if (currentMillis - timer > 100) {
    unsigned long timeSinceStart = millis();

    // MPU gets data from updates
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

    // Left MPU velocity and acceleration
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

    // Right MPU velocity and acceleration
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

    // Get data from PMW3389 sensors via readburst
    PMW3389_DATA data1 = sensor2.readBurst();
    PMW3389_DATA data2 = sensor1.readBurst();

    if (data1.isMotion || data1.isOnSurface) {
      L_PMW_X = ((data1.dx)) + L_PMW_X; // converts to 1mm since 16,000 CPI
      L_PMW_Y = ((data1.dy)) + L_PMW_Y;
    }
    if (data2.isMotion || data2.isOnSurface) {
      R_PMW_X = ((data2.dx)) + R_PMW_X; // converts to 1mm since 16,000 CPI
      R_PMW_Y = ((data2.dy)) + R_PMW_Y;
    }

    // Left PMW velocities
    if (prev_L_PMW_X != 0) {
      L_PMW_X_vel = (L_PMW_X - prev_L_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_L_PMW_Y != 0) {
      L_PMW_Y_vel = (L_PMW_Y - prev_L_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    // Left PMW accelerations
    if (prev_L_PMW_X_vel != 0) {
      L_PMW_X_acc = (L_PMW_X_vel - prev_L_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_L_PMW_Y_vel != 0) {
      L_PMW_Y_acc = (L_PMW_Y_vel - prev_L_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }

    // Right PMW velocities
    if (prev_R_PMW_X != 0) {
      R_PMW_X_vel = (R_PMW_X - prev_R_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_R_PMW_Y != 0) {
      R_PMW_Y_vel = (R_PMW_Y - prev_R_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    /* Right PMW accelerations */
    // -------------------------------------------------------------
    if (prev_R_PMW_X_vel != 0) {
      R_PMW_X_acc = (R_PMW_X_vel - prev_R_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_R_PMW_Y_vel != 0) {
      R_PMW_Y_acc = (R_PMW_Y_vel - prev_R_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    // -------------------------------------------------------------

    /* If not in motion/on surface, reset acceleration value back to zero */
    // -------------------------------------------------------------
    if (!(data1.isMotion || data1.isOnSurface)) {
      L_PMW_X_acc = 0;
      L_PMW_Y_acc = 0;
      L_PMW_Y_vel = 0;
      L_PMW_X_vel = 0;
      L_PMW_Y = 0;
      L_PMW_X = 0;
    }
    if (!(data2.isMotion || data2.isOnSurface)) {
      R_PMW_X_acc = 0;
      R_PMW_Y_acc = 0;
      R_PMW_X_vel = 0;
      R_PMW_Y_vel = 0;
      R_PMW_Y = 0;
      R_PMW_X = 0;
    }
    // -------------------------------------------------------------

    /* Force sensors read at Pin A0, A1, A2, A3 */
    // -------------------------------------------------------------
    force_1 = (analogRead(FORCE_1_PIN) - 136) * 0.011; // 136 offset to try to "zero" the value
    force_2 = (analogRead(FORCE_2_PIN) - 136) * 0.011; // 136 offset to try to "zero" the value
    force_3 = (analogRead(FORCE_3_PIN) - 136) * 0.011; // 136 offset to try to "zero" the value
    force_4 = (analogRead(FORCE_4_PIN) - 136) * 0.011; // 136 offset to try to "zero" the value
    // -------------------------------------------------------------

    /* Trial and error */
    // -------------------------------------------------------------
    float xL = mpu6050_1.getAccX();
    float yL = mpu6050_1.getAccY();
    float zL = mpu6050_1.getAccZ();

    float xR = mpu6050_2.getAccX();
    float yR = mpu6050_2.getAccY();
    float zR = mpu6050_2.getAccZ();
    // -------------------------------------------------------------

    /* Print sensor data to Serial */
    // -------------------------------------------------------------
    Serial.print(String(force) + "|" + String(L_pitchAcc / 1000) + "|" + String(L_yawAcc / 1000) + "|" + String(R_pitchAcc / 1000) + "|" + String(R_yawAcc / 1000) + "|" + String(L_PMW_Y_acc / 10) +
                 "|" + String(L_PMW_X_acc / 10) + "|" + String(R_PMW_Y_acc / 10) + "|" + String(R_PMW_X_acc / 10) + "|" + String(L_pitchVel) + "|" + String(L_yawVel) + "|" + String(R_pitchVel) +
                 "|" + String(R_yawVel) + "|" + String(L_PMW_Y_vel) + "|" + String(L_PMW_X_vel) + "|" + String(R_PMW_Y_vel) + "|" + String(R_PMW_X_vel) + "|" + String(L_pitch) +
                 "|" + String(L_yaw) + "|" + String(R_pitch) + "|" + String(R_yaw) + "|" + String(L_PMW_Y) + "|" + String(L_PMW_X) + "|" + String(R_PMW_Y) + "|" + String(R_PMW_X) +
                 "|" + String(xR) + "|" + String(yR) + "|" + String(zR) + "|" + String(xL) + "|" + String(yL) + "|" + String(zL) + "|" + String(data1.isMotion && data1.isOnSurface) +
                 "|" + String(data2.isMotion && data2.isOnSurface) + '\n');
    // -------------------------------------------------------------

    /* Save previous values */
    // -------------------------------------------------------------
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
    // -------------------------------------------------------------
  }
}
