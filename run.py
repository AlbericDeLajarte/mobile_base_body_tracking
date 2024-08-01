from src.markerPose import MarkerPose
from src.mobileBaseControl import MobileBaseControl

import time
import numpy as np
from scipy.spatial.transform import Rotation as R

import pyagxrobots
import time

import cv2

if __name__ == '__main__':

    tracer = pyagxrobots.pysdkugv.TracerBase()
    tracer.EnableCAN()
    tracer.EnableCAN()
    
    # Create an instance of the MarkerPose class
    marker_pose = MarkerPose(camera_calibration='calibration/calibration_chessboard.yaml', marker_len=8.17e-2, alpha=0.5)
    base_controller = MobileBaseControl(K_linear=1.5, K_angular=1.5, max_linear=0.5, max_angular=1)

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

        # Wait for 1 second
        time.sleep(0.1)

cv2.destroyAllWindows()