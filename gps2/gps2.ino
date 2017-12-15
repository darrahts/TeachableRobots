#include <EEPROM.h>


/************************************************************************************************************/
/*                                                                      VARIABLES                           */
/************************************************************************************************************/

//used to match the nmea header i.e. GPRMC
int header[5] = {0,0,0,0,0};

//hex (byte) value of GPRMC
int match[5] = {71,80,82,77,67};

//contains one reading 
String data = "";

//largest bounding boxes of known location in format {minLat, maxLat, minLon, maxLon}
float knownLocations[8][4] = { {0,0,0,0}, //HINT: USE YOUR OWN LOCATIONS
                               {0,0,0,0},
                               {0,0,0,0},
                               {0,0,0,0},
                               {0,0,0,0},
                               {0,0,0,0},
                               };

//checks if gps is at a new location or known location, used for logic in saving the data
bool newLocation = true;

//nmea string gives 'A' for valid and 'V' for invalid
bool valid = false;

//number of parsed data points in the string, may vary depending on nmea sentence type
String dataPoints[12];

//used for conversion
char floatBuffer[64];

//used for timer functionality with reading frequency
unsigned long t1 = millis();
unsigned long t2 = millis();

//time between polling the gps in ms
unsigned long delayTime = 1800000L;
//unsigned long delayTime = 60000L;

//start of the memory address, memAdr = 0 : value of next memAdr, persistant through power cycles
//2 = atLoc_1, 4 = atLoc_2, 6 = atLoc_3, 8 = atLoc_4, 10 = atLoc_5, 12 = atLoc_6
int memAdr = 14;

//values of interest that are stored in eeprom
byte hour;
byte day;
float lat;
float lon;

//struct that holds the values of interest
struct DataLine
{
    byte _hour;
    byte _day;
    float _lat;
    float _lon;
};

// 3 readings are taken at a time (1 second apart)
DataLine lines[3];

//number of readings that occur at the locations of interest
byte atLoc_1 = 0;
byte atLoc_2 = 0;
byte atLoc_3 = 0;
byte atLoc_4 = 0;
byte atLoc_5 = 0;
byte atLoc_6 = 0;



/************************************************************************************************************/
//$GPRMC,200215.00,A,3608.71203,N,08647.59642,W,0.362,82.71,131117,,,A*4C
//       hour     valid     lat          long     speed       date
/************************************************************************************************************/

/*
 *  FUNCTIONS (and line number)
 *  
 *  - Run() . . . . . . . . . . . . . . . . . . . . 117
 *  - ReadGPS() . . . . . . . . . . . . . . . . . . 156
 *  - Parse() . . . . . . . . . . . . . . . . . . . 213
 *  - ProcessData() . . . . . . . . . . . . . . . . 244
 *  - CountKnownLocations(latAvg, lonAvg) . . . . . 294
 *  - LoadData(printLog). . . . . . . . . . . . . . 349
 *  - SaveData(). . . . . . . . . . . . . . . . . . 397
 *  - ClearEEPROM(startAdr, endAdr) . . . . . . . .  
 *  - SaveIntEEPROM(startAdr, val). . . . . . . . .
 *  - LoadIntEEPROM(startAdr) . . . . . . . . . . .
 *  - setup() . . . . . . . . . . . . . . . . . . .
 *  - loop(). . . . . . . . . . . . . . . . . . . .
 *  - PrintString(raw). . . . . . . . . . . . . . .
 *  - Compare() . . . . . . . . . . . . . . . . . . 
 *  - GetFloat(i) . . . . . . . . . . . . . . . . . 
 */


/************************************************************************************************************/
/*                                                                 CORE FUNCTIONS                           */
/************************************************************************************************************/
/*
 *                                      These are the core gps data handling functions
 *                                      
 *                                      - Run()
 *                                      - ReadGPS()
 *                                      - Parse()
 *                                      - ProcessData()
 */
