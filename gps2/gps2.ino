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
float knownLocations[8][4] = { {3608.86,3608.89,8638.29,8638.32}, //Loc_1
                               {3614.03,3614.09,8670.33,8670.40}, //Loc_2
                               {3618.33,3618.46,8677.83,8677.93}, //Loc_3
                               {3617.01,3617.15,8667.83,8667.96}, //Loc_4
                               {3618.11,3618.24,8660.48,8660.73}, //Loc_4
                               {3621.56,3621.63,8660.27,8660.47}, //Loc_4
                               {3621.58,3621.72,8659.84,8660.00}, //Loc_5
                               {3619.04,3619.10,8662.78,8662.88}  //Loc_6
                               };

//if the nmea string contains A (instead of V)


//number of parsed data points in the string, may vary depending on nmea sentence type
String dataPoints[12];

//used for conversion
char floatBuffer[64];

//used for timer functionality with reading frequency
long t1 = millis();
long t2 = millis();

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
    int retryCounter = 0;
    int delayTime = 60000;
    t2 = millis();
    if(t2 - t1 > delayTime)
    {
        t1 = t2;
        for(int i = 0; i < 3; i++)
        {
            ReadGPS();
            if(valid)
            {
                lines[i] = {hour, day, lat, lon};
                delay(1000);    
            }
            else 
            {
              Serial.println("data not valid.");
              PrintString(true);
              //stay in the for loop to keep trying for a valid reading
              i--;
              retryCounter++;
            }
            if(retryCounter > 10)
            {
                break;
            }
        }
        if(valid)
        {
            if(SaveData()) Serial.print("Saved");
        }
    }
}

/************************************************************************************************************/
/*                                                                  READ GPS                                */
void ReadGPS()
{
    while(true)
    {
        if(Serial1.read() == 36)
        {
          delay(3);
           for(int i = 0; i < 5; i ++)
           {
              header[i] = Serial1.read();
              delay(3);
           }
           if(Compare())
           {
              delay(3);
             int x = Serial1.read();
             while(x != 10)
             {
                data += char(x);
                delay(3);
                x = Serial1.read();
             }
             Parse();
             ProcessData();
             data = "";
             break;
           }
        }
        
    }
}

/************************************************************************************************************/
/*                                                                  PARSE                                   */
void Parse()
{
      //clear old data values
      for(int i = 0; i < 12; i++)
      {
          dataPoints[i] = "";
      }
      int k = 0;
      for(int i = 1; i < data.length(); i++)
      {
          if(data[i] != ',')
          {
              dataPoints[k] += data[i];
          }
          else
          {
              k++;
          }
      }   
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
 for(int i = 0; i < 8; i++)
      {
           if(latAvg > knownLocations[i][0] && latAvg < knownLocations[i][1] && lonAvg > knownLocations[i][2] && lonAvg < knownLocations[i][3])
          {
              if(i == 0) 
              {
                  atLoc_1 += 1;
                  Serial.println("at loc1");
              }
               if(i == 1) 
              {
                  atLoc_2 += 1;
                  Serial.println("at loc2");
              }
               if(i == 2) 
              {
                  atLoc_3 += 1;
                  Serial.println("at loc3");
              }
               if(i == 3) 
              {
                  atLoc_4 += 1;
                  Serial.println("at loc4");
              }
               if(i == 4) 
              {
                  atLoc_4 += 1;
                  Serial.println("at loc4");
              }
               if(i == 5) 
              {
                  atLoc_4 += 1;
                  Serial.println("at loc4");
              }
               if(i == 6) 
              {
                  atLoc_5 += 1;
                  Serial.println("at loc5");
              }
               if(i == 7) 
              {
                  atLoc_6 += 1;
                  Serial.println("at loc6");
              }
          }
      }
}
 
/************************************************************************************************************/
/*                                                                LOAD DATA                                 */
void LoadData()
{
    atLoc_1 = LoadIntEEPROM(2);
    atLoc_2 = LoadIntEEPROM(4);
    atLoc_3 = LoadIntEEPROM(6);
    atLoc_4 = LoadIntEEPROM(8);
    atLoc_5 = LoadIntEEPROM(10);
    atLoc_6 = LoadIntEEPROM(12);

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

          //increase counter for known locations
          if(atLoc_1 != LoadIntEEPROM(2)) SaveIntEEPROM(2, atLoc_1);
          if(atLoc_2 != LoadIntEEPROM(4)) SaveIntEEPROM(4, atLoc_2);
          if(atLoc_3 != LoadIntEEPROM(6)) SaveIntEEPROM(6, atLoc_3);
          if(atLoc_4 != LoadIntEEPROM(8)) SaveIntEEPROM(8, atLoc_4);
          if(atLoc_5 != LoadIntEEPROM(10)) SaveIntEEPROM(10, atLoc_5);
          if(atLoc_6 != LoadIntEEPROM(12)) SaveIntEEPROM(12, atLoc_6);
          
          
          EEPROM.put(memAdr, lines[0]._hour);
          memAdr += 1;
          EEPROM.put(memAdr, lines[0]._day);
          memAdr += 1;
          EEPROM.put(memAdr, latAvg);
          memAdr += 4;
          EEPROM.put(memAdr, lonAvg);
          memAdr += 4;
          Serial.print(lines[0]._hour); 
          Serial.print(" ");
          Serial.print(lines[0]._day); 
          Serial.print(" ");
          Serial.print(latAvg); 
          Serial.print(" ");
          Serial.print(lonAvg); 
          Serial.println();

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
        EEPROM.write(i, '\0');
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
    //ClearEEPROM(14, 4095);
    //SaveIntEEPROM(0, 14);
    
    Serial.begin(9600);
    Serial1.begin(9600);
    memAdr = LoadIntEEPROM(0);
    Serial.println();
    Serial.println(memAdr);
    Serial.println();
}


/************************************************************************************************************/
/*                                                                  LOOP                                    */
/************************************************************************************************************/


void loop() 
{   
    //LoadData();
    //while(true) {}
    Run();
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
