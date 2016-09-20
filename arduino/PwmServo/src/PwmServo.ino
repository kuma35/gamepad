// PwmServo.ino
// -*- coding:utf-8 -*-

#include <EEPROM.h>
#include <HardwareSerial.h>
#include <Servo.h>

#define DEBUG

#define SERVO_VOLUME 2
#define SERIAL_SPEED 115200

#define EEPROM_BASE 0
#define EEPROM_I2C_ADDR	0	// NO USE
#define EEPROM_SERVO_0 1 
#define EEPROM_MIN_L_OFFSET 1	// little endigan 0x12,0x34 to 0x1234
#define EEPROM_MIN_H_OFFSET 2
#define EEPROM_MAX_L_OFFSET 3
#define EEPROM_MAX_H_OFFSET 4
#define EEPROM_SERVO_1 6
//#define EEPROM_MIN_L_OFFSET 1
//#define EEPROM_MIN_H_OFFSET 2
//#define EEPROM_MAX_L_OFFSET 3
//#define EEPROM_MAX_H_OFFSET 4
//0 - 10 USEING

// return code
// first byte is:
// 'I' Info
// 'O' Ok
// 'N' Ng
// second byte is ignore. normaly ':'
// follow bytes is msg.

const char *Comma = ",";

Servo Sv[SERVO_VOLUME];
struct servo_info_t {
  int pin;
  int min;
  int max;
} Servo_info[SERVO_VOLUME];

void eat(void) {
  while (Serial.available() > 0) {
    delay(10);
    (void)Serial.read();
  }
}

int get_servo_pin(int id) {
  int pin;
  switch (id) {
  case 0:
    pin = EEPROM.read(EEPROM_SERVO_0);
    break;
  case 1:
    pin = EEPROM.read(EEPROM_SERVO_1);
    break;
  }
  return pin;
}

int get_servo_min(int id) {
  int min;
  switch (id) {
  case 0:
    min = EEPROM.read(EEPROM_SERVO_0+EEPROM_MIN_H_OFFSET) << 8 |
      EEPROM.read(EEPROM_SERVO_0+EEPROM_MIN_L_OFFSET);
    break;
  case 1:
    min = EEPROM.read(EEPROM_SERVO_1+EEPROM_MIN_H_OFFSET) << 8 |
      EEPROM.read(EEPROM_SERVO_1+EEPROM_MIN_L_OFFSET);
    break;
  }
  return min;
}

int get_servo_max(int id) {
  int max;
  switch (id) {
  case 0:
    max = EEPROM.read(EEPROM_SERVO_0+EEPROM_MAX_H_OFFSET) << 8 |
      EEPROM.read(EEPROM_SERVO_0+EEPROM_MAX_L_OFFSET);
    break;
  case 1:
    max = EEPROM.read(EEPROM_SERVO_1+EEPROM_MAX_H_OFFSET) << 8 |
      EEPROM.read(EEPROM_SERVO_1+EEPROM_MAX_L_OFFSET);
    break;
  }
  return max;
}

void cmd_attach(int id) {
  if (Sv[id].attached()) {
    Sv[id].detach();
    Sv[id].attach(Servo_info[id].pin);
  } else {
    Sv[id].attach(Servo_info[id].pin);
  }
  Serial.print("O:A");
}

void cmd_detach(int id) {
  if (Sv[id].attached()) {
    Sv[id].detach();
  }
  Serial.print("O:D");
}

void cmd_info(void) {
  Serial.println("O:I");
  Serial.println(F("Sv,pin,min,max"));
  for (int i = 0;i < SERVO_VOLUME; i++ ) {
    Serial.print(i);
    Serial.print(Comma);
    Serial.print(Servo_info[i].pin);
    Serial.print(Comma);
    Serial.print(Servo_info[i].min);
    Serial.print(Comma);
    Serial.println(Servo_info[i].max);
  }
}

void cmd_pulse(int id, int pulse) {
  if (Sv[id].attached()) {
    if (pulse < Servo_info[id].min) {
      pulse = Servo_info[id].min;
    } else if (Servo_info[id].max < pulse) {
      pulse = Servo_info[id].max;
    }
    Sv[id].writeMicroseconds(pulse);
  }
  Serial.print("O:P");
}

void cmd_write(int addr, int v) {
  EEPROM.write(addr, v);
  Serial.print("O:W");
}

void cmd_read(int addr) {
  int v;
  v = EEPROM.read(addr);
  Serial.print("O:R");
  Serial.print(v, HEX);
}

void cmd_signature(void) {
  Serial.print(__DATE__ " " __TIME__);
}

void setup()
{
  for (int i = 0; i < SERVO_VOLUME; i++) {
    Servo_info[i].pin = get_servo_pin(i);
    Servo_info[i].min = get_servo_min(i);
    Servo_info[i].max = get_servo_max(i);
  }
  Serial.begin(SERIAL_SPEED);
  Serial.print("O:S " __DATE__ " " __TIME__);
}

void loop()
{
  int c;
  int id;
  int pulse_l;
  int pulse_h;
  int pulse;
  int addr;
  int v;
  if (Serial.available() > 0) {
    delay(100);
    c = Serial.read();
    switch (c) {
    case 'A':	// attach
      id = Serial.read();
      if (id == -1) {
	eat();
	return;
      }
      cmd_attach(id);
      break;
    case 'D': // detach
      if ((id = Serial.read()) == -1) {
	eat();
	return;
      }
      cmd_detach(id);
      break;
    case 'I': // info
      cmd_info();
      break;
    case 'P': // pulse
      id = Serial.read();
      if (id == -1) {
	eat();
	return;
      }
      pulse_l = Serial.read();
      if (pulse_l == -1) {
	eat();
	return;
      }
      pulse_h = Serial.read();
      if (pulse_h == -1) {
	eat();
	return;
      }
      pulse = pulse_h << 8 | pulse_l;
      cmd_pulse(id, pulse);
      break;
    case 'R': // eeprom-read
      addr = Serial.read();
      if (addr == -1) {
	eat();
	return;
      }
      cmd_read(addr);
      break;
    case 'S':
      cmd_signature();
      break;
    case 'W': // eeprom-write
      addr = Serial.read();
      if (addr == -1) {
	eat();
	return;
      }
      v = Serial.read();
      if (v == -1) {
	eat();
	return;
      }
      cmd_write(addr, v);
      break;
    default:
      eat();
      break;
    }
  } else {
    delay(100);
  }
}
