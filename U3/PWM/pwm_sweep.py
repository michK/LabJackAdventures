from time import sleep

import u3

# Open the first found LabJack.
d = u3.U3()

# Set the timer clock to be 4 MHz with a given divisor
d.configTimerClock(TimerClockBase=0, TimerClockDivisor=1)

# Enable the timer
d.configIO(NumberOfTimersEnabled=1)

# Configure the timer for PWM, starting with a duty cycle of 0.0015%.
baseValue = int((1-0.0015) * 65536)
d.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))

# Loop, updating the duty cycle every 100ms
for i in range(65):
    currentValue = baseValue - (i * 1000)
    dutyCycle = (float(65536-currentValue) / 65535) * 100.0
    print("Duty Cycle = %s%%" % dutyCycle)
    d.getFeedback(u3.Timer0(Value=currentValue, UpdateReset=True))
    sleep(0.1)

print("Duty Cycle = 100%")
d.getFeedback(u3.Timer0(Value=0, UpdateReset=True))

# Close the device.
d.close()
