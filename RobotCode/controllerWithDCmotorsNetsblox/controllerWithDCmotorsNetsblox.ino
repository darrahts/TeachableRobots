
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
//size of input / command sequence
#define INPUT_SIZE 512
#define SEQUENCE_LENGTH 60

//min and max velocity vals (input)
const int minV = 0;
const int maxV = 20;

//min and max motor speed vals
const int minS = 90;
const int maxS = 150;
 
/********************************************************************************************************
 *                                             GLOBAL VARIABLES                                         *                                                  
 ********************************************************************************************************/
//current speed in range [minV, maxV]
int curSpd = 0;
int prevSpd = 0;

//current motor val in range [minS, maxS]
int curVal = 0; 
int prevVal = 0;

//current direction (-1 or 5/stop, 1/forward, 2/backward, 3/turningleft, 4/turningright)
int curDir = -1; 
int prevDir = -1;

//IR baseline readings. adjust these to your sensors and environment
int readings[] = {500,400,700};

//holds the input received from serial
char input[INPUT_SIZE];

//holds the command and amounts for the current executing sequence
int commands[SEQUENCE_LENGTH];
int amounts[SEQUENCE_LENGTH];

//whether to execute the command/sequence or not
bool execute = true;

//battery voltage
double voltage = 0.0;

//scaling for left/right motor differences
double scale = 0.0;

//whether manual control (netsblox, keyboard, etc) or not (using grid)
bool manual = false;

/********************************************************************************************************
 *                                                  FUNCTIONS                                           *
 ********************************************************************************************************/

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
}

/*                            CHECK VOLTAGE          
 *        Reads the VIN voltage (i.e. direct from battery)
 *        5.5 is an approximation from the voltage divider
 *        analog read gives 0-1024 so need to divide by 1024
 *        10500 = r1 + r2     1500 = r2
 */
void CheckVoltage()
{
    double v = (analogRead(VOLTAGE_SR) * 5.0) / 1024.0;
    voltage = (v * 10500.0 / 1500.0);
    Serial.write('~');
    delay(50);
    Serial.println(voltage);
}


/*                            MANUAL CONTROL          
 *          executes a single command at a time from serial.
 *          w = forward
 *          s = backward
 *          x = stop
 *          a = left
 *          d = right
 *          q = exit manual control
 *          z = dummy 
 */
void ManualControl()
{  
    int cmd = -1;
    manual = true;
    int val = 6; //speed val
    
    while(manual)  
    {
        //ReadLineSensors();
        //AssertCourse();
        if(Serial.available() > 0)
        {
            cmd = int(Serial.read());
            Serial.println(cmd);

            if(cmd == 120) //x
            {
                Stop();
                Serial.write('x');    
            }
            else if (cmd == 119) //w
            {
                Serial.write('w');
                if(prevDir == 1) 
                {  
                    val += 2;
                    Drive(val, 1);  
                }
                else
                {
                    val = 6;
                    Drive(val, 1); 
                }             
            }
            else if (cmd == 115) //s
            {
                Serial.write('s');
                if(prevDir == 2) 
                {  
                    val += 2;
                    Drive(val, 2);  
                }
                else
                {
                    val = 6;
                    Drive(val, 2);
                }              
            }
            else if (cmd == 97) //a
            {
                Serial.write('a');
                Turn(3, 15, 0);
                Drive(curSpd, prevDir);
            }
            else if (cmd == 100) //d
            {
                Serial.write('d');
                Turn(4, 15, 0);
                Drive(curSpd, prevDir);                
            }
            else if(cmd == 113) //q
            {
                manual = false;
                //Serial.write('q');
            }
            else if(cmd == 122) //z dime left
            {
                Turn(3, 0, 1);
            }
            else if(cmd == 99) //c dime right
            {
                Turn(4, 180, 1);
            }
            else
            {
                Stop();
                //Serial.write('u');
            }
        }
    }
}

/*                            Netsblox CONTROL          
 *
 */
