from src.estimator2D import Estimator2D
import numpy as np
import time

from tqdm import tqdm

if __name__ == '__main__':

    state_estimator = Estimator2D(path_imu="/dev/tty.usbserial-210", path_optical_flow="/dev/tty.usbserial-0001")

    accelerations = []
    velocities = []
    quaternions = []
    angular_velocities = []
    times = []
    t0 = time.time()
    # for _ in tqdm(range(3000)):
    for _ in range(10000):
        
        times.append(time.time()-t0)

        state_estimator.update_state()

        np.set_printoptions(precision=3, suppress=True)
        # print(f"{time.time()-t0:.3f}", state_estimator.linear_acceleration, state_estimator.optical_flow)
        print(f"Position: {state_estimator.kf.x[2:4]}, Velocity: {state_estimator.kf.x[0:2]}")


        accelerations.append(state_estimator.linear_acceleration)
        angular_velocities.append(state_estimator.angular_velocity)
        quaternions.append(state_estimator.quaternion)
        velocities.append(state_estimator.optical_flow)

        time.sleep(0.001)
    state_estimator.stop()
    # Log
    with open("log/data_sensor_new.csv", "w") as f:
        f.write("Time [s],Acceleration X [m/s^2],Acceleration Y [m/s^2],Acceleration Z [m/s^2],Angular velocity X [rad/s],Angular velocity Y [rad/s],Angular velocity Z [rad/s],Quaternion X,Quaternion Y,Quaternion Z,Quaternion W,Velocity X [m/s],Velocity Y [m/s]\n")
        for t, acceleration, angular_velocity, quaternion, velocity in zip(times, accelerations, angular_velocities, quaternions, velocities):
            f.write(f"{t},{acceleration[0]},{acceleration[1]},{acceleration[2]},{angular_velocity[0]},{angular_velocity[1]},{angular_velocity[2]},{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]},{velocity[0]},{velocity[1]}\n")



