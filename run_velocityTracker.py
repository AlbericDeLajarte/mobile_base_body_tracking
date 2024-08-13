from src.estimator2D import Estimator2D
from src.mobileBaseControl import MobileBaseControl

import numpy as np
import time

from tqdm import tqdm
import sys
import signal

from scipy.spatial.transform import Rotation as R

import pyagxrobots

if __name__ == '__main__':

    # init estimator and controller
    state_estimator = Estimator2D(path_imu="/dev/ttyUSB0", path_optical_flow="/dev/ttyUSB1")

    tracer = pyagxrobots.pysdkugv.TracerBase()
    tracer.EnableCAN()
    tracer.EnableCAN()
    tracer.EnableCAN()

    # Control parameters
    KP_linear = 1
    KP_angular = 1
    max_linear = 0.4
    max_angular = 1

    base_controller = MobileBaseControl(KP_linear=KP_linear, KP_angular=KP_angular, 
                                        max_linear=max_linear, max_angular=max_angular, 
                                        KI_linear=0.2, KI_angular=1, alpha=0.6)

    # Handler to log and exit at the end
    def signal_handler(sig, frame):
        state_estimator.stop()

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
    while state_estimator.time < 1000:
        
        # Estimate and control robot
        state_estimator.update_state()

        teleop_velocity = np.concatenate(( state_estimator.kf.x[:2], [0.0] ))
        base_linear_velocity = np.concatenate(( [tracer.GetLinearVelocity()], [0.0, 0.0] ))
        base_angular_velocity = np.concatenate(( [0.0, 0.0], [tracer.GetAngularVelocity()] ))

        command_linear_velocity, command_angular_velocity = base_controller.velocity_tracking(teleop_velocity, state_estimator.angular_velocity, base_linear_velocity, base_angular_velocity)
        tracer.SetMotionCommand(linear_vel=command_linear_velocity[0], angular_vel=command_angular_velocity[2])

        # Print and log
        np.set_printoptions(precision=3, suppress=True)
        print(f"Time:{state_estimator.time:.2f}, Position: {state_estimator.kf.x[2:4]}, Velocity: {state_estimator.kf.x[:2]}")

        # Save data
        times.append(state_estimator.time)
        base_controls.append([command_linear_velocity[0], command_angular_velocity[2]])
        base_states.append([tracer.GetLinearVelocity(), tracer.GetAngularVelocity()])

        time.sleep(0.001)

    signal_handler(None, None)
    



