from src.markerPose import MarkerPose
from src.mobileBaseControl import MobileBaseControl

import time
import numpy as np
from scipy.spatial.transform import Rotation as R

import pyagxrobots
import time
import datetime

import sys
import signal

import cv2

if __name__ == '__main__':

    tracer = pyagxrobots.pysdkugv.TracerBase()
    tracer.EnableCAN()
    tracer.EnableCAN()
    tracer.EnableCAN()

    # Control parameters
    K_linear = 3
    K_angular = 1.5
    max_linear = 0.4
    max_angular = 1
    
    alpha_estimation = 0.5
    alpha_control = 1

    marker_len = 131.1e-3
    base_states = []
    base_controls = []
    times = []

    def signal_handler(sig, frame):
        file_name = datetime.datetime.now().strftime("%m_%d_%Y-%I:%M%p:%S.csv")
        with open(f"log/{file_name}", "w") as f:
            f.write(f"K_linear: {K_linear}, K_angular: {K_angular}, max_linear: {max_linear}, max_angular: {max_angular}, alpha_estimation: {alpha_estimation}, alpha_control: {alpha_control}, marker_len: {marker_len}\n\n")
            f.write("Time [s],State Linear velocity [m/s],State Angular velocity [rad/s],Control Linear velocity [m/s],Control Angular velocity [rad/s]\n")

            for time, base_state, base_control in zip(times, base_states, base_controls):
                f.write(f"{time}, {base_state[0]}, {base_state[1]}, {base_control[0]}, {base_control[1]}\n")
        sys.exit(0)

    # Register hook to log and exit at the end
    signal.signal(signal.SIGINT, signal_handler)

    # Create an instance of the MarkerPose class
    marker_pose = MarkerPose(camera_calibration='calibration/calibration_chessboard.yaml', marker_len=marker_len, alpha=alpha_estimation)
    base_controller = MobileBaseControl(K_linear=K_linear, K_angular=K_angular, max_linear=max_linear, max_angular=max_angular)

    t0 = time.time()
    while True:

        # ret, frame = marker_pose.cap.read()
        # if ret: 
        #     imS = cv2.resize(frame, (960, 540)) 
        #     cv2.imshow("test", imS)

        # Get the position and orientation of the marker
        position, orientation = marker_pose.get_marker_pose()

        # Get the desired velocity of the mobile base
        linear_velocity, angular_velocity = base_controller.control_velocity(position, orientation)


        # Print observation and control
        np.set_printoptions(precision=2, suppress=True)
        print(f"Position: {position*100.}, Orientation: {R.from_quat(orientation).as_euler('xyz', degrees=True)}")
        print(f"Linear velocity: {linear_velocity}, Angular velocity: {(angular_velocity):.2f}")
        print("----")

        tracer.SetMotionCommand(linear_vel=linear_velocity[0], angular_vel=angular_velocity)

        # Save data
        times.append(time.time()-t0)
        base_controls.append([linear_velocity[0], angular_velocity])
        base_states.append([tracer.GetLinearVelocity(), tracer.GetAngularVelocity()])

        # Wait for 1 second
        # time.sleep(0.1)

cv2.destroyAllWindows()