import cv2
import numpy as np

from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp

class MarkerPose():

    '''
    Marker pose class

    args:
    camera_calibration: str, path to the camera calibration file
    marker_len: float, length of the ArUco marker [m]
    alpha: float, exponential average factor

    return:
    marker_position: np.array, position of the ArUco marker [m]
    marker_orientation: np.array, orientation of the ArUco marker [quaternion]

    '''

    def __init__(self, camera_calibration: str, marker_len: float, alpha : float = 0.9) -> None:

        self.marker_len = marker_len
        self.alpha = alpha

        # Get the camera calibration parameters
        cv_file = cv2.FileStorage(camera_calibration, cv2.FILE_STORAGE_READ) 
        self.mtx = cv_file.getNode('K').mat()
        self.dst = cv_file.getNode('D').mat()
        cv_file.release()
        

        # Load the ArUco dictionary
        self.this_aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.this_aruco_parameters = cv2.aruco.DetectorParameters_create()

        self.cap = cv2.VideoCapture(0)

        # Initialize the marker pose
        self.marker_position = np.zeros(3)
        self.marker_orientation = np.array([0, 0, 0, 1])

        self.zero_position = np.zeros(3)
        self.zero_orientation = R.from_quat([0, 0, 0, 1])

        self.calibration_counter = 0

        self.camera2robot = R.from_euler('x', -90, degrees=True) * R.from_euler('y', -90, degrees=True)


    def get_marker_pose(self) -> tuple:

        ret, frame = self.cap.read()  
     
        # Detect ArUco markers in the video frame
        (corners, marker_ids, rejected) = cv2.aruco.detectMarkers(  frame, 
                                                                    self.this_aruco_dictionary, 
                                                                    parameters=self.this_aruco_parameters,
                                                                    cameraMatrix=self.mtx, distCoeff=self.dst)
        
        # Check that at least one ArUco marker was detected
        if marker_ids is not None:
            
            # Estimate the pose of the detected marker
            rvecs, tvecs, obj_points = cv2.aruco.estimatePoseSingleMarkers( corners,
                                                                            self.marker_len,
                                                                            self.mtx,
                                                                            self.dst)

            # Get normalized position and orientation
            new_position = self.camera2robot.apply(tvecs[0][0]) - self.zero_position

            rotation_matrix = cv2.Rodrigues(np.array(rvecs[0][0]))[0]
            new_rotation = (self.camera2robot*R.from_matrix(rotation_matrix))*self.zero_orientation.inv()

            # Run calibration, if not ready return init value (0, 0)
            if not self.run_calibration(new_position, new_rotation): return (self.marker_position, self.marker_orientation)

            # Exponential average on position and orientation
            self.marker_position = (1-self.alpha)*self.marker_position + self.alpha*new_position

            previous_rotation = R.from_quat(self.marker_orientation)
            slerp_rot = Slerp([0, 1], R.concatenate([previous_rotation, new_rotation]))([self.alpha])
            self.marker_orientation = slerp_rot.as_quat()[0]



            return (self.marker_position, self.marker_orientation)

        else: return (np.zeros(3), np.array([0, 0, 0, 1]))
            

    def run_calibration(self, new_position, new_rotation) -> bool:  

        n_calibrations = 3

        if self.calibration_counter > n_calibrations: return True

        if self.calibration_counter == 0:
            self.position_calibrations = []
            self.orientation_calibrations = []
            self.calibration_counter += 1

        if self.calibration_counter < n_calibrations:
            self.position_calibrations.append(new_position)
            self.orientation_calibrations.append(new_rotation)
            self.calibration_counter += 1

        elif self.calibration_counter == n_calibrations:
            self.zero_position = np.mean(self.position_calibrations, axis=0)
            self.zero_orientation = R.mean(R.concatenate(self.orientation_calibrations))

            self.calibration_counter += 1

            del self.position_calibrations
            del self.orientation_calibrations

        return False
    

    def __del__(self):
        self.cap.release()

        




