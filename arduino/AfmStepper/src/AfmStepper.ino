/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->	http://www.adafruit.com/products/1438
*/


#include <Wire.h>
#include <Adafruit_MotorShield.h>
//#include "utility/Adafruit_PWMServoDriver.h"

#define SERIAL_SPEED 9600

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #1 (M1 and M2)
// ST-42BYH1004
// 400 steps per revolution (0.9 degree +- 5%)
Adafruit_StepperMotor *Stepper = AFMS.getStepper(400, 1);

void eat(void) {
  while (Serial.available() > 0) {
    delay(10);
    (void)Serial.read();
  }
}

void cmd_signature(void) {
  Serial.print(__DATE__ " " __TIME__);
}

void cmd_forward(int count) {
  Stepper->step(count, FORWARD, MICROSTEP);
  Serial.print("O:F");
}

void cmd_backward(int count) {
  Stepper->step(count, BACKWARD, MICROSTEP);
  Serial.print("O:B");
}

void setup() {
  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz
  Stepper->setSpeed(10);  // 10 rpm   

  Serial.begin(SERIAL_SPEED);
  Serial.print("O:S " __DATE__ " " __TIME__);
}

void loop() {
  int c;
  int count;
  int pulse_l;
  int pulse_h;
  int pulse;
  int addr;
  int v;
  if (Serial.available() > 0) {
    delay(100);
    c = Serial.read();
    switch (c) {
    case 'F':	// forward
      count = Serial.read();	// count
      if (count == -1) {
	eat();
	return;
      }
      cmd_forward(count);
      break;
    case 'B': // backward
      if (count == -1) {
	eat();
	return;
      }
      cmd_backward(count);
      break;
    case 'S':
      cmd_signature();
      break;
    default:
      eat();
      break;
    }
  } else {
    delay(100);
  }
}
