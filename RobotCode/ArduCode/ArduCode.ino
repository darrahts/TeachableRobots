
//#include <Servo.h>
#include <EEPROM.h>
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
#define TRIG 4
#define ECHO 12

//line sensors
#define LEFT_IR A2
#define RIGHT_IR A3
#define MIDDLE_IR A4

//pan and tilt servo
//#define PAN_SERVO A0
//#define TILT_SERVO A1
//Servo pan;
//Servo tilt;


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
//#define PAN_LEFT_MAX 170
//#define PAN_CENTER 105
//#define PAN_RIGHT_MAX 40
//
////tilt range of motion
//#define TILT_UP_MAX 30
//#define TILT_CENTER 120
//#define TILT_DOWN_MAX 150

//size of input / command sequence
#define INPUT_SIZE 254
#define SEQUENCE_LENGTH 60

//size of EEPROM 1024 for uno, 4096 for mega
#define EEPROM_SIZE 1023

/********************************************************************************************************
 *                                             GLOBAL VARIABLES                                         *                                                  
 ********************************************************************************************************/
//if the robot is stopped (0) going forward (1) backward (2) left (3) right (4)
int dir = 1;

//holds the input received from serial
char input[INPUT_SIZE + 1];

//holds the command and amounts for the current executing sequence
int commands[SEQUENCE_LENGTH];
int amounts[SEQUENCE_LENGTH];

//used to loop through motor pins to turn them off
int motorPins[] = {6,7,8,11,9,10};

//used for sonic range sensor, tof of echo
long duration;

//used for sonic range sensor, distance to obj in cm
int distance;

//IR baseline readings. adjust these to your sensors and environment
int readings[] = {500,400,700};

//The most recent command executed
int cmd = 0;

//used for logic control with line following
int state = 0;

//used to count intersections (nodes) 
int count = 0;

//used for eeprom addressing
int memAdr = 0; 

//map of the coordinate space
byte coordinateSpace[10][10] ={{1,1,1,0,0,0,0,0,0,0},
                               {0,0,1,0,0,0,0,0,0,0},
                               {0,0,1,0,0,0,0,0,0,0},
                               {0,0,1,0,0,0,0,0,0,0},
                               {0,0,1,1,1,1,0,0,0,0},
                               {0,0,0,0,0,1,0,0,0,0},
                               {1,1,0,0,0,1,0,0,0,0},
                               {0,1,1,1,1,1,0,0,0,0},
                               {0,0,0,0,0,0,0,0,0,0},
                               {0,0,0,0,0,0,0,0,0,0}};
                            


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
    dir = 0;
}

/*                         FORWARD                
 *        Robot drives forward, accounts for 
 *        motor differences with offset
 */
void Forward()
{
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  dir = 1;
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
  dir = 2;
}

