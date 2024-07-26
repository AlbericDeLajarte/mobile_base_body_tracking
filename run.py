from src.markerPose import MarkerPose
from src.mobileBaseControl import MobileBaseControl

import time
import numpy as np
from scipy.spatial.transform import Rotation as R

if __name__ == '__main__':
    
    # Create an instance of the MarkerPose class
    marker_pose = MarkerPose(camera_calibration='calibration/calibration_chessboard.yaml', marker_len=8.17e-2, alpha=0.7)
    base_controller = MobileBaseControl(K_linear=2, K_angular=1, max_linear=0.5, max_angular=1)

    while True:

        # Get the position and orientation of the marker
        position, orientation = marker_pose.get_marker_pose()

        # Get the desired velocity of the mobile base
        linear_velocity, angular_velocity = base_controller.control_velocity(position, orientation)

        # Print observation and control
        np.set_printoptions(precision=2, suppress=True)
        print(f"Position: {position*100.}, Orientation: {R.from_quat(orientation).as_euler('xyz', degrees=True)}")
        print(f"Linear velocity: {linear_velocity*100.}, Angular velocity: {np.degrees(angular_velocity):.2f}")
        print("----")

        # Wait for 1 second
        time.sleep(0.1)