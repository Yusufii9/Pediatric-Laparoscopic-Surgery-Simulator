/*********************************************************************************************
Author: Atallah Madi
Date: November 10th, 2023
Last edited: November 10th, 2023
Purpose: This code is used to calibrate the scales. It will print the output of the scales
         and allow the user to change the scale factor while the code is running. This code
         is used to find the scale factor that will be used in the final code.
*********************************************************************************************/

// Libraries
#include "HX711.h"

// Pin Definitions
#define FORCE_4_PIN 6   // D6
#define FORCE_3_PIN 5   // D5
#define FORCE_2_PIN 4   // D4
#define FORCE_1_PIN 3   // D3
#define FORCE_CLK_PIN 2 // D2

// Global variables and defines
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

float increment = 10; // adjust for more percision
float SCALE_FACTOR = 830; // final scale factor that was found
float sum = 0;

// Setup functions
void setup()
{
    Serial.begin(31250);
    Serial.println("Press + or a to increase calibration factor");
    Serial.println("Press - or z to decrease calibration factor");

    // Initialize pins for scales
    scale1.begin(FORCE_1_PIN, FORCE_CLK_PIN);
    scale2.begin(FORCE_2_PIN, FORCE_CLK_PIN);
    scale3.begin(FORCE_3_PIN, FORCE_CLK_PIN);
    scale4.begin(FORCE_4_PIN, FORCE_CLK_PIN);

    // Set scale to defualt = 1
    scale1.set_scale();
    scale2.set_scale();
    scale3.set_scale();
    scale4.set_scale();

    // Tare scale to 0
    scale1.tare();
    scale2.tare();
    scale3.tare();
    scale4.tare();
}

void loop()
{
    // Set scale to 830 
    scale1.set_scale(SCALE_FACTOR);
    scale2.set_scale(SCALE_FACTOR);
    scale3.set_scale(SCALE_FACTOR);
    scale4.set_scale(SCALE_FACTOR);

    // Read the value of all scales
    sum = (int)(scale1.get_units() + scale2.get_units() + scale3.get_units() + scale4.get_units());

    // Print the value of all scales
    Serial.println("SCLAE OUTPUT: " + String(sun) + " grams" + " SCALE FACTOR: " + String(SCALE_FACTOR));

    // Change scale factor while running << change by using + or - keys>>
    if (Serial.available())
    {
        char temp = Serial.read();
        if (temp == '+' || temp == 'a')
            SCALE_FACTOR += increment;
        else if (temp == '-' || temp == 'z')
            SCALE_FACTOR -= increment;
    }
}