/************************************************************************************************************/
/*                                                                    RUN                                   */
void Run()
{
    //Serial.println("running.");
    int retryCounter = 0;
    for(int i = 0; i < 3; i++)
    {
        ReadGPS();
       // Serial.println("read gps.");
        if(valid)
        {
            lines[i] = {hour, day, lat, lon};
            delay(2000);
            //PrintString(false);
        }
        else 
        {
          //Serial.println("data not valid.");
          //PrintString(true);
          //stay in the for loop to keep trying for a valid reading
          i--;
          retryCounter++;
          delay(1000);
        }
        if(retryCounter > 10)
        {
            //Serial.println("couldn't poll gps.");
            break;
        }            
    
    }
    if(valid)
    {
        SaveData();
        //if(SaveData()) Serial.println("Saved");
    }
}

/************************************************************************************************************/
/*                                                                  READ GPS                                */
bool ReadGPS()
{
    valid = true;
    int counter = 0;
    while(true)
    {
        counter++;
        delay(5);
        int val = Serial1.read();
        //Serial.println(val);
        if(val == 36)
        {
     //     Serial.println("found start of string.");
          delay(5);
           for(int i = 0; i < 5; i ++)
           {
              header[i] = Serial1.read();
              delay(5);
           }
       //    Serial.println("comparing header");
           if(Compare())
           {
     //         Serial.println("header match!");
              delay(5);
             int x = Serial1.read();
             while(x != 10 && x != 36 && x != int('*') && x != -1)
             {
                counter++;
                data += char(x);
                delay(5);
                x = Serial1.read();
                if(counter == 500)
                {
                    valid = false;
                    break;
                }
             }
      //       Serial.println("received data string.");
             if(valid) Parse();
      //       Serial.println("parsed.");
             if(valid) ProcessData();
      //       Serial.println("processed.");
             data = "";
             break;
           }
        }
        if(counter == 500)
        {
            valid = false;
            return false;
        }
    }
    return true;
}

/************************************************************************************************************/
/*                                                                  PARSE                                   */
bool Parse()
{
      //clear old data values
      for(int i = 0; i < 12; i++)
      {
          dataPoints[i] = "";
      }
      int k = 0;
      if(data.length() < 50 && data.length() > 83)
      {
          valid = false;
          return false;
      }
      
      for(int i = 1; i < data.length(); i++)
      {
          //Serial.println("in loop.");
          if(data[i] != ',')
          {
              dataPoints[k] += data[i];
          }
          else
          {
              k++;
          }
      }   
      return true;
}

/************************************************************************************************************/
/*                                                               PROCESS DATA                               */
bool ProcessData()
{
      //nmea standard A = valid, V = invalid
      if(dataPoints[1] != "A")
      {
          valid = false;
          return false;
      }
      float v = GetFloat(6);
      if(v > 10)
      {
          valid = false;
          return false;
      }
      else
      {
          valid = true;
          float t = GetFloat(0);
          
          //time in format hhmmss
          hour = byte(t / 10000);
          if(hour > 24)
          {
              hour = hour - 24;
          }
          
          lat = GetFloat(2);
          lon = GetFloat(4);
          
          //date in format ddmmyy
          day = byte(GetFloat(8)/10000);
      }
      return true;
}


/************************************************************************************************************/
/*                                                               EEPROM FUNCTIONS                           */
/************************************************************************************************************/
/*
 *                                  these functions interact with the eeprom with
 *                                  
 *                                  - LoadData()
 *                                  - SaveData()
 *                                  - SaveIntEEPROM()
 *                                  - LoadIntEEPROM()
 */

