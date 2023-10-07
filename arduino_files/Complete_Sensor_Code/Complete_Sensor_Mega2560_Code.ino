#include <MPU6050_2.h>      // Include the library for MPU6050 sensor 2
#include <MPU6050_1.h>      // Include the library for MPU6050 sensor 1
#include <Wire.h>           // Include the Wire library for I2C communication
#include <PMW3389.h>        // Include the library for PMW3389 sensor
#include <SPI.h>            // Include the SPI library for SPI communication

// Initializing MPU6050 sensors from libraries
MPU6050 mpu6050_1(Wire);     // Create an instance of MPU6050 for sensor 1
MPU60502 mpu6050_2(Wire);    // Create an instance of MPU6050 for sensor 2 (Addressed at 0x69)

// Initialize timer variables
long timer = millis();               // Store the current time in milliseconds
long prevTimeSinceStart = millis();   // Store the previous time since start

// Initializing PMW3389 sensors from the library
PMW3389 sensor1;    // Create an instance of PMW3389 for the right sensor
PMW3389 sensor2;    // Create an instance of PMW3389 for the left sensor

// Variables to store sensor data
float x1 = 0;
float y1 = 0;
float x2 = 0;
float y2 = 0;
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
  Serial.begin(38400);  // Initialize the serial communication
  
  // MPU6050 setup
  Wire.begin();                     // Initialize I2C communication
  mpu6050_1.begin();                // Initialize MPU6050 sensor 1
  mpu6050_1.calcGyroOffsets(true);  // Calculate gyro offsets for sensor 1
  mpu6050_2.begin();                // Initialize MPU6050 sensor 2
  mpu6050_2.calcGyroOffsets(true);  // Calculate gyro offsets for sensor 2
  
  while (!Serial);  // Wait until serial communication is established
  
  // PMW3389 setup
  sensor1.begin(53, 16000);  // Initialize PMW3389 sensor 1 with SS pin 53 and 16000 CPI
  sensor2.begin(40, 16000);  // Initialize PMW3389 sensor 2 with SS pin 40 and 16000 CPI
}

void loop() {
  unsigned long currentMillis = millis();  // Get the current time in milliseconds
  mpu6050_1.update();  // Update sensor 1 data
  mpu6050_2.update();  // Update sensor 2 data
  
  if (currentMillis - timer > 100) {
    // Code inside this block runs every 100 milliseconds
    
    unsigned long timeSinceStart = millis();  // Calculate time since program start
    
    // Get angles (pitch and yaw) from MPU sensors for both left and right sensors
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
    
    // Calculate velocities and accelerations for both left and right sensors
    if (prev_L_yaw != 0) {
        L_yawVel = (L_yaw - prev_L_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prev_L_pitch != 0) {
        L_pitchVel = (L_pitch - prev_L_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prev_L_yawVel != 0) {
        L_yawAcc = (L_yawVel - prev_L_yawVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_L_pitchVel != 0) {
        L_pitchAcc = (L_pitchVel - prev_L_pitchVel) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s^2
    }
    if (prev_R_yaw != 0) {
        R_yawVel = (R_yaw - prev_R_yaw) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
    if (prev_R_pitch != 0) {
        R_pitchVel = (R_pitch - prev_R_pitch) * 1000.00 / (timeSinceStart - prevTimeSinceStart); // deg/s
    }
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
      L_PMW_Y = ((data1.dy)) + L_PMW_Y; // converts to 1mm since 16,000 CPI
    }
    if (data2.isMotion || data2.isOnSurface) {
      R_PMW_X = ((data2.dx)) + R_PMW_X; // converts to 1mm since 16,000 CPI
      R_PMW_Y = ((data2.dy)) + R_PMW_Y; // converts to 1mm since 16,000 CPI
    }
    
    // Calculate left PMW velocities
    if (prev_L_PMW_X != 0) {
      L_PMW_X_vel = (L_PMW_X - prev_L_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_L_PMW_Y != 0) {
      L_PMW_Y_vel = (L_PMW_Y - prev_L_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    
    // Calculate left PMW accelerations
    if (prev_L_PMW_X_vel != 0) {
      L_PMW_X_acc = (L_PMW_X_vel - prev_L_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_L_PMW_Y_vel != 0) {
      L_PMW_Y_acc = (L_PMW_Y_vel - prev_L_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    
    // Calculate right PMW velocities
    if (prev_R_PMW_X != 0) {
      R_PMW_X_vel = (R_PMW_X - prev_R_PMW_X) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    if (prev_R_PMW_Y != 0) {
      R_PMW_Y_vel = (R_PMW_Y - prev_R_PMW_Y) / (timeSinceStart - prevTimeSinceStart); // units/s
    }
    
    // Calculate right PMW accelerations
    if (prev_R_PMW_X_vel != 0) {
      R_PMW_X_acc = (R_PMW_X_vel - prev_R_PMW_X_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    if (prev_R_PMW_Y_vel != 0) {
      R_PMW_Y_acc = (R_PMW_Y_vel - prev_R_PMW_Y_vel) / (timeSinceStart - prevTimeSinceStart); // units/s^2
    }
    
    // If not in motion/on surface, reset acceleration value back to zero
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
    
    // Read force sensor connected to Pin A0
    force = (analogRead(A0) - 136) * 0.011; // Offset adjustment
    
    // Get accelerometer data from MPU sensors
    float xL = mpu6050_1.getAccX();
    float yL = mpu6050_1.getAccY();
    float zL = mpu6050_1.getAccZ();
    
    float xR = mpu6050_2.getAccX();
    float yR = mpu6050_2.getAccY();
    float zR = mpu6050_2.getAccZ();
    
    // Division by 1000.00 to convert pitch and yaw to smaller digit value
    Serial.print(String(force) + "|" + String(L_pitchAcc/1000) + "|" + String(L_yawAcc/1000) + "|" + String(R_pitchAcc/1000) + "|" + String(R_yawAcc/1000) + "|" + String(L_PMW_Y_acc/10) +
    "|" + String(L_PMW_X_acc/10) + "|" + String(R_PMW_Y_acc/10) + "|" + String(R_PMW_X_acc/10) + "|" + String(L_pitchVel) + "|" + String(L_yawVel) + "|" + String(R_pitchVel) +
    "|" + String(R_yawVel) + "|" + String(L_PMW_Y_vel) + "|" + String(L_PMW_X_vel) + "|" + String(R_PMW_Y_vel) + "|" + String(R_PMW_X_vel) + "|" + String(L_pitch) +
    "|" + String(L_yaw) + "|" + String(R_pitch) + "|" + String(R_yaw) + "|" + String(L_PMW_Y) + "|" + String(L_PMW_X) + "|" + String(R_PMW_Y) + "|" + String(R_PMW_X) +
    "|" + String(xR) + "|" + String(yR) + "|" + String(zR) + "|" + String(xL) + "|" + String(yL) + "|" + String(zL) + "|" + String(data1.isMotion && data1.isOnSurface) +
    "|" + String(data2.isMotion && data2.isOnSurface) + '\n');
    
    // Save previous values for the next iteration
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
