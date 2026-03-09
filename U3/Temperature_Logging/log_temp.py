import datetime

import u3

d = u3.U3()

numChannels = 8
quickSample = 1
longSettling = 0
latestAinValues = [0] * numChannels

# To learn the if the U3 is an HV
d.configU3()

# For applying the proper calibration to readings.
d.getCalibrationData()

FIOEIOAnalog = (2 ** numChannels) - 1
fios = FIOEIOAnalog & 0xFF
eios = FIOEIOAnalog // 256
d.configIO(FIOAnalog=fios, EIOAnalog=eios)

d.getFeedback(u3.PortDirWrite(Direction=[0, 0, 0], WriteMask=[0, 0, 15]))

feedbackArguments = []
feedbackArguments.append(u3.DAC0_8(Value=125))
feedbackArguments.append(u3.PortStateRead())

# Check if the U3 is an HV
if d.configU3()['VersionInfo'] & 18 == 18:
    isHV = True
else:
    isHV = False

for i in range(numChannels):
    feedbackArguments.append(u3.AIN(i, 31, QuickSample=quickSample, LongSettling=longSettling))

results = d.getFeedback(feedbackArguments)
for j in range(numChannels):
    # Figure out if the channel is low or high voltage to use the correct calibration
    if isHV is True and j < 4:
        lowVoltage = False
    else:
        lowVoltage = True
    latestAinValues[j] = d.binaryToCalibratedAnalogVoltage(results[2 + j], isLowVoltage=lowVoltage, isSingleEnded=True)

volts = latestAinValues[4]

temp = (55.56 * volts) + 255.37 - 273.15

datestring = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

with open('/home/pi/LabJack/Temperature_Log/temperature-log.txt', 'a') as f:
    f.write(datestring + ',' + str(temp) + '\n')

d.close()
