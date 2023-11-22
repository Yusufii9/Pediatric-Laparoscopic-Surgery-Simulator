/*********************************************************************************************
Author: Atallah Madi
Date: October 21th, 2023
Last edited: November 10th, 2023
Purpose: This code is used to read data from MPU6050, PMW3389, HX711 ADC and Load cells.
         The data is then sent to the computer via Serial. The data is then read by Python Application
         This code is for the Arduino Nano.
*********************************************************************************************/

// Libraries
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#include <MPU6050_1.h> // Include the library for MPU6050 sensor
#include <MPU6050_2.h> // Include the library for MPU6050 sensor
#include <PMW3389.h>   // Include the library for PMW3389 sensor
#include <HX711.h>     // Include the HX711 library for force sensors
#include <Wire.h>      // Include the Wire library for I2C communication
#include <SPI.h>       // Include the SPI library for SPI communication
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

/* Constants declaration, and pins definition */
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// I2C pins, digital pins
#define SCL_PIN 19 // A5
#define SDA_PIN 18 // A4

// SPI pins, digital pins
#define SCK_PIN 13  // D13
#define MISO_PIN 12 // D12
#define MOSI_PIN 11 // D11
#define SS_PIN_1 8  // D8
#define SS_PIN_2 7  // D7

// Force sensor pins, digital pins
#define FORCE_4_PIN 6   // D6
#define FORCE_3_PIN 5   // D5
#define FORCE_2_PIN 4   // D4
#define FORCE_1_PIN 3   // D3
#define FORCE_CLK_PIN 2 // D2

const int SERIAL_BAUD_RATE = 31250;

const float SCALE_FACTOR = 830;              // this value is obtained by calibrating the scale with known weights
const float SCALE_CONV_FACTOR = 0.009806652; // Newtons = Grams * 0.009806652
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

/* Initializing Libraries */
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;
PMW3389 sensor1;          // LEFT HAND
PMW3389 sensor2;          // RIGHT HAND
MPU6050 mpu6050_1(Wire);  // LEFT HAND
MPU60502 mpu6050_2(Wire); // RIGHT HAND
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

/* Variables declaration */
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
long timer = millis();              // timer for MPU6050
long prevTimeSinceStart = millis(); // timer for PMW3389

// Sensor variables
float xL = 0;
float yL = 0;
float zL = 0;

float xR = 0;
float yR = 0;
float zR = 0;

float force = 0;
int weight1 = 0;
int weight2 = 0;
int weight3 = 0;
int weight4 = 0;
bool allScalesNonZero;

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
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

/* Intializing Sensors */
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
void setup()
{
  Wire.begin();
  Serial.begin(SERIAL_BAUD_RATE);

  // MPU portion
  mpu6050_1.begin();
  mpu6050_1.calcGyroOffsets(true);
  mpu6050_2.begin();
  mpu6050_2.calcGyroOffsets(true);

  while (!Serial)
    ; // Wait for serial to initialize.

  sensor1.begin(SS_PIN_1, 16000); // to set CPI (Count per Inch), pass it as the
  sensor2.begin(SS_PIN_2, 16000); // second argument to the begin function

  // Force sensor portion
  scale1.begin(FORCE_1_PIN, FORCE_CLK_PIN);
  scale2.begin(FORCE_2_PIN, FORCE_CLK_PIN);
  scale3.begin(FORCE_3_PIN, FORCE_CLK_PIN);
  scale4.begin(FORCE_4_PIN, FORCE_CLK_PIN);

  scale1.set_scale(SCALE_FACTOR); // RAW_Reading/SCALE_FACTOR = grams
  scale2.set_scale(SCALE_FACTOR);
  scale3.set_scale(SCALE_FACTOR);
  scale4.set_scale(SCALE_FACTOR);

  scale1.tare(); // reset the scale to 0
  scale2.tare(); // sets current weight as to offset
  scale3.tare(); // RAW_Reading - OFFSET = 0
  scale4.tare();
}