/*                         LEFT   / LEFT ADJUST            
 *        uses duration in a delay to adjust the angle
 *        195 is for right angle turns while in motion
 *        adjust is used for line tracking
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
  dir = 3;
}

void LeftAdjustFwd(int duration)
{
  analogWrite(MTR_A_EN, SPEED+20);
  analogWrite(MTR_B_EN, LOW);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, LOW);
  delayMicroseconds(1000*duration);
}

void LeftAdjustBk(int duration) //needs fixed
{
  analogWrite(MTR_A_EN, LOW);
  analogWrite(MTR_B_EN, SPEED+20);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  delay(duration);
}

/*                         RIGHT   / RIGHT ADJUST          
 *        uses duration in a delay to adjust the angle
 *        195 is for right angle turns while in motion
 *        adjust is used for line tracking
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
  dir = 4;
}

void RightAdjustFwd(int duration)
{
  analogWrite(MTR_A_EN, LOW);
  analogWrite(MTR_B_EN, SPEED+20);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  delayMicroseconds(1000*duration);
}

void RightAdjustBk(int duration) //needs fixed
{
  analogWrite(MTR_A_EN, SPEED+20);
  analogWrite(MTR_B_EN, LOW);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, LOW);
  delay(duration);
}

/*                         PARSE COMMAND          
 *        Takes a command input in the form:
 *        move1&amount1:move2&amoount2:<etc>:move60&amount60:*
 *        
 *        ex 1-2_5-0_* would be forward 2 then stop
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
        
        // Add the final 0 to end of the input string
        input[size_] = 0;
        //Serial.println(input);

        //counters for the commands and amounts
        int c = 0;
        int a = 0;
        
        // Read each command pair 
        char* command = strtok(input, "_");
        
        while (command != 0)
        {
            // Split the input command in two values (command and amount)
            char* separator = strchr(command, '-');
            if (separator != 0)
            {
                //split the string in 2: replace '_' with 0
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
            command = strtok(0, "_");
         }
         commands[c] = 5;
         amounts[a] = 0;
    }
    //Serial.println(commands[1]);
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
        for(int i = 0; i < SEQUENCE_LENGTH; i++)
        {
            if(commands[i] == 1)
            {
                Serial.println("fwd****************");
                while(count != amounts[i])
                {
                    Forward();
                    ReadLineSensors();
                    AssertCourse();
                }
                count = 0; 
            }
            else if(commands[i] == 2)
            {
                //Serial.println("bk");
                while(count != amounts[i])
                {
                    Backward();
                    ReadLineSensors();
                    AssertCourse();
                    test();
                }
            }
            else if(commands[i] == 3)
            {
               Serial.println("left****************");
                Left(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 4)
            {
                Serial.println("right****************");
                Right(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 5)
            {
                Serial.println("stop");
                Stop();
            }
            else if(commands[i] == 6)
            {
                Serial.println("entering test mode.");
                test();
                Serial.println("exited test mode.");
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

/*                            READ LINE SENSORS          
 *        Takes an analog reading of the IR sensors and computes
 *        course correction movements if necessary
 */
void ReadLineSensors()
{
    readings[0] = analogRead(LEFT_IR);
    readings[1] = analogRead(MIDDLE_IR);
    readings[2] = analogRead(RIGHT_IR);
}


/*                         CHECK DISTANCE          
 *        Obstacle detection, uses the robots current dir
 *        to respond with appropriate avoidance movement
 */
