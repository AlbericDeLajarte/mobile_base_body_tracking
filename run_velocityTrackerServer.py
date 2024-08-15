from src.estimator2D import Estimator2D
from src.mobileBaseControl import MobileBaseControl

from src.communication import Receiver

import numpy as np
import time

import sys
import signal

from scipy.spatial.transform import Rotation as R

import pyagxrobots

if __name__ == '__main__':

    tracer = pyagxrobots.pysdkugv.TracerBase()
    tracer.EnableCAN()
    tracer.EnableCAN()
    tracer.EnableCAN()

    zmq_receiver = Receiver("tcp://*:5555")

    # Handler to log and exit at the end
    def signal_handler(sig, frame):

        import datetime
        file_name = datetime.datetime.now().strftime("%m_%d_%Y-%I:%M%p:%S.csv")
        with open(f"log/{file_name}", "w") as f:
            f.write("Time [s],State Linear velocity [m/s],State Angular velocity [rad/s],Control Linear velocity [m/s],Control Angular velocity [rad/s]\n")

            for time, base_state, base_control in zip(times, base_states, base_controls):
                f.write(f"{time}, {base_state[0]}, {base_state[1]}, {base_control[0]}, {base_control[1]}\n")

        sys.exit(0)
    # Register hook to log and exit at the end
    signal.signal(signal.SIGINT, signal_handler)

    base_states = []
    base_controls = []
    times = []
    t0 = time.time()
    tNow = 0.0
    while tNow < 1000:

        tNow = time.time() - t0
        
        # Estimate and control robot
        command_linear_velocity, command_angular_velocity = zmq_receiver.get_command()
        tracer.SetMotionCommand(linear_vel=command_linear_velocity[0], angular_vel=command_angular_velocity[2])
        print(f"Time {tNow:.3f} s, Command linear velocity {command_linear_velocity[0]:.3f} m/s, Command angular velocity {command_angular_velocity[2]:.3f} rad/s")

        # Save data
        times.append(tNow)
        base_controls.append([command_linear_velocity[0], command_angular_velocity[2]])
        base_states.append([tracer.GetLinearVelocity(), tracer.GetAngularVelocity()])

        time.sleep(0.001)

    signal_handler(None, None)
    



