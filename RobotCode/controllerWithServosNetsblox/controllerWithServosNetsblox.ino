#include <Servo.h>

Servo MTR_A;
Servo MTR_B;


//min and max velocity vals
int minV = -20; 
int maxV = 20;

//min and max servo vals
int minS = 30;
int maxS = 150;

int currentSpeed = 0;


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
    
    MTR_A.write(90+scale*i);
    MTR_B.write(90-scale*i);
    delay(35);   
}

void RampL(int i)
{
    int scale = 3;
    MTR_A.write(90+scale*i);
    MTR_B.write(90+scale*i);
    delay(35); 
}

void RampR(int i)
{
    int scale = 3;
    MTR_A.write(90-scale*i);
    MTR_B.write(90-scale*i);
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
}


//********************************************************* TURN
/*
 * turns left or right
 */





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
    
    //forward and increasing or backward and decreasing
    if((currentSpeed >= 0 && currentSpeed < velocity) || (velocity <= 0 && velocity > currentSpeed))
    {
        for(int i = currentSpeed+1; i <= velocity; i++) 
        {
            Ramp(i);
        }
    }

    //forward and decreasing or backward and increasing
    else if((velocity >= 0 && velocity < currentSpeed) || (currentSpeed <= 0 && currentSpeed > velocity))
    {
        for(int i = currentSpeed-1; i >= velocity; i--)
        {
            Ramp(i);
        }
    }

    //forward to backward
    else if(currentSpeed > 0 && velocity < 0)
    {
        Stop();
        for(int i = -1; i >= velocity; i--)
        {
            Ramp(i);
        }
    }

    //backward to forward
    else if(currentSpeed < 0 && velocity > 0)
    {
        Stop();
        for(int i = 1; i <= velocity; i++)
        {
            Ramp(i);
        }
    }
    else
    {
        Stop();
    }
    currentSpeed = velocity;
}

//*********************************************** SETUP
//***********************************************************
void setup() 
{
    MTR_A.attach(9);
    MTR_B.attach(10);
    Serial.begin(38400);
    
}

//*********************************************** MAIN
//***********************************************************
void loop() 
{

//    Drive(-10);
//    delay(1000);
//    Drive(10);
//    delay(1000);
    Stop();
    delay(2000);
}





















