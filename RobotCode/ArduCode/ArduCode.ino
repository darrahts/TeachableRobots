
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

//line sensors
#define LEFT_IR A3
#define MIDDLE_IR A4
#define RIGHT_IR A2

#define LEFT_LED 3
#define MIDDLE_LED 4
#define RIGHT_LED 5

//voltage sensor
#define VOLTAGE_SR A1

//sonic range sensor
//#define TRIG 4
//#define ECHO 12

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
int OFFSET = 26;
int SPEED = 110;

//pan range of motion
//#define PAN_LEFT_MAX 170
//#define PAN_CENTER 105
//#define PAN_RIGHT_MAX 40
//
////tilt range of motion
//#define TILT_UP_MAX 30
//#define TILT_CENTER 120
//#define TILT_DOWN_MAX 150

//line readings > BLACK = black line, < WHITE = white canvas
#define BLACK 260
#define WHITE 245

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

//battery voltage
double voltage = 0.0;

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
                            

bool previousState[] = {0,0,0,0,0,0,0,0,0,0};
bool currentState[] = {0,0,0,0,0,0,0,0,0,0};
bool nextState[] = {0,0,0,0,0,0,0,0,0,0};

bool onCourse = false;
bool tooFarRight = false;
bool tooFarLeft = false;
bool atIntersection = false;
bool passedIntersection = true;
bool turning = false;
bool finishedTurning = false;
bool managed = true;

bool leftTriggered = false;
bool middleTriggered = false;
bool rightTriggered = false;

int leftCount = 0;
int rightCount = 0;


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
  if(managed)
  {
    Forward();
    delay(350);
  }
  analogWrite(MTR_A_EN, SPEED);
  analogWrite(MTR_B_EN, SPEED - OFFSET);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, HIGH);
  if(managed)
  {
      delay(50);
      ReadLineSensors();
      while(readings[1] > WHITE)
      {
        ReadLineSensors();
      }
      delay(10);
      while(readings[2] > WHITE)
      {
        ReadLineSensors();
      }
      delay(10);
      while(readings[0] < BLACK) 
      {
        ReadLineSensors();
      }
  }
  else
  {
      delay(duration);
  }
   Stop();
  dir = 3;
}

void LeftAdjustFwd(int duration)
{
  analogWrite(MTR_A_EN, SPEED+25);
  analogWrite(MTR_B_EN, LOW);
  digitalWrite(MTR_A_A, HIGH);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, LOW);
  digitalWrite(MTR_B_B, LOW);
  delay(duration / 10);
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
  if(managed)
  {
    Forward();
    delay(350);
  }
  analogWrite(MTR_A_EN, SPEED + 20);
  analogWrite(MTR_B_EN, SPEED + 20 - OFFSET);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, HIGH);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  if(managed)
  {
      delay(50);
      ReadLineSensors();
      while(readings[1] > WHITE)
      {
        ReadLineSensors();
      }
      delay(10);
      while(readings[0] > WHITE)
      {
        ReadLineSensors();
      }
      delay(10);
      while(readings[2] < BLACK) 
      {
        ReadLineSensors();
      }
  }
  else
  {
      delay(duration);
  }
  Stop();
  dir = 4;
}

