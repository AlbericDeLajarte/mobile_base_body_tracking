import serial
import numpy as np
import struct

message_MSP = {0x1F01: 'MSP2_SENSOR_RANGEFINDER',
                    0x1F02: 'MSP2_SENSOR_OPTIC_FLOW'}

class OpticalFlow():

    def __init__(self, path_device: str, baud_rate : int = 115200, alpha=1) -> None:
        
        self.ser = serial.Serial(path_device, baud_rate)

        self.alpha = alpha  

        self.velocity = np.zeros(2)
        self.altitude = 0


    def update(self):

        # Read the contents of the serial port until we find the header
        buffer = ''
        while buffer != b'$': buffer = self.ser.read(1)
        x = self.ser.read()
        if x != b'X':
            print(x)
            return

        # Parse the data
        receive_mode = self.ser.read(1)
        flag = self.ser.read(1)
        function_message = struct.unpack('<H', self.ser.read(2))[0]
        payload_length = struct.unpack('<H', self.ser.read(2))[0]
        payload = self.ser.read(payload_length)
        checksum = self.ser.read(1)

        if function_message in message_MSP:
            
            if message_MSP[function_message] == 'MSP2_SENSOR_RANGEFINDER':
                assert payload_length == 5, "Payload length of rangefinder is not 5"
                quality = struct.unpack('<B', payload[:1])[0]
                posZ = struct.unpack('<i', payload[1:])[0]/1000.0
                # print(f'Quality: {quality}, posZ: {posZ}')
                if posZ>0: self.altitude = self.alpha*posZ + (1-self.alpha)*self.altitude
            
            if message_MSP[function_message] == 'MSP2_SENSOR_OPTIC_FLOW':
                assert payload_length == 9, "Payload length of optic flow is not 12"
                quality = struct.unpack('<B', payload[:1])[0]
                speedX = struct.unpack('<i', payload[1:5])[0]/100.0
                speedY = -struct.unpack('<i', payload[5:9])[0]/100.0
                # print(f'Quality: {quality}, speedX: {speedX:.3f}, speedY: {speedY:.3f}')
                self.velocity = self.alpha*np.array([speedX, speedY]) + (1-self.alpha)*self.velocity
            
            # print(f"Time {time.time()-t0}, Quality: {quality}, Position: {position}")
        else:
            print(function_message, payload)


if __name__ == '__main__':
    import time

    of = OpticalFlow(path_device="/dev/tty.usbserial-0001")

    for _ in range(1000):
        of.update()
        print(of.velocity, of.altitude)
        time.sleep(0.01)