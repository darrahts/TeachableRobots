

#include <Servo.h>

Servo pan;
Servo tilt;

//right motor (facing with the robot)
#define MTR_A_EN 6
#define MTR_A_A 7
#define MTR_A_B 8

//left motor
#define MTR_B_EN 11
#define MTR_B_A 9
#define MTR_B_B 10

#define TRIG 6
#define ECHO 12

#define LEFT_IR A2
#define RIGHT_IR A3
#define MIDDLE_IR A4

#define PAN_SERVO A0
#define TILT_SERVO A1

#define OFFSET 25 // change this to match your motor performance
#define SPEED 105

#define PAN_LEFT_MAX 170
#define PAN_CENTER 105
#define PAN_RIGHT_MAX 40

#define TILT_UP_MAX 30
#define TILT_CENTER 120
#define TILT_DOWN_MAX 150


byte state = 0;


int motorPins[] = {6,7,8,11,9,10};


void motorsOff()
{
    for(int i = 0; i < 6; i++)
  {
    digitalWrite(motorPins[i], LOW);
  }
  state = 0;
}

void forward()
{
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  state = 1;
}

void backward()
{
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  state = 2;
}

void left(int duration)
{
  analogWrite(MTR_A_EN, SPEED + 20);
  analogWrite(MTR_B_EN, SPEED + 20 - OFFSET);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  delay(duration); //195 is for right angle turns while in motion
  motorsOff();
  state = 3;
}

void right(int duration)
{
  analogWrite(MTR_A_EN, SPEED + 20);
  analogWrite(MTR_B_EN, SPEED + 20 - OFFSET);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  delay(duration); //195 is for right angle turns while in motion
  motorsOff();
  state = 4;
}

int checkDistance()
{
  long duration;
  int distance;
  digitalWrite(TRIG, LOW);
  delayMicroseconds(5);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = duration / 29 / 2;
  if(distance < 20 && distance >10)
  {
    if(state == 1)
    {
      backward();
      delay(500);
      motorsOff();
    }
    else if(state == 3)
    {
      backward();
      delay(100);
      motorsOff();
      right(100);
      motorsOff();
    }
      else if(state == 4)
    {
      backward();
      delay(100);
      motorsOff();
      left(100);
      motorsOff();
    }
  }
  return distance;
}

void setup() 
{
  Serial.begin(9600);
  for(int i = 0; i < 6; i++)
  {
    pinMode(motorPins[i], OUTPUT);
  }

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  pan.attach(PAN_SERVO);
  tilt.attach(TILT_SERVO);

  
  motorsOff();
  pan.write(PAN_CENTER);
  tilt.write(TILT_CENTER); 

  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
}

long timer = 0; //dont use delay 

void loop() 
{
  Serial.print(analogRead(A3));
  Serial.print("   ");
 // Serial.print(analogRead(A3));
  Serial.print("   ");
 // Serial.print(analogRead(A4));
  Serial.print("   ");
  Serial.println();
  delay(500);

}
