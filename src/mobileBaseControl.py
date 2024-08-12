from scipy.spatial.transform import Rotation as R
import numpy as np

class MobileBaseControl:
    
    '''
    Mobile base controller class

    args:
    K_linear: float, linear velocity gain
    K_angular: float, angular velocity gain
    max_linear: float, maximum linear velocity [m/s]
    max_angular: float, maximum angular velocity [rad/s]

    return:
    command_linear_velocity: float, linear velocity command [m/s]
    '''

    def __init__(self, K_linear, K_angular, max_linear, max_angular) -> tuple:

        self.K_linear = K_linear
        self.K_angular = K_angular

        self.max_linear = max_linear
        self.max_angular = max_angular


    def position_tracking(self, target_position, target_orientation):

        euler_orientation = R.from_quat(target_orientation).as_euler('xyz', degrees=False)
        horizontal_position = target_position[0:2]
        
        command_linear_velocity = self.K_linear*horizontal_position
        command_angular_velocity = self.K_angular*euler_orientation

        command_linear_velocity = np.clip(command_linear_velocity, -self.max_linear, self.max_linear)
        command_angular_velocity = np.clip(command_angular_velocity, -self.max_angular, self.max_angular)

        return command_linear_velocity, command_angular_velocity
    

    def velocity_tracking(self, target_velocity, target_angular_velocity):

        command_linear_velocity = self.K_linear*target_velocity
        command_angular_velocity = self.K_angular*target_angular_velocity

        command_linear_velocity = np.clip(command_linear_velocity, -self.max_linear, self.max_linear)
        command_angular_velocity = np.clip(command_angular_velocity, -self.max_angular, self.max_angular)

        return command_linear_velocity, command_angular_velocity