void RightAdjustFwd(int duration)
{
  analogWrite(MTR_A_EN, LOW);
  analogWrite(MTR_B_EN, SPEED+25);
  digitalWrite(MTR_A_A, LOW);
  digitalWrite(MTR_A_B, LOW);
  digitalWrite(MTR_B_A, HIGH);
  digitalWrite(MTR_B_B, LOW);
  delay(duration / 10);
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
 *        move1-amount1_move2-amoount2_<etc>_*
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
                //Serial.println("fwd****************");
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
                }
            }
            else if(commands[i] == 3)
            {
               //Serial.println("left****************");
                Left(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 4)
            {
                //Serial.println("right****************");
                Right(int(2.166666 * amounts[i]));
            }
            else if(commands[i] == 5)
            {
                Serial.println("stop");
                Stop();
            }
            else if(commands[i] == 6)
            {
                Serial.println("entering ManualControl mode.");
                ManualControl();
                Serial.println("exited ManualControl mode.");
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
    digitalWrite(LEFT_LED, HIGH);
    digitalWrite(RIGHT_LED, HIGH);
    digitalWrite(MIDDLE_LED, HIGH);
    delay(5);
    readings[0] = analogRead(LEFT_IR);
    readings[1] = analogRead(MIDDLE_IR);
    readings[2] = analogRead(RIGHT_IR);
    digitalWrite(LEFT_LED, LOW);
    digitalWrite(RIGHT_LED, LOW);
    digitalWrite(MIDDLE_LED, LOW);
    //Serial.println("read");
}

/*                            CHECK VOLTAGE          
 *        Reads the VIN voltage (i.e. direct from battery)
 *        5.5 is an approximation from the voltage divider
 *        analog read gives 0-1024 so need to divide by 1024
 *        12200 = r1 + r2 2200 = r2
 */
void CheckVoltage()
{
    double v = (analogRead(VOLTAGE_SR) * 5.54) / 1024.0;
    voltage = (v * 12200.0 / 2200.0);
    Serial.println(voltage);
}

/*                         ASSERT COURSE          
 *        Ensures the robot follows the line and tracks the number
 *        of intersections (nodes) crossed.
 */
void AssertCourse()
{
    //if the robot is on course
    if (readings[0] < WHITE && readings[1] > BLACK && readings[2] < WHITE)
    {
        onCourse = true;
        if(atIntersection == true)
        {
            atIntersection = false;
            passedIntersection = true;
            Serial.println("-");
        }
        state = 0;
    }
    //if the robot reaches an intersection
    else if( onCourse && (dir == 1 || dir == 2) && readings[0] > BLACK && readings[1] > BLACK && readings[2] > BLACK)
    {
        if (count == 0 || passedIntersection == true)
        {
            atIntersection = true;
            passedIntersection = false;
            count += 1;      
            Serial.println("+");      
        }
        state = 1;
        //Serial.println("here");
    }
    //if the left and middle sensor read the line and the right sensor does not               
    else if ( readings[0] > BLACK && readings[1] > BLACK && readings[2] < WHITE)
    {
        passedIntersection = true;
        tooFarLeft = false;
        tooFarRight = true;
        Serial.println("<");
        leftCount += 1;
        if(leftCount == 8)
        {
          OFFSET += 1;
          leftCount = 0;
        }
        if(dir == 1)
        {
            LeftAdjustFwd(150);
        }
        if(dir == 2)
        {
            LeftAdjustBk(30);
        }       
    }
    //if the left sensor reads the line and the middle and right do not (needs larger correction)
    else if(readings[0] > BLACK && readings[1] < WHITE && readings[2] < WHITE)
    {    
      passedIntersection = true;
        tooFarLeft = false;
        tooFarRight = true;
        Serial.println("<<");
        leftCount += 1;
        if(leftCount == 8)
        {
          OFFSET += 1;
          leftCount = 0;
        }
        if(dir == 1)
        {
            LeftAdjustFwd(200); 
        }
        if(dir == 2)
        {
            LeftAdjustBk(50);
        }            
    }
    //if the right and middle sensor read the line and the left sensor does not
    else if ( readings[0] < WHITE && readings[1] > BLACK && readings[2] > BLACK)
    {
      
        tooFarRight = false;
        tooFarLeft = true;
        Serial.println(">");
        rightCount += 1;
        if(rightCount == 8)
        {
          OFFSET -= 1;
          rightCount = 0;
        }
        if(dir == 1)
        {
            RightAdjustFwd(150);
        }
        if(dir == 2)
        {
            RightAdjustBk(30);
        }  
    }
    //if the right sensor reads the line and the middle and left do not (needs larger correction)
    else if(readings[0] < WHITE && readings[1] < WHITE && readings[2] > BLACK)
    {
        tooFarRight = false;
        tooFarLeft = true;
        Serial.println(">>");
        rightCount += 1;
        if(rightCount == 8)
        {
          OFFSET -= 1;
          rightCount = 0;
        }
        if(dir == 1)
        {
            RightAdjustFwd(200);
        }
        if(dir == 2)
        {
            RightAdjustBk(50);
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
    //CheckVoltage();
    //Serial.println(analogRead(VOLTAGE_SR));
    //Serial.println(coordinateSpace[1][2]);
  
    //ReadLineSensors();
    //Serial.print(readings[0]); Serial.print("\t"); Serial.print(readings[1]); Serial.print("\t"); Serial.println(readings[2]);
    
     // byte size_ = Serial.readBytes(input, INPUT_SIZE);
     // Serial.println(input);
      
    ParseCommand();
    ExecuteCommand();
    
//         if(Serial.available() > 0)
//        {
//            cmd = int(Serial.read());
//            Serial.println(cmd);
//        }
}


////////////////////////////////// FUNCTIONS NOT COMMITTED YET //////////////////////////////////

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

void ManualControl()
{  
    managed = false;
    while(true)  
    {
        //ReadLineSensors();
        //AssertCourse();
        if(Serial.available() > 0)
        {
            cmd = int(Serial.read());
            //Serial.println(cmd);
        }
        if(cmd == 120) //x
        {
            Stop();
            //Serial.println("x");
        }
        else if (cmd == 119) //w
        {
            Forward();
            //Serial.println("w");
        }
        else if (cmd == 115) //s
        {
            Backward();
            //Serial.println("s");
        }
        else if (cmd == 97) //a
        {
            Left(195);
            //Serial.println("a");
        }
        else if (cmd == 100) //d
        {
            Right(195);
            //Serial.println("d");
        }
        else if(cmd == 118) //v
        {
            CheckVoltage();
            cmd = 120;
            //Serial.println("v");
        }
        else if(cmd == 114) //r
        {
            ReadLineSensors();
            Serial.print(readings[0]); Serial.print("\t"); Serial.print(readings[1]); Serial.print("\t"); Serial.println(readings[2]);
            cmd = 120;  
            
        }
        else if(cmd == 113) //q
        {
            managed = true;
            break;
        }
        else
        {
            Stop();
        }
    }
}

//1-3_4-90_1-2_*













//1-2_3-90_1-1_3-90_1-2_3-90_1-1_*
