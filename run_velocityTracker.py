from src.estimator2D import Estimator2D
from src.mobileBaseControl import MobileBaseControl

import numpy as np
import time

from tqdm import tqdm
import sys
import signal

from scipy.spatial.transform import Rotation as R

# import pyagxrobots

if __name__ == '__main__':

    # init estimator and controller
    state_estimator = Estimator2D(path_imu="/dev/tty.usbserial-1110", path_optical_flow="/dev/tty.usbserial-0001")

    # tracer = pyagxrobots.pysdkugv.TracerBase()
    # tracer.EnableCAN()
    # tracer.EnableCAN()
    # tracer.EnableCAN()

    # Control parameters
    K_linear = 1
    K_angular = 1
    max_linear = 0.4
    max_angular = 1

    base_controller = MobileBaseControl(K_linear=K_linear, K_angular=K_angular, max_linear=max_linear, max_angular=max_angular)

    # Handler to log and exit at the end
    def signal_handler(sig, frame):
        state_estimator.stop()

        # Log
        with open("log/data_sensor_new_squareXTheta.csv", "w") as f:
            f.write("Time [s],Acceleration X [m/s^2],Acceleration Y [m/s^2],Acceleration Z [m/s^2],Angular velocity X [rad/s],Angular velocity Y [rad/s],Angular velocity Z [rad/s],Quaternion X,Quaternion Y,Quaternion Z,Quaternion W,Velocity X [m/s],Velocity Y [m/s],Height [m],Position X [m],Position Y [m]\n")
            for t, acceleration, angular_velocity, quaternion, velocity, position in zip(times, accelerations, angular_velocities, quaternions, velocities, positions):
                f.write(f"{t},{acceleration[0]},{acceleration[1]},{acceleration[2]},{angular_velocity[0]},{angular_velocity[1]},{angular_velocity[2]},{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]},{velocity[0]},{velocity[1]},{velocity[2]},{position[0]},{position[1]}\n")

        sys.exit(0)
    # Register hook to log and exit at the end
    signal.signal(signal.SIGINT, signal_handler)

    accelerations = []
    velocities = []
    positions = []
    quaternions = []
    angular_velocities = []
    times = []
    while state_estimator.time < 100:
        
        times.append(state_estimator.time)

        # Estimate and control robot
        state_estimator.update_state()
        command_linear_velocity, command_angular_velocity = base_controller.velocity_tracking(state_estimator.optical_flow[:2], state_estimator.angular_velocity)
        # tracer.SetMotionCommand(linear_vel=command_linear_velocity[0], angular_vel=command_angular_velocity[2])

        # Print and log
        np.set_printoptions(precision=3, suppress=True)
        print(f"Time:{state_estimator.time:.2f}, Position: {state_estimator.kf.x[2:4]}, Velocity: {state_estimator.kf.x[:2]}")

        accelerations.append(state_estimator.linear_acceleration)
        angular_velocities.append(state_estimator.angular_velocity)
        quaternions.append(state_estimator.quaternion)
        velocities.append(state_estimator.optical_flow)
        positions.append(state_estimator.kf.x[2:4])

        time.sleep(0.001)

    signal_handler(None, None)
    



