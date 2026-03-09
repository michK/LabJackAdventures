import time
import signal

import u3
from stepper_tools import ramp_up


def handler(signum, frame):
    """Used to catch Ctrl-C event to stop script"""
    d.writeRegister(5000, 0)
    d.close()
    exit(1)

# System parameters
theta_step = 1.8
rpm = 550
print("Target rpm: {}".format(rpm))

# Deduced values
f_step = rpm * 360 * 32 / (60 * theta_step)
divisor = int(48e6 / (256 * f_step))
f_step_actual = 48e6 / (256 * divisor)
rpm_actual = f_step_actual * 60 * theta_step / (360 * 32)
print("Actual rpm: {}".format(round(rpm_actual)))

# Open the first found LabJack.
d = u3.U3()

# Enable the timer
d.configIO(NumberOfTimersEnabled=1)

# Set DIR pin high
d.writeRegister(5002, 5)
# Switch on DAC0 to enable
d.writeRegister(5000, 5)

ramp_up(d, rpm, 50, theta_step)

print("Up to speed")

time.sleep(5)

# Stop
d.writeRegister(5000, 0)

# Close the device.
d.close()