/* Main Program */
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
void loop()
{
  unsigned long currentMillis = millis(); // current time for MPU6050 in milliseconds

  mpu6050_1.update(); // update MPU6050
  mpu6050_2.update(); // update MPU6050

  // Read data from sensors every 100 milliseconds
  if (currentMillis - timer > 100)
  {
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
    if (prev_L_yaw != 0)
    {
      L_yawVel = (L_yaw - prev_L_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prev_L_pitch != 0)
    {
      L_pitchVel = (L_pitch - prev_L_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }

    // Accelerations
    if (prev_L_yawVel != 0)
    {
      L_yawAcc = (L_yawVel - prev_L_yawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_L_pitchVel != 0)
    {
      L_pitchAcc = (L_pitchVel - prev_L_pitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }

    // Right MPU velocity and acceleration
    if (prev_R_yaw != 0)
    {
      R_yawVel = (R_yaw - prev_R_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prev_R_pitch != 0)
    {
      R_pitchVel = (R_pitch - prev_R_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }

    // Accelerations
    if (prev_R_yawVel != 0)
    {
      R_yawAcc = (R_yawVel - prev_R_yawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_R_pitchVel != 0)
    {
      R_pitchAcc = (R_pitchVel - prev_R_pitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }

    // Get data from PMW3389 sensors via readburst
    PMW3389_DATA data1 = sensor2.readBurst();
    PMW3389_DATA data2 = sensor1.readBurst();

    if (data1.isMotion || data1.isOnSurface)
    {
      L_PMW_X = ((data1.dx)) + L_PMW_X; // converts to 1mm since 16,000 CPI 16000=32767 in two's compliment so 32767=16,000=inch=25.4mm therefore 1290=1mmm.
      L_PMW_Y = ((data1.dy)) + L_PMW_Y; // Can measure 10cm on ruler and use that bit value to convert
    }
    if (data2.isMotion || data2.isOnSurface)
    {
      R_PMW_X = ((data2.dx)) + R_PMW_X; // converts to 1mm since 16,000 CPI 16000=32767 in two's compliment so 32767=16,000=inch=25.4mm therefore 1290=1mmm.
      R_PMW_Y = ((data2.dy)) + R_PMW_Y;
    }

    // Left PMW velocities
    if (prev_L_PMW_X != 0)
    {
      L_PMW_X_vel = (L_PMW_X - prev_L_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_L_PMW_Y != 0)
    {
      L_PMW_Y_vel = (L_PMW_Y - prev_L_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    // Left PMW accelerations
    if (prev_L_PMW_X_vel != 0)
    {
      L_PMW_X_acc = (L_PMW_X_vel - prev_L_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_L_PMW_Y_vel != 0)
    {
      L_PMW_Y_acc = (L_PMW_Y_vel - prev_L_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }

    // Right PMW velocities
    if (prev_R_PMW_X != 0)
    {
      R_PMW_X_vel = (R_PMW_X - prev_R_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_R_PMW_Y != 0)
    {
      R_PMW_Y_vel = (R_PMW_Y - prev_R_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }

    // Right PMW accelerations
    if (prev_R_PMW_X_vel != 0)
    {
      R_PMW_X_acc = (R_PMW_X_vel - prev_R_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_R_PMW_Y_vel != 0)
    {
      R_PMW_Y_acc = (R_PMW_Y_vel - prev_R_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }

    // If not in motion/on surface, reset acceleration value back to zero
    if (!(data1.isMotion || data1.isOnSurface))
    {
      L_PMW_X_acc = 0;
      L_PMW_Y_acc = 0;
      L_PMW_X_vel = 0;
      L_PMW_Y_vel = 0;
      L_PMW_X = 0;
      L_PMW_Y = 0;
    }
    if (!(data2.isMotion || data2.isOnSurface))
    {
      R_PMW_X_acc = 0;
      R_PMW_Y_acc = 0;
      R_PMW_X_vel = 0;
      R_PMW_Y_vel = 0;
      R_PMW_X = 0;
      R_PMW_Y = 0;
    }

    /* Force sensors readings */
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Force sensors readings (grams)
    weight1 = scale1.get_units();
    weight2 = scale2.get_units();
    weight3 = scale3.get_units();
    weight4 = scale4.get_units();
    
    // Check if all scales are non-zero
    allScalesNonZero = (weight1 != 0) && (weight2 != 0) && (weight3 != 0) && (weight4 != 0);

    // Stability check: If any one scale is zero while others are not, ignore the readings
    if (allScalesNonZero) {
      // Calculate force in Newtons
      force = ((weight1 + weight2 + weight3 + weight4) * SCALE_CONV_FACTOR);
    } else { force = 0;}
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    /*
    Print sensor data from Serial into .txt file
    force = if -ve, then it is pushing force, if +ve, then it is pull force
    L_PMW_Y / R_PMW_Y = surge
    L_PMW_X / R_PMW_X = roll
    L_pitch / R_pitch = pitch
    L_yaw / R_yaw = yaw
    */
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Serial.println(String(force) + "|" +
                   String(L_pitchAcc / 1000) + "|" + String(L_yawAcc / 1000) + "|" +
                   String(R_pitchAcc / 1000) + "|" + String(R_yawAcc / 1000) + "|" +
                   String(L_PMW_Y_acc) + "|" + String(L_PMW_X_acc) + "|" +
                   String(R_PMW_Y_acc) + "|" + String(R_PMW_X_acc) + "|" +
                   String(L_pitchVel) + "|" + String(L_yawVel) + "|" +
                   String(R_pitchVel) + "|" + String(R_yawVel) + "|" +
                   String(L_PMW_Y_vel) + "|" + String(L_PMW_X_vel) + "|" +
                   String(R_PMW_Y_vel) + "|" + String(R_PMW_X_vel) + "|" +
                   String(L_pitch) + "|" + String(L_yaw) + "|" +
                   String(R_pitch) + "|" + String(R_yaw) + "|" +
                   String(L_PMW_Y) + "|" + String(L_PMW_X) + "|" +
                   String(R_PMW_Y) + "|" + String(R_PMW_X) + "|" +
                   String(xR) + "|" + String(yR) + "|" + String(zR) + "|" +
                   String(xL) + "|" + String(yL) + "|" + String(zL) + "|" +
                   String(data1.isMotion && data1.isOnSurface) + "|" +
                   String(data2.isMotion && data2.isOnSurface));

    /* Save previous values */
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
  }
}
