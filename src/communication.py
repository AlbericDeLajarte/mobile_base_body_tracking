import zmq
import numpy as np

class Receiver():
    def __init__(self, adress, timeout=500):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(adress)
        self.timeout = timeout

        self.command_linear_velocity = np.zeros(3)
        self.command_angular_velocity = np.zeros(3)

    def get_command(self):

        if self.socket.poll(self.timeout):
            message = self.socket.recv_string().split(",")
            self.command_linear_velocity = np.array([float(message[0]), float(message[1]), float(message[2])])
            self.command_angular_velocity = np.array([float(message[3]), float(message[4]), float(message[5])])

            # Send a reply back to the requester
            self.socket.send_string("OK")
        else:
            self.command_linear_velocity = np.zeros(3)
            self.command_angular_velocity = np.zeros(3)

        return self.command_linear_velocity, self.command_angular_velocity
    
    def close(self):
        """Close the ZeroMQ socket and context."""
        self.socket.close()
        self.context.term()
    

class Sender():
    def __init__(self, adress):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(adress)

    def send_command(self, command_linear_velocity, command_angular_velocity):
        message = f"{command_linear_velocity[0]},{command_linear_velocity[1]},{command_linear_velocity[2]},{command_angular_velocity[0]},{command_angular_velocity[1]},{command_angular_velocity[2]}"
        self.socket.send_string(message)
        reply = self.socket.recv_string()

        assert reply == "OK", "Error in communication"

    def close(self):
        self.socket.close()
        self.context.term()