void NetsbloxControl()
{  // Serial.flush();
    delay(250);
    Serial.write('N');
    delay(250);
  //  Serial.flush();
    char cmd = 0x00;
    manual = true;
    int val = 0; //speed val
    
    char inB = 0x00;
    int args[] = {0, 0, 0, 0, 0};
    int in = 0;
    uint8_t i = 0;
    bool flag = false;
    
    while(manual)  
    {
        //ReadLineSensors();
        //AssertCourse();
       // while(!Serial.available()) ; //*
        if(Serial.available() > 0)
        {
            for(int k = 0; k < 5; k++)
            {
                args[k] = 0;
            }
            i = 0;
            in = 0;
            while(true)
            {
                while(!Serial.available()) ;
                inB = Serial.read();
                //Serial.print("new: ");
                //Serial.println(inB);
                if(inB == 'n')
                {
                   // Serial.println("end");
                    flag = true;
                    Serial.flush();
                    break;
                }   
                if(inB == 0x20) //space
                {
                    i++;
                    continue;
                }
                if(inB == -1) continue;
                args[i] *= 10;
                args[i] = ((inB -48) + args[i]);
            }
            //Serial.println(in);
//            for(int j = 0; j < 5; j++)
//            {
//                Serial.println(args[j]);
//            }
        }
        
        if(flag)
        {
            Serial.flush();
            delay(5);
            if(args[0] == 5) 
            {
                Stop();
                Serial.write('x');    
            }
            else if (args[0] == 1)
            {
                Serial.write('w');
                Drive(args[1], args[0]); 
            }
            else if (args[0] == 2)
            {
                Serial.write('s');
                Drive(args[1], args[0]);             
            }
            else if (args[0] == 3) 
            {
                Serial.write('a');
                Turn(args[0],args[1],args[2]);
                Drive(curSpd, prevDir);
            }
            else if (args[0] == 4)
            {
                Serial.write('d');
                Turn(args[0], args[1], args[2]);
                Drive(curSpd, prevDir);                
            }
            else if(args[0] == 9)
            {
                manual = false;
                Serial.write('q');
            }
            else if(args[0] == 6)
            {
                CheckVoltage();
                //Serial.println(voltage);
            }
            else if(args[0] == 7)
            {
                ReadLineSensors();
                Serial.write(0x7E);
                delay(30);
                Serial.print(readings[0]); Serial.print(" "); Serial.print(readings[1]); Serial.print(" "); Serial.println(readings[2]);
            }
            else
            {
                Stop();
                //Serial.write('u');
            }
            flag = false;
        }
    }
}

