import u3

d = u3.U3()

dacAddress = 5000  # DAC0 Modbus address (5002 = DAC1)

d.writeRegister(dacAddress, 2.5)

d.close()
