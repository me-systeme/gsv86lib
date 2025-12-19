import time

# import os
# import sys
# # Projekt-Root bestimmen
# ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# SRC = os.path.join(ROOT, "src")
# # src zum Import-Pfad hinzufügen
# sys.path.insert(0, SRC)
# from gsv86lib.gsv86 import gsv86

from gsv86lib import gsv86

# Open GSV-8 device on given serial port
# Example: "COM5" on Windows, "/dev/ttyACM0" on Linux
# This is just an example. You need to set the COM port 
# and Baudrate (here 115200) depending on your device.
# The default configuration of devices GSV 8 and GSV 6 are:
# GSV8: 115200
# GSV6: 230400
dev = gsv86("COM3", 115200)

# Optional: configure data rate (Hz)
dev.writeDataRate(50.0)

# Start continuous transmission
dev.StartTransmission()

time.sleep(0.2)

# Read a single measurement frame
measurement = dev.ReadValue()

# Access individual channels (1..8)
ch1 = measurement.getChannel1()
ch2 = measurement.getChannel2()
ch3 = measurement.getChannel3()
ch4 = measurement.getChannel4()
ch5 = measurement.getChannel5()
ch6 = measurement.getChannel6()
ch7 = measurement.getChannel7()
ch8 = measurement.getChannel8()

print("Channel 1:", ch1)
print("Channel 2:", ch2)
print("Channel 3:", ch3)
print("Channel 4:", ch4)
print("Channel 5:", ch5)
print("Channel 6:", ch6)
print("Channel 7:", ch7)
print("Channel 8:", ch8)

dev.SetZero(0)
print("All channels are set to zero.")

# dev.SetZero(1)
# print("Channels 1 is set to zero.")

time.sleep(1)

measurement = dev.ReadValue()

# Access individual channels (1..8)
ch1 = measurement.getChannel1()
ch2 = measurement.getChannel2()
ch3 = measurement.getChannel3()
ch4 = measurement.getChannel4()
ch5 = measurement.getChannel5()
ch6 = measurement.getChannel6()
ch7 = measurement.getChannel7()
ch8 = measurement.getChannel8()

print("Channel 1:", ch1)
print("Channel 2:", ch2)
print("Channel 3:", ch3)
print("Channel 4:", ch4)
print("Channel 5:", ch5)
print("Channel 6:", ch6)
print("Channel 7:", ch7)
print("Channel 8:", ch8)

# Stop transmission when done
dev.StopTransmission()