#include <Servo.h>
/********************************************************************************************************
 *                                             PIN DEFINITIONS                                          *                                                  
 ********************************************************************************************************/

//right motor (facing with the robot)
#define MTR_A_EN 6
#define MTR_A_A 7
#define MTR_A_B 8

//left motor
#define MTR_B_EN 11
#define MTR_B_A 9
#define MTR_B_B 10

//sonic range sensor
#define TRIG 6
#define ECHO 12

//line sensors
#define LEFT_IR A2
#define RIGHT_IR A3
#define MIDDLE_IR A4

//pan and tilt servo
#define PAN_SERVO A0
#define TILT_SERVO A1
Servo pan;
Servo tilt;


/********************************************************************************************************
 *                                             CONSTANT DEFINITIONS                                     *                                                  
 ********************************************************************************************************/

// motor speeds
//the offset and speed values should be calibrated for every
//motor pair.  the robot should drive straight for a minimum
//distance of 5ft to be considered calibrated
#define OFFSET 25 
#define SPEED 105

//pan range of motion
#define PAN_LEFT_MAX 170
#define PAN_CENTER 105
#define PAN_RIGHT_MAX 40

//tilt range of motion
#define TILT_UP_MAX 30
#define TILT_CENTER 120
#define TILT_DOWN_MAX 150

//size of input / command sequence
#define INPUT_SIZE 254
#define SEQUENCE_LENGTH 60


/********************************************************************************************************
 *                                             GLOBAL VARIABLES                                         *                                                  
 ********************************************************************************************************/
//if the robot is stopped (0) going forward (1) backward (2) left (3) right (4)
byte state = 0;

//holds the input received from serial
char input[INPUT_SIZE + 1];

//holds the command and amounts for the current executing sequence
int commands[SEQUENCE_LENGTH];
int amounts[SEQUENCE_LENGTH];

//used to loop through motor pins to turn them off
int motorPins[] = {6,7,8,11,9,10};

//used for control in the main loop instead of delays
long timer = 0;


/********************************************************************************************************
 *                                               FUNCTIONS                                              *                                                  
 ********************************************************************************************************/

/*                         STOP                
 *        turns off the motors
 */
void Stop()
{
    for(int i = 0; i < 6; i++)
    {
      digitalWrite(motorPins[i], LOW);
    }
    state = 0;
}

/*                         FORWARD                
 *        Robot drives forward, accounts for 
 *        motor differences with offset
 */
void Forward()
{
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  state = 1;
}

/*                         BACKWARD                
 *        Robot drives in reverse, accounts for 
 *        motor differences with offset
 */
void Backward()
{
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  state = 2;
}

/*                         LEFT               
 *        uses duration in a delay to adjust the angle
 *        195 is for right angle turns while in motion
 */
void Left(int duration)
{
  analogWrite(MTR_A_EN, SPEED + 20);
  analogWrite(MTR_B_EN, SPEED + 20 - OFFSET);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  delay(duration); 
   Stop();
  state = 3;
}

/*                         RIGHT             
 *        uses duration in a delay to adjust the angle
 *        195 is for right angle turns while in motion
 */
void Right(int duration)
{
  analogWrite(MTR_A_EN, SPEED + 20);
  analogWrite(MTR_B_EN, SPEED + 20 - OFFSET);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  delay(duration); 
  Stop();
  state = 4;
}

/*                         CHECK DISTANCE          
 *        Obstacle detection, uses the robots current state
 *        to respond with appropriate avoidance movement
 */
int CheckDistance()
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
      Backward();
      delay(500);
       Stop();
    }
    else if(state == 3)
    {
      Backward();
      delay(100);
       Stop();
      Left(100);
       Stop();
    }
      else if(state == 4)
    {
      Backward();
      delay(100);
       Stop();
      Right(100);
       Stop();
    }
  }
  return distance;
}

/*                         PARSE COMMAND          
 *        Takes a command input in the form:
 *        move1&amount1:move2&amoount2:<etc>:move60&amount60:*
 *        
 *        ex 1&10:2&2:5&0:* would be
 *        forward 10 then left 2 then plot end. 
 *        
 *        1 = forward    \___ amount from 0 to 20 in units
 *        2 = backward   /
 *        3 = left       \___ amount from 0 to 180 in degrees
 *        4 = right      /
 *        5 = stop  --------- input should be 6&0 
 *        * = end   --------- end of command sequence
 */
void ParseCommand()
{
    //check if theres anything in the stream
    if(Serial.available())
    {
        //read the stream into the input variable and returns
        //the number of bytes to size_
        byte size_ = Serial.readBytes(input, INPUT_SIZE);
        
        //counters for commands and amounts
        int c = 0;
        int a = 0; 
        
        // Add the final 0 to end of the input string
        input[size_] = 0;
        Serial.println(input);
        
        // Read each command pair 
        char* command = strtok(input, ":");
        
        while (command != 0)
        {
            // Split the command in two values
            char* separator = strchr(command, '&');
            if (separator != 0)
            {
                // Actually split the string in 2: replace ':' with 0
                *separator = 0;
                
                //put the command in the commands array at the same
                //index as the corresponding amount
                commands[c] = atoi(command);
                c++;
                ++separator;
                
                //put the amount in the amounts array at the same
                //index as the corresponding command
                amounts[a] = atoi(separator);
                a++;
            }
            // Find the next command in input string
            command = strtok(0, ":");
        }
    }
}

/*                         EXECUTE COMMAND          
 *        Sequentially executes the commands from the commands
 *        array and amounts array. Does not use delays so line
 *        tracking and obstacle detection can operate at each
 *        iteration.
 */
void ExecuteCommand()
{
    if(commands[0] > 0)
    {
        Serial.println(commands[1]);
        Serial.println(amounts[1]);
        for(int i = 0; i < SEQUENCE_LENGTH; i++)
        {
            if(commands[i] == 1)
            {
                Forward();
                delay(1000*amounts[i]);                            //FIX THIS DELAY
            }
            else if(commands[i] == 2)
            {
                Backward();
                delay(1000*amounts[i]);                           //FIX THIS DELAY
            }
            else if(commands[i] == 3)
            {
                Left(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 4)
            {
                Right(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 5)
            {
                Stop();
            }
            else
            {
                Stop();
            }
            commands[i] = -1;
            amounts[i] = 0;
        }
    }
}


/********************************************************************************************************
 *                                               SETUP                                                  *                                                  
 ********************************************************************************************************/
void setup() 
{
  //enable the serial port
  Serial.begin(9600);

  //configure sonic range sensor
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  //configure servos
  pan.attach(PAN_SERVO);
  tilt.attach(TILT_SERVO);

  //configure line following sensors
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);

  //configure motor pins as output
  for(int i = 0; i < 6; i++)
  {
    pinMode(motorPins[i], OUTPUT);
  }
  
  //turn motors off and center the ptu
  Stop();
  pan.write(PAN_CENTER);
  tilt.write(TILT_CENTER); 
}


/********************************************************************************************************
 *                                                MAIN                                                  *                                                  
 ********************************************************************************************************/
void loop() 
{
  ParseCommand();
  ExecuteCommand();
}









