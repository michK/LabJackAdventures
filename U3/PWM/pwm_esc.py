from time import sleep

import numpy as np
import u3

# Open the first found LabJack.
d = u3.U3()

# Set the timer clock to be 4 MHz with a given divisor
d.configTimerClock(TimerClockBase=0, TimerClockDivisor=1)

# Enable the timer; TimerCounterPinOffset=4 puts PWM output on FIO4 pin
d.configIO(NumberOfTimersEnabled=1, TimerCounterPinOffset=4)

# Map throttle [0, 1] to ESC duty cycle range [5.9%, 12.1%]
throttle_setting = 0.0
throttle_range = [0, 1]
duty_range = [5.9, 12.1]
duty_cycle = np.interp(throttle_setting, throttle_range, duty_range) / 100

baseValue = int((1-duty_cycle) * 65536)
d.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))

# Close the device.
d.close()
