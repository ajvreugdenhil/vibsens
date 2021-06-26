#include <Arduino.h>
#include <Wire.h>
#include <LSM6.h>

LSM6 imu;

char report[80];

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("test???");
  Wire.begin();

  if (!imu.init())
  {
    Serial.println("Failed to detect and initialize IMU!");
    while (1)
      ;
  }
  imu.enableDefault();
}

int16_t previous_x = 0;
int16_t previous_y = 0;
int16_t previous_z = 0;

void loop()
{
  delay(10);
  imu.readAcc();
  snprintf(report, sizeof(report), "[%d, %d, %d]",
           imu.a.x - previous_x,
           imu.a.y - previous_y,
           imu.a.z - previous_z);
  Serial.println(report);

  previous_x = imu.a.x;
  previous_y = imu.a.y;
  previous_z = imu.a.z;
}
