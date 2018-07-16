
//#include <Servo.h>
#include <EEPROM.h>
/********************************************************************************************************
 *                                             PIN DEFINITIONS                                          *                                                  
 ********************************************************************************************************/

//right motor (facing with the robot)
#define MTR_A_EN 6
#define MTR_A_A 8
#define MTR_A_B 7

//left motor
#define MTR_B_EN 11
#define MTR_B_A 9
#define MTR_B_B 10

//line sensors
#define LEFT_IR A3
#define MIDDLE_IR A4
#define RIGHT_IR A2

#define LEFT_LED 3
#define MIDDLE_LED 4
#define RIGHT_LED 5

//voltage sensor
#define VOLTAGE_SR A1

//used to loop through motor pins to turn them off
int motorPins[] = {6,7,8,11,9,10};
/********************************************************************************************************
 *                                             CONSTANT PARAMETERS                                      *                                                  
 ********************************************************************************************************/
//min and max velocity vals (input)
const int minV = 0;
const int maxV = 20;

//min and max motor speed vals
const int minS = 90;
const int maxS = 150;

//scaling for left/right motor differences
const float scale = .75f; 
/********************************************************************************************************
 *                                             GLOBAL VARIABLES                                         *                                                  
 ********************************************************************************************************/
//current speed in range [minV, maxV]
int curSpd = 0;

//current motor val in range [minS, maxS]
int curVal = 0; 

//current direction (-1/stop, 0/forward, 1/backward, 2/turningleft, 3/turningright)
int curDir = -1; 

/********************************************************************************************************
 *                                                  FUNCTIONS                                           *
 ********************************************************************************************************/


/*                                                   MOTORS                                       *                                                  
 ********************************************************************************************************/


int DegToDelay(bool dime, int deg)
{
    if(dime)
    {
       return int(abs(deg)*2.35 + 40);
    }
}


/*                                  STOP                
 *                         turns off the motors
 */
void Stop()
{
    for(int i = curSpd; i >= 0; i--)
    {
        Ramp(i, -1, -1);
    }

    for(int i = 0; i < 6; i++)
    {
      digitalWrite(motorPins[i], LOW);
    }
    curSpd = 0;
    curDir = -1;
    curVal = 0; 
}

/*
 * gradually increases speed of motors
 * @param i: velocity counter
 * @param c: 0 starts motors
 * @param d: 0 for forward, 1 for backward
 */
void Ramp(int i, int c, int d)
{
    curVal = 90+3*i;
    analogWrite(MTR_A_EN, curVal);
    analogWrite(MTR_B_EN, int(curVal*scale));
    delay(35);
    
    if(c == 0)
    {
        if(d == 0) //forward
        {
            analogWrite(MTR_A_EN, int(.5*curVal));
            digitalWrite(MTR_B_A, HIGH);
            digitalWrite(MTR_B_B, LOW);
            digitalWrite(MTR_A_A, HIGH);
            digitalWrite(MTR_A_B, LOW);
        }
        else if(d == 1) //backward
        {
            analogWrite(MTR_A_EN, int(.5*curVal));
            digitalWrite(MTR_B_B, HIGH);
            digitalWrite(MTR_B_A, LOW);
            digitalWrite(MTR_A_B, HIGH);
            digitalWrite(MTR_A_A, LOW);            
        }
    }
}


//********************************************************* DRIVE
/* drives forward or backwards
 * @param velocity : in range -10, 10 inclusive, 0 = stop
 * @param dir: direction 0 = forward, 1 = backward
 */
void Drive(int velocity, uint8_t dir)
{
    int c = 0;
    
    if(velocity < minV || velocity > maxV)
    {
        Serial.println("velocity must be in range of [minV, maxV]");
        return;
    }

    //changing directions
    if(curDir != -1 && curDir != dir)
    {
        Stop();
    }
    

    //increasing speed
    if((curDir == -1 || curDir == dir) && velocity > curSpd) 
    {
        for(int i = curSpd+1; i <= velocity; i++)
        {
            Ramp(i, c, dir);
            c = 1;
        }
    }

    //decreasing speed
    else if((curDir == -1 || curDir == dir) && velocity < curSpd)
    {
        Serial.println("decreasing.");
        for(int i = curSpd-1; i >= velocity; i--)
        {
            Ramp(i, c, dir);
            c = 1; 
        }
    }
    
    else
    {
        Stop();
    }
    curSpd = velocity;
    curDir = dir;
}

//********************************************************* DRIVE
/* turns left or right, heading turns or dime turns
 * @param dir: direction, 2=left, 3=right
 * @param deg: turn degrees in range (0, 180] in 5 deg steps
 * @param dime: 1 for dime turn, 0 for regular turn. if set to 1 
 *          and deg = 0 will continue to turn until stopped
 */
void Turn(uint8_t dir, int deg, bool dime)
{
    int c = 0; 

    if(!dime && (dir != 2 || dir != 3 || deg < 1 || deg > 180 || deg % 5 != 0 || deg == 0))
    {
        Serial.println("bad turn.");
        return; 
    }

    if(dime || curVal == 0)
    {
        if(dir == 2)
        {
            analogWrite(MTR_B_EN, 120);
            analogWrite(MTR_A_EN, 120);
            digitalWrite(MTR_B_B, HIGH);
            digitalWrite(MTR_B_A, LOW);
            digitalWrite(MTR_A_A, HIGH);
            digitalWrite(MTR_A_B, LOW);
            delay(DegToDelay(1, deg));
        }

        else if(dir == 3)
        {
            analogWrite(MTR_B_EN, 120);
            analogWrite(MTR_A_EN, 120);
            digitalWrite(MTR_B_A, HIGH);
            digitalWrite(MTR_B_B, LOW);
            digitalWrite(MTR_A_B, HIGH);
            digitalWrite(MTR_A_A, LOW);
            delay(DegToDelay(1, deg));
        }
        
        else
        {
            Serial.println("bad turn.");
        }
    }
    
    else if(curVal != 0 && dir == 2)
    {
      
          analogWrite(MTR_B_EN, );
          analogWrite(MTR_A_EN, 120);
          digitalWrite(MTR_B_A, HIGH);
          digitalWrite(MTR_B_B, LOW);
          digitalWrite(MTR_A_A, HIGH);
          digitalWrite(MTR_A_B, LOW);        
        
    }
    
    
}


/********************************************************************************************************
 *                                               SETUP                                                  *                                                  
 ********************************************************************************************************/
void setup() 
{
 
    //enable the serial port
    Serial.begin(38400);
    //Serial1.begin(9600);
  
    //configure line following sensors
    pinMode(LEFT_IR, INPUT);
    pinMode(MIDDLE_IR, INPUT);
    pinMode(RIGHT_IR, INPUT);
  
    pinMode(LEFT_LED, OUTPUT);
    pinMode(MIDDLE_LED, OUTPUT);
    pinMode(RIGHT_LED, OUTPUT);
  
    //configure voltage sensor reading
    pinMode(VOLTAGE_SR, INPUT);
  
    //configure motor pins as output
    for(int i = 0; i < 6; i++)
    {
      pinMode(motorPins[i], OUTPUT);
    }
    
    //turn motors off
    Stop();
    
}



/********************************************************************************************************
 *                                                MAIN                                                  *                                                  
 ********************************************************************************************************/
void loop() 
{
   // Turn(3, 90, 1);
   // delay(200);
  //  Drive(12, 1);
    //delay(1000);
   // Drive(7, 0);
   // delay(1000);
    Stop();
    delay(5000);
  
}
















