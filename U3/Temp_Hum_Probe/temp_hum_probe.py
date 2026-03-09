from time import sleep

import u3

# Set communication pin
pin = 4

# Set delay constants
delay = {
    '1ms':  5/1000,
    '40ms': 20/1000,
    '80ms': 70/1000,
}

# Open the first found LabJack.
d = u3.U3()

# Set FIO4 to high to start
d.setFIOState(pin, state=1)

# Wait 1s
sleep(1)

# Go low for 1ms to start communication
d.setFIOState(pin, state=0)
sleep(delay['1ms'])

# Go back to high
d.setFIOState(pin, state=1)

# Wait for 40ms for probe to prepare response
sleep(delay['40ms'])

# Go low for 80ms and listen to response
d.setFIOState(pin, state=0)
sleep(delay['80ms'])

# Go back to high
d.setFIOState(pin, state=1)

# Close the device.
d.close()
