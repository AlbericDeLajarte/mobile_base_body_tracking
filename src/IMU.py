import serial
import binascii
import struct
import numpy as np

def clean_byte(bytes):
    return binascii.unhexlify( (b''.join(bytes)) )

class IMU():

    def __init__(self, path_device: str, baud_rate : int = 115200) -> None:

        self.serial = serial.Serial(path_device, baud_rate)
        
        self.acceleration = np.zeros(3)
        self.angular_velocity = np.zeros(3)

        self.euler_orientation = np.zeros(3)
        self.quaternion = np.array([0, 0, 0, 1])


    def update(self, nTry = 10):

        # Sync the serial port with header
        iter = 0
        while(iter < nTry):
            header = ''
            while header != b'\x5A':
                header = self.serial.read(1)

            hex_string = binascii.hexlify(self.serial.read(81))
            byte_pairs = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]

            if (clean_byte(byte_pairs[0:3]) == b'\xa5\x4c\x00') and (clean_byte(byte_pairs[5:8]) == b'\x91\x01\x00'): break
            iter += 1

        # Don't update the IMU data if the header is not found
        if iter == nTry:
            print("IMU data not found")
            return

        # Fill sensor data
        # temperature = struct.unpack('b', clean_byte(byte_pairs[8:9]) )
        # pressure = struct.unpack('<f', clean_byte(byte_pairs[9:13]) )
        # time = struct.unpack('<I', clean_byte(byte_pairs[13:17]) )

        self.acceleration = np.array([
            struct.unpack('<f', clean_byte(byte_pairs[17:21]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[21:25]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[25:29]) )[0]
        ])
        self.angular_velocity = np.array([
            struct.unpack('<f', clean_byte(byte_pairs[29:33]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[33:37]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[37:41]) )[0]
        ])
        # magnetic_field = np.array([
        #     struct.unpack('<f', clean_byte(byte_pairs[41:45]) )[0],
        #     struct.unpack('<f', clean_byte(byte_pairs[45:49]) )[0],
        #     struct.unpack('<f', clean_byte(byte_pairs[49:53]) )[0]
        # ])
        self.euler_orientation = np.array([
            struct.unpack('<f', clean_byte(byte_pairs[53:57]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[57:61]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[61:65]) )[0]
        ])
        new_quaternion = np.array([
            struct.unpack('<f', clean_byte(byte_pairs[69:73]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[73:77]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[77:81]) )[0],
            struct.unpack('<f', clean_byte(byte_pairs[65:69]) )[0],
        ])

        if np.abs(np.linalg.norm(new_quaternion)-1)<0.1: self.quaternion=new_quaternion