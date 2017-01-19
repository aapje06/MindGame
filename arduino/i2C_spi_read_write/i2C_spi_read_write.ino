#include <Wire.h> //library voor i2C
#include <QueueArray.h> //library om met een Queue (rij) te werken
#include <Adafruit_NeoPixel.h> //library om met die neopixels te werken
#define bril1 A0 //ledstrip van bril 1, zit op analoge pin omdat digitale op waren
#define bril2 A1 //ledstrip van bril 2, zit op analoge pin omdat digitale op waren
Adafruit_NeoPixel brilstrip1 = Adafruit_NeoPixel(7, bril1, NEO_GRB + NEO_KHZ800); //initializeren van stips
Adafruit_NeoPixel brilstrip2 = Adafruit_NeoPixel(7, bril2, NEO_GRB + NEO_KHZ800); //41 is aantal leds in strip
int leds[] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53};
//Adafruit_NeoPixel holestrips[] = {timestrip1,timestrip2};
#define SLAVE_ADDRESS 0x04 //voor i2c, de rpi stuurt dan naar adress 0x04
int pulsePin2 = A3;
byte speler1 = 0; //hierin wordt de sensorwaarde van speler1 opgeslagen
byte speler2 = 0; //hierin wordt de sensorwaarde van speler2 opgeslagen
int RGB[] = {0,0,0}; //bevat de laatste 3 bytes per paket
int counter = 0; //telt tot 4 om zo ieder pakket juist te plaatsen
int port = 0; // is de eerste byte van het pakket en bepaald de actie
boolean initialize = false; 
QueueArray <byte> queue;

//voor de sensor1:
int pulsePin = A2;                 // Pulse Sensor purple wire connected to analog pin 0
volatile int BPM;                   // int that holds raw Analog in 0. updated every 2mS
volatile int Signal;                // holds the incoming raw data
volatile int IBI = 600;             // int that holds the time interval between beats! Must be seeded! 
volatile boolean Pulse = false;     // "True" when User's live heartbeat is detected. "False" when not a "live beat". 
volatile boolean QS = false;        // becomes true when Arduino finds a beat.
// Regards Serial OutPut  -- Set This Up to your needs
static boolean serialVisual = true;   // Set to 'false' by Default.  Re-set to 'true' to see Arduino Serial Monitor ASCII Visual Pulse

void setup (void) //alle inputs, outputs plaatsen)
{
  for (int i = 2; i < 18; i++)
  {
    pinMode(i,INPUT_PULLUP);
  }
  pinMode(18,INPUT_PULLUP);
  
  for (int i = 22; i < 54; i++)
  {
    pinMode(i,OUTPUT);
  }
  brilstrip1.begin();
  brilstrip2.begin();
  brilstrip1.setBrightness(255); //adjust brightness here
  brilstrip2.setBrightness(255); //adjust brightness here
  brilstrip1.show();
  brilstrip2.show();
  Serial.begin (115200);   // debugging
  Wire.begin(SLAVE_ADDRESS); //i2c initializeren
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  initializegame();

  //voor de sensor:
    interruptSetup();                 // sets up to read Pulse Sensor signal every 2mS 
   // IF YOU ARE POWERING The Pulse Sensor AT VOLTAGE LESS THAN THE BOARD VOLTAGE, 
   // UN-COMMENT THE NEXT LINE AND A
}
// I2C receive data routine

void receiveData(int byteCount) //ontvangt continue data
{
  while(Wire.available()) 
  {
    int temp = Wire.read();
    if(initialize == false)queue.enqueue(temp); //en plaatst alle data meteen in een rij.
    if (temp == 61)
    {
      initialize = false;
      startgame();
    }
  }
}

// I2C send data routine
void sendData(){
  byte sensor1value = (byte)BPM;
  byte sensor2value = 100;
  byte inputs[] = {0,sensor1value,1,sensor2value,2,speler1,3,speler2};
  Wire.write(inputs,8); // verzend de sensorwaarden en de waardes van de pinnen (als byte) naar de rpi
  delay(250);
}


