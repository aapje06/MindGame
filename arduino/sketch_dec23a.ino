void setup() 
{
for (int i = 2; i < 19; i++)
 {
  pinMode(i,INPUT_PULLUP); 
 }
 for (int i = 22; i < 54; i++)
 {
  pinMode(i,OUTPUT);
 }
 Serial.begin(9600);

}

void loop() {
  for (int i = 2; i < 18; i++)
 {
    printled(i,digitalRead(i));    
 }
  if (digitalRead(18))
  {
    digitalWrite(52,HIGH);
    digitalWrite(53,LOW);
  }
  else
  {
    digitalWrite(53,HIGH);
    digitalWrite(52,LOW);
  }
}
void printled(int port, boolean highlow)
{
  Serial.println(port);
  Serial.println(highlow);
  if (highlow == 1)
  {
  digitalWrite(22+(port-2)*2, HIGH);
  digitalWrite(23+(port-2)*2,LOW);
  }
  else
  {
    digitalWrite(22+(port-2)*2, LOW);
    digitalWrite(23+(port-2)*2, HIGH);
  }
 
}


