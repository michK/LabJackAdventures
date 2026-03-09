from time import sleep

import u3

# Open the first found LabJack.
d = u3.U3()

# Set the timer clock to be 4 MHz with a given divisor
d.configTimerClock(TimerClockBase=0, TimerClockDivisor=1)

# Enable the timer
d.configIO(NumberOfTimersEnabled=1)

# Configure the timer for PWM
duty_cycle = 0.2
baseValue = int((1-duty_cycle) * 65536)
d.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))

# Close the device.
d.close()
