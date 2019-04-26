# Simple Adafruit BNO055 sensor reading example.  Will print the orientation
# and calibration data every second.
#
# Copyright (c) 2015 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import subprocess
import time
import requests
#from deepstream import get, post
from Adafruit_BNO055 import BNO055

import time

import roslibpy
#192.168.1.3 is base station needs to changed for comp
client = roslibpy.Ros(host='192.168.1.2', port=9090)
talker = roslibpy.Topic(client, '/baseIMU', 'std_msgs/String')

global imuData
imuData = {}
heading = 0

#subprocess.call(["python", "calImuOnly.py"])
time.sleep(3)

magneticDeclination = 11.88

# Create and configure the BNO sensor connection.  Make sure only ONE of the
# below 'bno = ...' lines is uncommented:
# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
#bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
# BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
# and RST connected to pin P9_12:
bno = BNO055.BNO055(busnum=1)
confMode = True

# Enable verbose debug logging if -v is passed as a parameter.
time.sleep(1)
# Initialize the BNO055 and stop if something went wrong.
while not bno.begin():
    print('Waiting for sensor...')
    time.sleep(1)

def magToTrue(h):
    return (h + magneticDeclination) % 360


fileIn = open('calibrationData.txt','r')
data = fileIn.read().splitlines()
for i in range(len(data)):
    data[i] = int(data[i])
print data
bno.set_calibration(data)
fileIn.close()

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()


print('Reading BNO055 data, press Ctrl+C to quit...')

def start_talking():
    global heading
    while client.is_connected:
        talker.publish(roslibpy.Message({'data': str(heading)}))
#        print('Sending message...')

        try:
            # Read the Euler angles for heading, roll, pitch (all in degrees)
	    heading, roll, pitch = bno.read_euler()
	    # Read the calibration status, 0=uncalibrated and 3=fully calibrated
	    #sys, gyro, accel, mag = bno.get_calibration_status()
	    heading = magToTrue(heading)

	    if sys == 3 and gyro == 3 and accel == 3 and mag == 3 and confMode:
	        bno.set_mode(0X0C)
	        confMode = False

	    time.sleep(1)
            talker.unadvertise()
        except:
            print("Error")


client.on_ready(start_talking)
client.run_forever()
