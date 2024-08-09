import serial
import numpy as np
import struct

message_MSP = {0x1F01: 'MSP2_SENSOR_RANGEFINDER',
                    0x1F02: 'MSP2_SENSOR_OPTIC_FLOW'}

class OpticalFlow():

    def __init__(self, alpha=1) -> None:
        
        self.ser = serial.Serial('/dev/tty.usbserial-0001', 115200)

        self.alpha = alpha  

        self.velocity = np.zeros(3)


    def get_pose(self):

        # Read the contents of the serial port (we don't know how many bytes)
        buffer = ''
        while buffer != b'$': buffer = self.ser.read(1)
        x = self.ser.read()
        if x != b'X':
            print(x)
            return

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
                self.velocity[2] = self.alpha*posZ + (1-self.alpha)*self.velocity[2]
            
            if message_MSP[function_message] == 'MSP2_SENSOR_OPTIC_FLOW':
                assert payload_length == 9, "Payload length of optic flow is not 12"
                quality = struct.unpack('<B', payload[:1])[0]
                posX = struct.unpack('<i', payload[1:5])[0]/1000.0
                posY = -struct.unpack('<i', payload[5:])[0]/1000.0
                # print(f'Quality: {quality}, posX: {posX}, posY: {posY}')
                self.velocity[:2] = self.alpha*np.array([posX, posY]) + (1-self.alpha)*self.velocity[:2]
            
            # print(f"Time {time.time()-t0}, Quality: {quality}, Position: {position}")
        else:
            print(function_message, payload)


        return self.velocity

        