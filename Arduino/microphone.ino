const int micpin = 7;
int mic; //variable for mic digitalRead 
int last_mic = 0;

void setup() {
  // put your setup code here, to run once:
//declare constant variables for pins
pinMode(micpin, INPUT);
last_mic = digitalRead(micpin);
Serial.begin(9600);
}


void loop() {
  int mic = digitalRead(micpin);
  if (mic == 1 && last_mic!=1){
    Serial.println("SOUND DETECTED");
    delay(2000);
  }
  last_mic = mic;
}