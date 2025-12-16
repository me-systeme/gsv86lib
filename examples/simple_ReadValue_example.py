import time
from gsv86lib import gsv86

# Open GSV-8 device on given serial port
# Example: "COM5" on Windows, "/dev/ttyACM0" on Linux
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

# Stop transmission when done
dev.StopTransmission()