#!/usr/bin/env python
#
#     |<------->|          Measure the time between two rising
#                          edges on the LabJack's FIO4 pin,
#     +----+    +----+     then calculate the frequency in Hertz.
#     |    |    |    |
# ----+    +----+    +----

import time
import u3

dev = u3.U3()
dev.configIO(TimerCounterPinOffset=4, NumberOfTimersEnabled=1)

cmd = u3.Timer0Config(TimerMode=2, Value=0)
dev.getFeedback(cmd)

# Set timer clock to 4 MHz, divisor=1
cmd = dev.configTimerClock(0, 1)
dev.getFeedback(cmd)

# Let a few pulses roll through the timer
time.sleep(0.1)

# Read pulse width in ticks
cmd = u3.Timer(timer=0)
ticks = dev.getFeedback(cmd)[0]

# Scale ticks to a period in seconds, then convert to frequency in Hz
if ticks > 0:
    period_secs = ticks / 4000000.0
    freq_hz = 1 / period_secs
else:
    freq_hz = 0

print("%0.04f Hz" % freq_hz)

dev.close()
