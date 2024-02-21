# LabJackAdventures
The [LabJack](https://labjack.com/) is a general purpose data aquisition device that can be used for many different things on top of aquiring data, including:
- Measuring analog voltage signals
- Outputting analog voltage signals
- Reading and writing digital signals
- Generating clock signals of different frequencies
- Using high speed timers and counters, which can in turn be used for:
    - Outputing PWM signals at different frequencies and duty cycles
    - Measuring signal frequencies
    - Reading encoders (rotary encoders for input or shaft encoders for motor speed)
    - Many more things ...

LabJack has many example scripts of how to use their devices in many different use cases, and their [website](https://labjack.com/) and [Github repo](https://github.com/labjack) are great resources.

Over time I've used LabJacks for various different things and thought I would throw my scripts into this repo; maybe someone will find it useful.
  
I've only used the U3-HV and T4 models, and although they are programmed with different API's, for the most part everything I've been able to do with the T4 I've also been able to do with the U3, so in my opinion the U3 is good enough for most applications unless you want to use the LJ as a stand-alone device in which case you need the Lua scripting functionality of the T-series.

In this repo I'll mostly post Python scripts for controlling the U3, since I've only used the T4 at work.

Questions, suggestions and bug notifications are welcome, just post an 'issue'
