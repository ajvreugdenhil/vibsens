#include <Arduino.h>
#include <Wire.h>
#include <LSM6.h>

LSM6 imu;

char report[250];

const int max_batchsize = 5000;
int16_t history_x[max_batchsize];
int16_t history_y[max_batchsize];
int16_t history_z[max_batchsize];

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
  Serial.flush();
  int batchsize = 0;
  while (!Serial.available())
  {
    imu.readAcc();
    history_x[batchsize] = imu.a.x - previous_x;
    history_y[batchsize] = imu.a.y - previous_y;
    history_z[batchsize] = imu.a.z - previous_z;
    previous_x = imu.a.x;
    previous_y = imu.a.y;
    previous_z = imu.a.z;
    batchsize += 1;
    if (batchsize >= max_batchsize)
    {
      batchsize = 0;
    }
  }
  while(Serial.available())
  {
    Serial.read();
  }

  const int histories_count = 3;
  int16_t *histories[histories_count] = {history_x, history_y, history_z};
  int16_t max_amplitudes[3] = {0, 0, 0};
  int16_t avg_amplitudes[3] = {0, 0, 0};
  int16_t frequencies[3] =    {0, 0, 0};
  for (int i = 0; i < histories_count; i++)
  {
    int16_t max_amplitude = 0;
    int64_t total_amplitude = 0;
    for (int j = 0; j < batchsize; j++)
    {
      if (abs(histories[i][j]) > abs(max_amplitude))
      {
        max_amplitude = histories[i][j];
      }
      total_amplitude += histories[i][j];

      max_amplitudes[i] = max_amplitude;
      avg_amplitudes[i] = total_amplitude / batchsize;
    }
  }

  snprintf(report,
           sizeof(report),
           "{\"MA_X\":%d, \"MA_Y\":%d, \"MA_Z\":%d, \"AA_X\":%d, \"AA_Y\":%d, \"AA_Z\":%d, \"F_X\":%d, \"F_Y\":%d, \"F_Z\":%d, \"SC\":%d}",
           max_amplitudes[0],
           max_amplitudes[1],
           max_amplitudes[2],
           avg_amplitudes[0],
           avg_amplitudes[1],
           avg_amplitudes[2],
           frequencies[0],
           frequencies[1],
           frequencies[2],
           batchsize);
  Serial.println(report);
}
