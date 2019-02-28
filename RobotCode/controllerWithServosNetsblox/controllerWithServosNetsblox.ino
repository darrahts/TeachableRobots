#include <Servo.h>

Servo MTR_L;
Servo MTR_R;

//line sensors
#define LEFT_IR A3
#define MIDDLE_IR A0
#define RIGHT_IR A2

//voltage sensor
#define VOLTAGE_SR A1

//min and max velocity vals
int minV = -20; 
int maxV = 20;

//min and max servo vals
int minS = 30;
int maxS = 150;

int currentSpeed = 0;
int amountL = 0;
int amountR = 0;

//battery voltage
double voltage = 0.0;

int dir = 0;


//IR baseline readings. adjust these to your sensors and environment
int readings[] = {500,400,700};



void CheckVoltage()
{
    double v = (analogRead(VOLTAGE_SR) * 5.0) / 1024.0;
    voltage = (v * 10500.0 / 1500.0);
    Serial.write('~');
    delay(50);
    Serial.println(voltage);
}

void ReadLineSensors()
{
    readings[0] = analogRead(LEFT_IR);
    readings[1] = analogRead(MIDDLE_IR);
    readings[2] = analogRead(RIGHT_IR);
}



/*
 * gradually changes motor speed to prevent spiking / wear on motors
 * scale is determined by the servo range / velocity range, i.e.
 *            servo range: 30 <-> 150 gives 120
 *            veloc range: -20 <-> 20 gives 40
 *            scale = 3
 */
void Ramp(int i)
{
    int scale = 3;
    amountL = 92-scale*i;
    amountR = 93+scale*i;
    if(dir == 1)
    {
        MTR_L.write(amountL);
        MTR_R.write(amountR);
    }
    else if(dir == 2)
    {
        MTR_L.write(91-scale*i);
        MTR_R.write(89+scale*i);
    }
    delay(35);   
}

void RampL(int i)
{
    int scale = 3;
    if(dir == 1)
    {
        MTR_L.write(amountL-2-scale*i);
        MTR_R.write(amountR+scale*i);
    }
}

void RampR(int i)
{
    int scale = 3;
    MTR_L.write(90-scale*i);
    MTR_R.write(90-scale*i);
    delay(35); 
}

//********************************************************** STOP
/*
 * stops the motors
 */
void Stop()
{
    if(currentSpeed < 0)
    {
        for(int i = currentSpeed+1; i <= 0; i++)
        {
            Ramp(i);
        }
    }
    if(currentSpeed > 0)
    {
        for(int i = currentSpeed-1; i >= 0; i--)
        {
            Ramp(i);
        }
    }
    else
    {
        Ramp(0);
    }
    currentSpeed = 0;
    dir = 0;
}


//********************************************************* TURN
/*
 * turns left or right
 */
void Left(int amount)
{
    int curDir = dir;
    int curSpd = currentSpeed;
    dir = 3;
    if(currentSpeed != 0)
    {
        int newAmount = amountL+amount;
        Serial.println(newAmount);
        MTR_L.write(newAmount);
        //MTR_R.write(amountR-amount);
    }
    dir = curDir;
    Serial.println(amountL);
    MTR_L.write(amountL);
    MTR_L.write(amountR);
}



//********************************************************* DRIVE
/* drives forward or backwards
 * @param velocity : in range -20, 20 inclusive, 0 = stop
 */
void Drive(int velocity)
{
    if(velocity < minV || velocity > maxV)
    {
        Serial.println("velocity must be in range of [minV, maxV]");
        return;
    }
    
    //forward and increasing
    if((currentSpeed >= 0 && currentSpeed < velocity) || (velocity <= 0 && velocity > currentSpeed))
    {
        dir = 1;
        for(int i = currentSpeed+1; i <= velocity; i++) 
        {
            Ramp(i);
        }
    }

    //backward and increasing
    else if((velocity >= 0 && velocity < currentSpeed)) // || (currentSpeed <= 0 && currentSpeed > velocity))
    {
        dir = 1;
        for(int i = currentSpeed-1; i >= velocity; i--)
        {
            Ramp(i);
        }
    }

    
    else if((currentSpeed <= 0 && currentSpeed > velocity))
    {
        dir = 2;
        for(int i = currentSpeed-1; i >= velocity; i--)
        {
            Ramp(i);
        }      
    }

    //forward to backward
    else if(currentSpeed > 0 && velocity < 0)
    {
        Stop();
        dir = 2;
        for(int i = -1; i >= velocity; i--)
        {
            Ramp(i);
        }
    }

    //backward to forward
    else if(currentSpeed < 0 && velocity > 0)
    {
        Stop();
        dir = 1;
        for(int i = 1; i <= velocity; i++)
        {
            Ramp(i);
        }
    }
//    else
//    {
//        Stop();
//    }
    currentSpeed = velocity;
}

//*********************************************** SETUP
//***********************************************************
void setup() 
{
    MTR_L.attach(9);
    MTR_R.attach(10);

    //configure line following sensors
    pinMode(LEFT_IR, INPUT);
    pinMode(MIDDLE_IR, INPUT);
    pinMode(RIGHT_IR, INPUT);

    //configure voltage sensor reading
    pinMode(VOLTAGE_SR, INPUT);
    
    Serial.begin(115200);
    
}

//*********************************************** MAIN
//***********************************************************
void loop() 
{

 //   Drive(-5);
    Serial.println(dir);
    Serial.println(amountL);
    Serial.println(amountR);
 //   MTR_L.write(109);
 //   MTR_R.write(107);
    
    //Serial.println(currentSpeed);
    delay(1000);
    //Left(7);
    
//    ReadLineSensors();
//    for(int i = 0; i < 3; i++)
//    {
//        Serial.print(readings[i]); Serial.print('\t');
//    }
//    Serial.println();
//    delay(500);
//      Stop();
//    Drive(-7);
//    Serial.println(dir);
//    delay(1000);
//    Drive(-3);
//    Serial.println(dir);
//    delay(1000);
//    Drive(3);
//    Serial.println(dir);
//    delay(1000);
//    Drive(7);
//    Serial.println(dir);
//    delay(1000);
//    Drive(-5);
//    Serial.println(dir);
//    delay(1000);
//    Stop();













    
}
