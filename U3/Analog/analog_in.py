import u3

d = u3.U3()

# To learn the if the U3 is an HV
d.configU3()

# For applying the proper calibration to readings.
d.getCalibrationData()

# Set FIO0 and FIO1 to analog
d.configIO(FIOAnalog=3)

# AIN0 = address 0, AIN1 = address 2, AIN3 = address 6
dacAddress = 0  # AIN0

volts = d.readRegister(dacAddress, 0)

print(volts)

d.close()
