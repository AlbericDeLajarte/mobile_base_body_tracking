from src.estimator2D import Estimator2D, trackerSwitch
from src.communication import Sender
from src.mobileBaseControl import MobileBaseControl

import numpy as np
import time

from tqdm import tqdm
import sys
import signal

from scipy.spatial.transform import Rotation as R

# Check list for demo !!
# - Plug cable, check tty port
# - Start the server
# - Start the client, check estimate is correct
# - Activate tracking

if __name__ == '__main__':

    # init estimator and controller
    state_estimator = Estimator2D(path_imu="/dev/tty.usbserial-1qqqqqqqqqqqq10", path_optical_flow="/dev/tty.usbserial-0001")
    zmq_sender = Sender("tcp://10.103.1.38:5555")
    switch = trackerSwitch(state_estimator)

    # Control parameters
    KP_linear = 1
    KP_angular = 1
    max_linear = 0.5
    max_angular = 1
    base_controller = MobileBaseControl(KP_linear=KP_linear, KP_angular=KP_angular, 
                                        max_linear=max_linear, max_angular=max_angular, alpha=0.8)

    # Handler to log and exit at the end
    def signal_handler(sig, frame):
        state_estimator.stop()
        zmq_sender.send_command(np.zeros(3), np.zeros(3))
        zmq_sender.close()

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
    while state_estimator.time < 1000:
        
        times.append(state_estimator.time)

        # Estimate and control robot
        state_estimator.update_state()
        if switch.isTracking:
            target_linear_velocity = np.concatenate((state_estimator.kf.x[:2], np.zeros(1)))
            # target_position = np.concatenate((state_estimator.kf.x[2:4], np.zeros(1)))
            command_linear_velocity, command_angular_velocity = base_controller.velocity_tracking(target_linear_velocity, state_estimator.angular_velocity)
            # command_linear_velocity, command_angular_velocity = base_controller.position_tracking(target_position, (R.from_quat(state_estimator.quaternion)*switch.zero_orientation).as_quat())
        else:
            command_linear_velocity, command_angular_velocity = np.zeros(3), np.zeros(3)
        zmq_sender.send_command(command_linear_velocity, command_angular_velocity)

        # Print and log
        np.set_printoptions(precision=3, suppress=True)
        print(f"Time:{state_estimator.time:.2f}, Position: {state_estimator.kf.x[2:4]}, Velocity: {state_estimator.kf.x[:2]}, Command: {command_linear_velocity[0]:.2f}, {command_angular_velocity[2]:.2f}")

        accelerations.append(state_estimator.linear_acceleration)
        angular_velocities.append(state_estimator.angular_velocity)
        quaternions.append(state_estimator.quaternion)
        velocities.append(state_estimator.optical_flow)
        positions.append(state_estimator.kf.x[2:4])

        time.sleep(0.001)

    signal_handler(None, None)
    