/************************************************************************************************************/
/*                                                               COUNT LOCATIONS                            */
void CountKnownLocations(float latAvg, float lonAvg)
{
      newLocation = true;
      for(int i = 0; i < 8; i++)
      {
           if(latAvg > knownLocations[i][0] && latAvg < knownLocations[i][1] && lonAvg > knownLocations[i][2] && lonAvg < knownLocations[i][3])
          {
              if(i == 0) 
              {
                  atLoc_1 += 1;
        //          Serial.print("at loc1   ");
         //         Serial.println(atLoc_1);
              }
               if(i == 1) 
              {
                  atLoc_2 += 1;
          //        Serial.println("at loc2");
              }
               if(i == 2) 
              {
                  atLoc_3 += 1;
           //       Serial.println("at loc3");
              }
               if(i == 3) 
              {
                  atLoc_4 += 1;
            //      Serial.println("at loc4");
              }
               if(i == 4) 
              {
                  atLoc_4 += 1;
            //      Serial.println("at loc4");
              }
               if(i == 5) 
              {
                  atLoc_4 += 1;
            //      Serial.println("at loc4");
              }
               if(i == 6) 
              {
                  atLoc_5 += 1;
            //      Serial.println("at loc5");
              }
               if(i == 7) 
              {
                  atLoc_6 += 1;
             //     Serial.println("at loc6");
              }
              newLocation = false;
          }
      }
}
 
/************************************************************************************************************/
/*                                                                LOAD DATA                                 */
void LoadData(bool printLogs)
{
    atLoc_1 = LoadIntEEPROM(2);
    atLoc_2 = LoadIntEEPROM(4);
    atLoc_3 = LoadIntEEPROM(6);
    atLoc_4 = LoadIntEEPROM(8);
    atLoc_5 = LoadIntEEPROM(10);
    atLoc_6 = LoadIntEEPROM(12);
    

    if(printLogs)
    {
        Serial.println(atLoc_1);
        Serial.println(atLoc_2);
        Serial.println(atLoc_3);
        Serial.println(atLoc_4);
        Serial.println(atLoc_5);
        Serial.println(atLoc_6);
        memAdr = 14;
        for(int i = 0; i < 4095; i++)
        {
              EEPROM.get(memAdr, hour);
              memAdr += 1;
              EEPROM.get(memAdr, day);
              memAdr += 1;
              EEPROM.get(memAdr, lat);
              memAdr += 4;
              EEPROM.get(memAdr, lon);
              memAdr += 4;
    
              if(day <= 0)
              {
                  break;
              }
              else
              {
                  Serial.print(hour); Serial.print(" ");
                  Serial.print(day);  Serial.print(" ");
                  Serial.print(lat);  Serial.print(" ");
                  Serial.print(lon);  Serial.println();             
              }
        }
    }
}

/************************************************************************************************************/
/*                                                                SAVE DATA                                 */

bool SaveData()
{
      float latAvg = 0.0f;
      float lonAvg = 0.0f;
      bool writeIt = false;

      //if the hours and day reading are valid
      if(lines[0]._hour >=0 && lines[0]._hour < 24 && lines[0]._day >=1 && lines[0]._day <=31)
      {
          writeIt = true;
      }
      else return false;
      
      for(int i = 0; i < 3; i++)
      {
          //if the lat and lon readings are valid (i.e. in this case, bounding box > TN
          if(lines[i]._lat > 3300 && lines[i]._lat < 3800 && lines[i]._lon > 8000 && lines[i]._lon < 9100)
          {
              writeIt = true;
              latAvg += lines[i]._lat;
              lonAvg += lines[i]._lon;
          }
          if(writeIt == false) return false;
      }

      if(writeIt)
      {
          latAvg /= 3;
          lonAvg /= 3;
          
          CountKnownLocations(latAvg, lonAvg);

          if(newLocation)
          {
              EEPROM.put(memAdr, lines[0]._hour);
              memAdr += 1;
              EEPROM.put(memAdr, lines[0]._day);
              memAdr += 1;
              EEPROM.put(memAdr, latAvg);
              memAdr += 4;
              EEPROM.put(memAdr, lonAvg);
              memAdr += 4;         
          }
          else
          {
              //increase counter for known locations
              if(atLoc_1 != LoadIntEEPROM(2)) SaveIntEEPROM(2, atLoc_1);
              else if(atLoc_2 != LoadIntEEPROM(4)) SaveIntEEPROM(4, atLoc_2);
              else if(atLoc_3 != LoadIntEEPROM(6)) SaveIntEEPROM(6, atLoc_3);
              else if(atLoc_4 != LoadIntEEPROM(8)) SaveIntEEPROM(8, atLoc_4);
              else if(atLoc_5 != LoadIntEEPROM(10)) SaveIntEEPROM(10, atLoc_5);
              else if(atLoc_6 != LoadIntEEPROM(12)) SaveIntEEPROM(12, atLoc_6);
          }
          SaveIntEEPROM(0, memAdr);
      }
      return true;
}

