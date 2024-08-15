import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kalman import KalmanFilter
from IMU import IMU
from opticalFlow import OpticalFlow

import multiprocessing
import numpy as np
from scipy.spatial.transform import Rotation as R

import time

from pynput import keyboard

class Estimator2D:
    def __init__(self, path_imu: str, path_optical_flow: str) -> None:

        self.kf = KalmanFilter(sigma_a=1.5e-3, sigma_opt=2e-3)

        self.gravity = np.array([0, 0, 9.81])

        self.path_imu = path_imu
        self.path_optical_flow = path_optical_flow

        # self.imu = IMU(path_imu)
        # self.optical_flow = OpticalFlow(path_optical_flow)
        
        # object for sharing data between processes
        self.manager = multiprocessing.Manager()
        self.sensor_data = self.manager.Namespace()
        self.sensor_data.acceleration = self.manager.list([0.0, 0.0, 1.0])
        self.sensor_data.angular_velocity = self.manager.list([0.0, 0.0, 0.0])
        self.sensor_data.quaternion = self.manager.list([0.0, 0.0, 0.0, 1.0])
        self.sensor_data.optical_flow = self.manager.list([0.0, 0.0, 0.0]) # vx, vy, height
        self.sensor_data.update_opticalFlow = self.manager.Value('i', 0)

        # State vector
        self.linear_acceleration = np.zeros(3)
        self.angular_velocity = np.zeros(3)
        self.quaternion = np.array([0.0, 0.0, 0.0, 1.0])
        self.optical_flow = np.zeros(3)
        self.kalman_state = np.zeros(4)

        self.time = 0.0
        self.t0 = time.time()


        # Start processes
        self.imu_process = multiprocessing.Process(target=imu_update, args=(self.path_imu, self.sensor_data))
        self.optical_flow_process = multiprocessing.Process(target=optical_flow_update, args=(self.path_optical_flow, self.sensor_data))

        self.imu_process.start()
        self.optical_flow_process.start()


    def update_state(self):
        
        # Update time
        new_time = time.time() - self.t0
        dt = new_time - self.time
        self.time = new_time

        # Update IMU
        self.linear_acceleration = np.array(self.sensor_data.acceleration)*self.gravity[2]
        self.angular_velocity = np.deg2rad(self.sensor_data.angular_velocity)
        self.quaternion = np.array(self.sensor_data.quaternion)

        # Rotate the acceleration to the world frame
        r = R.from_quat(self.quaternion)
        self.linear_acceleration = self.linear_acceleration - r.inv().apply(self.gravity)

        # Update the Kalman filter
        self.kf.predict(dt, self.linear_acceleration[:2])

        # Update Optical Flow
        if self.sensor_data.update_opticalFlow:
            angle_vertical = np.arccos(r.as_matrix()[2, 2])
            self.optical_flow = np.array(self.sensor_data.optical_flow)

            self.optical_flow[2] = self.optical_flow[2]*np.cos(angle_vertical)
            self.optical_flow[:2] *= 2*self.optical_flow[2] # experimental calibration

            self.optical_flow[0] -= (-self.angular_velocity[1]*self.optical_flow[2] +self.angular_velocity[2]*0.33)
            self.optical_flow[1] -= self.angular_velocity[0]*self.optical_flow[2]

            self.kf.update(self.optical_flow[:2])

            self.sensor_data.update_opticalFlow = 0


    def stop(self):
        self.imu_process.terminate()
        self.optical_flow_process.terminate()


    
def imu_update(path_imu, sensor_data):

    imu = IMU(path_imu)
    imu.update()
    while True:
        imu.update()
        sensor_data.acceleration[:] = imu.acceleration.tolist()
        sensor_data.angular_velocity[:] = imu.angular_velocity.tolist()
        sensor_data.quaternion[:] = imu.quaternion.tolist()


def optical_flow_update(path_optical_flow, sensor_data):
        
        optical_flow = OpticalFlow(path_optical_flow, alpha=0.9)
        while True:
            optical_flow.update()
            sensor_data.optical_flow[:2] = optical_flow.velocity.tolist()
            sensor_data.optical_flow[2] = optical_flow.altitude
            sensor_data.update_opticalFlow = 1



class trackerSwitch:
    def __init__(self, observer, key='X'):
        self.observer = observer
        self.key = key
        self.isTracking = False
        self.zero_orientation = R.from_quat(np.array([0, 0, 0, 1]))

        self.listener = keyboard.Listener(on_press=self.switch_tracker)
        self.listener.start()


    def switch_tracker(self, key):

        try:
            if key.char == 'q':
                self.isTracking = not self.isTracking
                self.observer.kf.x = np.zeros(4)
                self.zero_orientation = R.from_quat(self.observer.quaternion).inv()
        except AttributeError:
            pass  # Special keys (like arrow keys) don't have a 'char' attribute


if __name__ == "__main__":

    # init estimator and controller
    state_estimator = Estimator2D(path_imu="/dev/tty.usbserial-110", path_optical_flow="/dev/tty.usbserial-0001")

    for i in range(1000):
        state_estimator.update_state()
        np.set_printoptions(precision=3, suppress=True)
        print(f"Time:{state_estimator.time:.2f}, Position: {state_estimator.kf.x[2:4]}, Velocity: {state_estimator.kf.x[:2]}")
        time.sleep(0.01)

    state_estimator.stop()