// Main loop - wait for SPI interruption routine
void loop (void)
{
  setbuttonvalues();  //alle inputs updaten
  while(!queue.isEmpty()) //als er een pakket in queue zit dit eruit halen
  {
    if (counter == 0)
    {
      port = queue.dequeue(); //de poort is 1e waarde van pakket
      if (port == 0 || port == 255) //maar als dit een 0 of 255 is moet hij deze verwerpen en wachten op geldig antwoordt
      {
        counter = 0;
        Serial.println("Regular answer");
      }
      else
      {
        counter++; //indien de poort een geldig antwoord is mag hij de volgende 3 waardes inlezen
      }
    }
    else if (counter > 0 && counter < 4)
    {
      RGB[counter -1] = queue.dequeue(); //deze waardes worden in een array RGB geplaatst
      counter++;
    }
    else //als eer een pakket gemaakt is (geldige poort en 3 waardes in RGB zal hij actie ondernemen
    {
      Serial.print("pakket: "); //volgende print's zijn gewoon als controle
      Serial.print(port);
      Serial.print(" ");
      Serial.print(RGB[0]);
      Serial.print(" ");
      Serial.print(RGB[1]);
      Serial.print(" ");
      Serial.println(RGB[2]);
      /*if ((port > 21 && port < 54) && RGB[2] == 255) //dit zijn de leds voor de gaten, RGB[255] is extra controle
      {
        Serial.print("led geschakeld op poort ");
        Serial.println(port);
        setColor(port,RGB[0],RGB[1]); //functie aanroepen die gevraagde leds op doorgestuurde waarde Rood en Groen plaatsen
        counter = 0;          
      }*/
      if (port == 22)
      {
        for (int i = 0; i < 8; i++)
        {
          if (RGB[0] & 1 << i)
          {
            if (RGB[1] & 1 << i)
            {
              digitalWrite(22+i*2,HIGH);
            }
            else
            {
              digitalWrite(22+i*2,LOW);
            }
            if (RGB[2] & 1 << i)
            {
              digitalWrite(23+i*2,HIGH);
            }
            else
            {
              digitalWrite(23+i*2,LOW);
            }
          }
        }
        counter = 0;
      }
      else if (port == 38)
      {
        for (int i = 0; i < 8; i++)
        {
          if (RGB[0] & 1 << i)
          {
            if (RGB[1] & 1 << i)
            {
              digitalWrite(38+i*2,HIGH);
            }
            else
            {
              digitalWrite(38+i*2,LOW);
            }
            if (RGB[2] & 1 << i)
            {
              digitalWrite(39+i*2,HIGH);
            }
            else
            {
              digitalWrite(39+i*2,LOW);
            }
          }
        }
        counter = 0;
      }    
      
      else if (port == 54) //port 54 en 55 = de headsetstrip van speler 1 en 2
      {
        Serial.println("bril 1 geschakeld");
        for(uint16_t i=0; i<brilstrip1.numPixels(); i++) 
        {
         brilstrip1.setPixelColor(i, brilstrip1.Color(RGB[0],RGB[1],RGB[2])); 
        }
       brilstrip1.show();
        counter = 0;
      }
      else if (port == 55) ////port 54 en 55 = de headsetstrip van speler 1 en 2
      {
        Serial.println("bril 2 geschakeld");
        for(uint16_t i=0; i<brilstrip2.numPixels(); i++) 
        {
         brilstrip2.setPixelColor(i, brilstrip2.Color(RGB[0],RGB[1],RGB[2]));           
        }
        brilstrip2.show(); 
        counter = 0;
      }
      else if (port == 60 && RGB[0] == 255 && RGB[1] == 0 && RGB[2] == 255) //port 60 = initalize
      { //de bedoeling is dat dit doorgestuurd wordt in het begin en er dan een animatie op alle leds tevoorschijn komt
        initialize = true; //RGB[0],RGB[1] en RGB[2] zijn opnieuw extra controle
        Serial.println("initialize");
        initializegame(); 
        counter = 0;
      }
      else if (port == 61 && RGB[0] == 255 && RGB[1] == 0 && RGB[2] == 255) //port 60 = startgame
      { //als spel start alle leds van tijdsbalk groen maken, animatie stoppen op leds in gaten...
        initialize = false;
        Serial.println("startgame");
        startgame();
        counter = 0;
      }
      else //alstie ander pakket vindt: oei, is handig tijdens testen
      {
        Serial.print("oei op poort ");
        Serial.println(port);
        counter = 0; //in iedere if lus hierboven zie je onderaan 'counter = 0' dit zorgt ervoor dat hij aan zijn volgend pakket kan beginnen
      }
    }
  }
}
void setColor(int port, int R, int G) 
{
 if (R == 255)
  {
    digitalWrite(port, HIGH);
  }
  else if (R != 255)
  {
    digitalWrite(port, LOW);
  }
  if (G == 255)
  {
    digitalWrite(port+1, HIGH);
  }
  else if (G != 255)
  {
    digitalWrite(port+1, LOW);
  }
}

void setbuttonvalues()
{
  speler1 = 0;
  for (int i = 0; i < 8; i++)
  {
    int temp = digitalRead(i+2);
    if (temp == LOW)
    {
      speler1 = speler1 | 1<<i;//(int)(pow(2,i)+0.5);
      
    }
  }
  speler2 = 0;
  for (int i = 0; i < 8; i++)
  {
      int temp = digitalRead(i+10);
      if (temp == LOW)
      {
        speler2 = speler2 | 1<<i;//(int)(pow(2,i)+0.5);
      }
  }
}
void colorWipe(Adafruit_NeoPixel &stripbril, uint32_t c) {
  for(uint16_t i=0; i<stripbril.numPixels(); i++) {
    stripbril.setPixelColor(i, c); 
    stripbril.show();  
    delay(50);
  }
}

void initializegame()
{
  while (initialize)
  {
    for (int i = 0; i < 16; i++)
    {
      if (initialize)
      {
        setColor(22+2*i,255,0);
        delay(50);
      }
    }
    for (int i = 0; i < 16; i++)
    {
      if (initialize)
      {
        setColor(22+2*i,0,255);
        delay(50);
      } 
    }
  }
}
void startgame()
{
  for (int i = 0; i < 16; i++)
  {
    setColor(22+2*i,255,0);
  }
  for (int i = 0; i < 16; i++)
  {
    setColor(22+2*i,255,0);
  }
}

