#include <Wire.h>
int Address = 0x60;
#define BEARING_0 0x02
#define BEARING_1 0x03
int X0, X1;
void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  Wire.beginTransmission(Address);
  Wire.write(BEARING_0);
  Wire.write(BEARING_1);
  Wire.endTransmission();
   Wire.requestFrom(Address,2);
   if(Wire.available()<=2) {
    X0 = Wire.read(); // Reads the data from the register
    X1 = Wire.read();   
    int output = word(X0, X1);
    Serial.print(output);
    Serial.print("\n");
    delay(150);
  }
  
}