void ParseCommand()
{    
    //Serial.println("checking");
    //check if theres anything in the stream
    if(Serial.available())
    {
        //Serial.println("available!");
        //read the stream into the input variable and returns
        //the number of bytes to size_
        byte size_ = Serial.readBytes(input, INPUT_SIZE);
        
        if(size_ == 2 && input[0] == 0x6D) //m for manual
        {
            if(input[1] == 0x6D) //m for ManualMode, same as 109
            {
                Serial.write(0x6D);
                ManualControl();
            }
            if(input[1] == 0x6E) //n for netsblox control
            {
                Serial.write(0x6E);
                NetsbloxControl();
            }
            if(input[1] == 0x76) //v for CheckVoltage, same as 118
            {
                //Serial.write(0x7E);
                CheckVoltage();
                Serial.println(voltage);
                //Serial.write(0x76);
            }
            if(input[1] == 114) //r for ReadLineSensors, same as 0x72
            {
                ReadLineSensors();
                Serial.write(0x7E);
                delay(30);
                Serial.print(readings[0]); Serial.print("\t"); Serial.print(readings[1]); Serial.print("\t"); Serial.println(readings[2]);
            }
            if(input[1] == 115) //s for SaveParameters, same as 0x73
            {
                Serial.println("save params"); //SaveParameters();
                Serial.write(0x73);
            }
            if(input[1] == 'l') //l for LoadParameters
            {
                Serial.println("load params"); //LoadParameters();
            }
            if(input[1] == 'd') //d for display parameters (ShowParameters())
            {
                Serial.println("show params"); //ShowParameters();
            }
            if(input[1] == 'p')
            {
                Serial.println("dummy");
            }
            execute = false;
            input[0] = -1;
            input[1] = -1;
        }
        else if(size_ > 2 && input[0] == 0x53) //s for sequence
        {
            execute = true;
        }
        else
        {
            execute = false;
        }
        //Serial.println(input[0]);
        // Add the final 0 to end of the input string
        input[size_] = 0;
        //Serial.println(input);

        //counters for the commands and amounts
        int c = 0;
        int a = 0;
        
        // Read each command pair 
        char* command = strtok(input, "_");
        
        while (execute && command != 0)
        {
            // Split the input command in two values (command and amount)
            char* separator = strchr(command, '-');
            if (separator != 0)
            {
                //split the string in 2: replace '_' with 0
                *separator = 0;
                
                //put the command in the commands array at the same
                //index as the corresponding amount
                int next = atoi(command);
                //Serial.println(next);
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
         commands[c] = 5; //5 bc ExecuteCommand() calls Stop() with 5 
         amounts[a] = 0;
    }
}


/*
 * converts degrees to delay time
 * @param dime: if dime turn 1 or 0
 * @param deg: degrees from 0 to 180, step 5
 */
 //TODO fix dime equation, not enough delay, doesnt account for speed
int DegToDelay(bool dime, int deg)
{
    int d = 1;
    if(dime)
    {
        if(curSpd > 0)
        {
            return(int(abs(deg+5)*(15/curSpd) + 40));
        }
        else
        {
            return(int(abs(deg+5)*1.4 + 40));
            d = 20;
        }
    }
    else
    {
      //int d = abs(deg+5)*(112/curSpd);
      //Serial.println(d);
      if(curSpd > 0)
      {
          return abs(deg)*(112/curSpd);
      }
      else
      {
          return abs(deg)*2.5 + 60;
      }
    }
}


/*                                                   MOTORS                                       *                                                  
 ********************************************************************************************************/


//********************************************************* STOP
/*                                 
 * turns off the motors
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
    prevDir = curDir;
    curDir = -1;
    curVal = 0; 
}

//********************************************************* RAMP
/*
 * gradually increases speed of motors
 * @param i: velocity counter
 * @param c: 0 starts motors
 * @param d: 1 for forward, 2 for backward
 */
void Ramp(int i, int c, int d)
{
    CheckVoltage();
    curVal = 90+3*i;
    scale = curVal - ((voltage*10)/3.75) + 2;
    if(d == 1)
    {
        analogWrite(MTR_A_EN, curVal);
        analogWrite(MTR_B_EN, int(scale - 1));
    }
    else if(d == 2)
    {
        analogWrite(MTR_A_EN, int(curVal*1.04));
        analogWrite(MTR_B_EN, int(scale - 1));
    }      
    delay(35);
    
    if(c < 2 && curDir == -1)
    {
        if(d == 1) //forward
        {
            analogWrite(MTR_A_EN, 80);
            digitalWrite(MTR_B_A, HIGH);
            digitalWrite(MTR_B_B, LOW);
            digitalWrite(MTR_A_A, HIGH);
            digitalWrite(MTR_A_B, LOW);
        }
        else if(d == 2) //backward
        {
            analogWrite(MTR_A_EN, 85);
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
    if(curDir != -1 && curDir != 3 && curDir != 4 && curDir != dir)
    {
        Stop();
        //Serial.println(prevDir);
        if(prevDir == 2) {  delay(200);  }
    }
    

    //increasing speed or same
    if((curDir == -1 || curDir == dir || curDir == 3 || curDir == 4) && velocity >= curSpd) 
    {
        //Serial.print("increasing");
        for(int i = curSpd; i <= velocity; i++)
        {
            Ramp(i, c, dir);
            c++;
        }
    }

    //decreasing speed
    else if((curDir == -1 || curDir == dir  || curDir == 3 || curDir == 4) && velocity <= curSpd)
    {
    //    Serial.println("decreasing.");
        for(int i = curSpd; i >= velocity; i--)
        {
            Ramp(i, c, dir);
            c++; 
        }
    }
    
    else
    {
      //  Serial.println("stopping");
        Stop();
    }
    prevSpd = curSpd;
    curSpd = velocity;
    prevDir = curDir;
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

    if(!dime && dir != 3 && dir != 4 && (deg < 1 || deg > 180) && deg % 5 != 0 && deg == 0)
    {
        Serial.println("bad turn1.");
        return; 
    }
    
    if(dime || curVal == 0)
    {
        if(dir == 3) //left
        {
            //Serial.println("here");
            analogWrite(MTR_B_EN, 100);
            analogWrite(MTR_A_EN, 100);
            digitalWrite(MTR_B_B, HIGH);
            digitalWrite(MTR_B_A, LOW);
            digitalWrite(MTR_A_A, HIGH);
            digitalWrite(MTR_A_B, LOW);
            //delay(300);//
            delay(DegToDelay(1, deg));
            if(deg != 0 && curDir == -1) { Serial.println("stop"); Stop(); }
            else
            {
                Serial.print("deg: "); Serial.println(deg);
                Serial.print("dir: "); Serial.println(curDir);
            }
        }

        else if(dir == 4) //right
        {
            analogWrite(MTR_B_EN, 100);
            analogWrite(MTR_A_EN, 100);
            digitalWrite(MTR_B_A, HIGH);
            digitalWrite(MTR_B_B, LOW);
            digitalWrite(MTR_A_B, HIGH);
            digitalWrite(MTR_A_A, LOW);
            delay(DegToDelay(1, deg));
            if(deg != 0 && curDir == -1) { Stop(); }
        }
        
        else
        {
            Serial.println("bad turn2.");
        }
    }
    
    else if(curVal != 0 && curDir == 1 && dir == 3) //forward and left
    {
         // Serial.println("left");
          int r = ((curVal*1.2 < 150) ? curVal*1.2 : 150);
          analogWrite(MTR_B_EN, 70 );
          analogWrite(MTR_A_EN, r);
          digitalWrite(MTR_B_A, HIGH);
          digitalWrite(MTR_B_B, LOW);
          digitalWrite(MTR_A_A, HIGH);
          digitalWrite(MTR_A_B, LOW); 
          delay(DegToDelay(0, deg));
          analogWrite(MTR_B_EN, curVal*1.10);
          analogWrite(MTR_A_EN, curVal);
          prevDir = curDir;
          curDir = 3;
    }
    
    else if(curVal != 0 && curDir == 1 && dir == 4) //forward and right
    {
         // Serial.println("right");
          int l = ((curVal*1.01 < 150) ? curVal*1.01 : 150);
          analogWrite(MTR_B_EN,  l);
          analogWrite(MTR_A_EN, 80);
          digitalWrite(MTR_B_A, HIGH);
          digitalWrite(MTR_B_B, LOW);
          digitalWrite(MTR_A_A, HIGH);
          digitalWrite(MTR_A_B, LOW); 
          delay(DegToDelay(0, deg));
          analogWrite(MTR_A_EN, curVal*1.10);
          analogWrite(MTR_B_EN, curVal);
          prevDir = curDir;
          curDir = 4;
    }
    
    else if(curVal != 0 && curDir == 2 && dir == 3) //backward and left
    {
          //Serial.println("left");
          int r = ((curVal*1.2 < 150) ? curVal*1.2 : 150);
          analogWrite(MTR_B_EN, 70 );
          analogWrite(MTR_A_EN, r);
          digitalWrite(MTR_B_B, HIGH);
          digitalWrite(MTR_B_A, LOW);
          digitalWrite(MTR_A_B, HIGH);
          digitalWrite(MTR_A_A, LOW); 
          delay(DegToDelay(0, deg));
          analogWrite(MTR_B_EN, curVal*1.10);
          analogWrite(MTR_A_EN, curVal);
          prevDir = curDir;
          curDir = 3;
    }
    
    else if(curVal != 0 && curDir == 2 && dir == 4) //backward and right
    {
         // Serial.println("right");
          int l = ((curVal*1.01 < 150) ? curVal*1.01 : 150);
          analogWrite(MTR_B_EN,  (l - 10));
          analogWrite(MTR_A_EN, 80);
          digitalWrite(MTR_B_B, HIGH);
          digitalWrite(MTR_B_A, LOW);
          digitalWrite(MTR_A_B, HIGH);
          digitalWrite(MTR_A_A, LOW); 
          delay(DegToDelay(0, deg));
          analogWrite(MTR_A_EN, curVal*1.10);
          analogWrite(MTR_B_EN, curVal);
          prevDir = curDir;
          curDir = 4;
    }
}


/********************************************************************************************************
 *                                               SETUP                                                  *                                                  
 ********************************************************************************************************/
void setup() 
{
 
    //enable the serial port
    Serial.begin(38400);
  
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
  Serial.flush();
  delay(50);
  NetsbloxControl();
   // ParseCommand();
 //Drive(10, 1);
   // test();
   // delay(200);
  //  Drive(12, 2);
   // delay(3000);
   // Drive(7, 1);
   // delay(1000);
  //   Stop();
  //  delay(5000);
  
}

void test()
{
    Drive(10, 1);
    delay(900);
    Turn(3, 45, 0);
    Drive(10, 1);
    delay(900);
    Turn(4, 45, 0);
    Drive(10, 1);
    delay(900);
}