int CheckDistance()
{
  digitalWrite(TRIG, LOW);
  delayMicroseconds(5);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = duration / 29 / 2;
  if(distance < 20 && distance >10)
  {
    if(dir == 1)
    {
      Backward();
      delay(500);
       Stop();
    }
    else if(dir == 3)
    {
      Backward();
      delay(100);
       Stop();
      Left(100);
       Stop();
    }
      else if(dir == 4)
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


/*                         ASSERT COURSE          
 *        Ensures the robot follows the line and tracks the number
 *        of intersections (nodes) crossed.
 */
void AssertCourse()
{
    //if the robot is on course
    if (state == 1 && readings[0] < 640 && readings[1] > 640 && readings[2] < 820)
    {
        Serial.println("-\\");
        state = 0;
    }
    //if the robot reaches an intersection
    else if(state == 0 && (dir == 1 || dir == 2) && readings[0] > 700 && readings[1] > 700 && readings[2] > 820)
    {
        count += 1;
        state = 1;
        Serial.println("intersection");
        //Serial.println("here");
    }
    //if the left and middle sensor read the line and the right sensor does not               
    else if ( readings[0] > 700 && readings[1] > 700 && readings[2] < 800)
    {
        Serial.println("Go left!");
        if(dir == 1)
        {
            LeftAdjustFwd(15);
        }
        if(dir == 2)
        {
            LeftAdjustBk(15);
        }       
    }
    //if the left sensor reads the line and the middle and right do not
    else if(readings[0] > 700 && readings[1] < 600 && readings[2] < 800)
    {    
        Serial.println("Go left!");
        if(dir == 1)
        {
            LeftAdjustFwd(30); 
        }
        if(dir == 2)
        {
            LeftAdjustBk(30);
        }            
    }
    //if the right and middle sensor read the line and the left sensor does not
    else if ( readings[0] < 600 && readings[1] > 700 && readings[2] > 820)
    {
        Serial.println("Go right!");
        if(dir == 1)
        {
            RightAdjustFwd(15);
        }
        if(dir == 2)
        {
            RightAdjustBk(15);
        }  
    }
    //if the right sensor reads the line and the middle and left do not
    else if(readings[0] < 600 && readings[1] < 600 && readings[2] > 820)
    {
        Serial.println("Go right!");
        if(dir == 1)
        {
            RightAdjustFwd(30);
        }
        if(dir == 2)
        {
            RightAdjustBk(30);
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
  //Serial1.begin(9600);

  //configure sonic range sensor
  //pinMode(TRIG, OUTPUT);
  //pinMode(ECHO, INPUT);

  //configure servos
  //pan.attach(PAN_SERVO);
  //tilt.attach(TILT_SERVO);

  //configure line following sensors
  pinMode(LEFT_IR, INPUT);
  pinMode(MIDDLE_IR, INPUT);
  pinMode(RIGHT_IR, INPUT);

  //configure motor pins as output
  for(int i = 0; i < 6; i++)
  {
    pinMode(motorPins[i], OUTPUT);
  }
  
  //turn motors off and center the ptu
  Stop();
  //pan.write(PAN_CENTER);
  //tilt.write(TILT_CENTER); 
}


/********************************************************************************************************
 *                                                MAIN                                                  *                                                  
 ********************************************************************************************************/

void loop() 
{
    //Serial.println(coordinateSpace[1][2]);
    //dir = 2;
    //LeftAdjustBk(50);
    
    //ReadLineSensors();
    //AssertCourse();
    //test();
    //Serial.print(readings[0]); Serial.print("\t"); Serial.print(readings[1]); Serial.print("\t"); Serial.println(readings[2]);
    //LeftAdjust(100);
    //RightAdjust(100);
    //Stop();
    //delay(500);
    //Serial.println(CheckDistance());
    //NewPing sonar(TRIG, ECHO, 100);
    //Serial.println(sonar.ping_cm());
    //delay(250);
    
    ParseCommand();
    ExecuteCommand();
}

void eepromReadTest()
{
    for(int i = 0; i < 100; i++)
    {
        if(i%10 == 0)
        {
            Serial.println();
        }
        Serial.print(EEPROM.read(i));
        Serial.print(" ");
    }
    delay(2000);
}

void eepromWriteTest()
{
  bool finished = false;
  while(!finished)
  {
    for(int i = 0; i < 10; i++)
    {
        for(int j = 0; j < 10; j++)
        {
            EEPROM.write(memAdr, coordinateSpace[i][j]);
            memAdr += 1; 
            //Serial.print(coordinateSpace[i][j]);
            //Serial.print(" ");
            //Serial.print(sizeof(coordinateSpace[i][j]));
        }
        Serial.println();
    }
    delay(2000);
    finished = true;
  }
}

void test()
{  
    while(true)  
    {
        ReadLineSensors();
        AssertCourse();
        if(Serial.available() > 0)
        {
            cmd = int(Serial.read());
            Serial.println(cmd);
        }
        if(cmd == 48)
        {
            Stop();
        }
        else if (cmd == 49)
        {
            Forward();
        }
        else if (cmd == 50)
        {
            Backward();
        }
        else if (cmd == 51)
        {
            Left(195);
        }
        else if (cmd == 52)
        {
            Right(195);
        }
        else if(cmd == 53)
        {
     //     break;
        }
        else
        {
            Stop();
        }
    }
}

//1-2_3-90_1-2_5-0_*