/************************************************************************************************************/
/*                                                                 CLEAR EEPROM                             */
void ClearEEPROM(int startAdr, int endAdr)
{
    for(int i = startAdr; i <= endAdr; i++)
    {
        if(EEPROM.read(i) != '\0')
        {
            EEPROM.write(i, '\0');
        }
    }
}



/************************************************************************************************************/
/*                                                                   WRITE INT                              */
void SaveIntEEPROM(int startAdr, int val)
 {
     byte low = ((val >> 0) & 0xFF);
     byte high = ((val >> 8) & 0xFF);

     EEPROM.write(startAdr, low);
     EEPROM.write(startAdr + 1, high);
 }

/************************************************************************************************************/
/*                                                                    READ INT                              */
unsigned int LoadIntEEPROM(int startAdr)
{
    byte low = EEPROM.read(startAdr);
    byte high = EEPROM.read(startAdr + 1);
    
    return ((low << 0) & 0xFF) + ((high << 8) & 0xFF00);
}


/************************************************************************************************************/
/*                                                                  SETUP                                   */
/************************************************************************************************************/


void setup() 
{
    //these two lines reset the logs and counter
    //DO NOT UNCOMMENT THEM UNLESS YOU ARE DELETING THE LOGS!!!
    //to clear: uncomment, then 
    //ClearEEPROM(0,4095);
    //SaveIntEEPROM(0, 14);
    Serial.begin(9600);
    Serial1.begin(9600);
    LoadData(true); //loads previous known location information
    
    memAdr = LoadIntEEPROM(0);
    Serial.print("memAdr: ");
    Serial.println(memAdr);
    Serial.println();
}


/************************************************************************************************************/
/*                                                                  MAIN                                    */
/************************************************************************************************************/

void Main()
{
    t2 = millis();
    if((t2 - t1) > delayTime)
    {
        t1 = t2;
   //     Serial.print(delayTime / 60000L);
   //     Serial.println(" minutes");
        Run();
    }
    else
    {
        delay((1000 * 60 * 5));
        ClearStream();
    }
 //   Serial.println("main loop.");
}

void loop() 
{   
    //QueryGPS();
    Main();
}



/************************************************************************************************************/
/*                                                          HELPER FUNCTIONS                                */
/************************************************************************************************************/

void PrintString(bool raw)
{
    if(raw)
    {
         for(int i = 0; i < 12; i++)
         {
              Serial.print(dataPoints[i]);
              Serial.print(" ");
         }
         Serial.println();
    }
    else
    {
        Serial.print(hour);
        Serial.print(" ");
        Serial.print(day);
        Serial.print(" ");
        Serial.print(lat);
        Serial.print(" ");
        Serial.println(lon);
    }
}

bool Compare()
{
    for(int i = 0; i < 5; i++)
    {
        if(header[i] != match[i])
        {
            return false;
        }
    }
    return true;
}

float GetFloat(int i)
{
      for(int j = 0; j < 64; j++)
      {
          floatBuffer[j] = '\0';
      }
      dataPoints[i].toCharArray(floatBuffer, sizeof(floatBuffer));
      return atof(floatBuffer);
}

void test2()
{
        while(Serial1.available() > 0)
    {
        Serial.print(Serial1.read());
        Serial.print(" ");
    }
}

void QueryGPS()
{
    while(Serial1.available() > 0)
    {
      int x = Serial1.read();
      data += char(x); 
    }
    Serial.print(data);
    data = "";
}

void ClearStream()
{
    while(Serial1.available() > 0)
    {
        Serial1.read();
    }
}
