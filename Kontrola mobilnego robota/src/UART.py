import serial

class UART:
    def __init__(self,port,baudrate,timeout) -> None:
        self.UART = serial.Serial(port,baudrate,timeout=timeout)
    def sendMessage(self, v, rho, omega):
        rho = round(rho, 5)
        omega = round(omega, 5)
        checksum = v + rho + omega
        message = (str(v) + ',' + str(rho) + ',' + str(omega) + ',' + str(checksum) + '\n').encode('ascii')
        self.UART.write(message)
