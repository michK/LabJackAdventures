# This code demonstrates how to set up and run a stepper motor with a LabJack U3-HV
# and the DRV8825 stepper driver

# This stepper driver sets speed based on varying PWM frequency and not the more
# standard way of varying duty cycle, and thus only some fixed speeds can be achieved
# based on the discrete LJ clock frequencies

import time
import u3

# System parameters
theta_step = 1.8
rpm = 60
print("Target rpm: {}".format(rpm))

# Deduced values
f_step = rpm * 360 * 32 / (60 * theta_step)

divisor = int(48e6 / (256 * f_step))
f_step_actual = 48e6 / (256 * divisor)

rpm_actual = f_step_actual * 60 * theta_step / (360 * 32)
print("Actual rpm: {}".format(round(rpm_actual)))

# Open the first found LabJack.
d = u3.U3()

# Set the timer clock and divisor
d.configTimerClock(TimerClockBase=6, TimerClockDivisor=divisor)

# Enable the timer
d.configIO(NumberOfTimersEnabled=1)

# Set DIR pin high
d.writeRegister(5002,5)

# Configure the timer for PWM
duty_cycle = 0.5
baseValue = int((1-duty_cycle) * 65536)
d.getFeedback(u3.Timer0Config(TimerMode=1,Value=baseValue))

# Switch on DAC0 to enable
d.writeRegister(5000,5)

time.sleep(1)

# Change direction (first stop for brief period to avoid shock)
d.writeRegister(5000,0)
time.sleep(0.1)
d.writeRegister(5002,0)
d.writeRegister(5000,5)

time.sleep(1)

# Stop
d.writeRegister(5000,0)

# Close the device.
d.close()

