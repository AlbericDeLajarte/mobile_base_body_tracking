from scipy.spatial.transform import Rotation as R
import numpy as np
import time

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

    def __init__(self, KP_linear, KP_angular, KI_linear=0, KI_angular=0, max_linear=1, max_angular=1, alpha=1):

        self.KP_linear = KP_linear
        self.KP_angular = KP_angular

        self.KI_linear = KI_linear
        self.KI_angular = KI_angular

        self.max_linear = max_linear
        self.max_angular = max_angular

        # Init integrator
        self.integral_linear = np.zeros(3)
        self.integral_angular = np.zeros(3)
        self.max_linear_integrator = 1 # m
        self.max_angular_integrator = 1 # rad

        # Keep in memory target and command velocities
        self.target_linear_velocity = np.zeros(3)
        self.target_angular_velocity = np.zeros(3)

        self.command_linear_velocity = np.zeros(3)
        self.command_angular_velocity = np.zeros(3)

        self.tNow = time.time()

        self.alpha = alpha


    def position_tracking(self, target_position, target_orientation):

        euler_orientation = R.from_quat(target_orientation).as_euler('xyz', degrees=False)
        horizontal_position = target_position[0:2]
        
        command_linear_velocity = self.KP_linear*horizontal_position
        command_angular_velocity = self.KP_angular*euler_orientation

        command_linear_velocity = np.clip(command_linear_velocity, -self.max_linear, self.max_linear)
        command_angular_velocity = np.clip(command_angular_velocity, -self.max_angular, self.max_angular)

        # Smooth the command
        self.command_linear_velocity = self.alpha*command_linear_velocity + (1-self.alpha)*self.command_linear_velocity
        self.command_angular_velocity = self.alpha*command_angular_velocity + (1-self.alpha)*self.command_angular_velocity

        return self.command_linear_velocity, self.command_angular_velocity
    

    def velocity_tracking(self, target_linear_velocity, target_angular_velocity, current_velocity=None, current_angular_velocity=None):

        # Compute integral term as the position drift from the last command
        if current_velocity is not None and current_angular_velocity is not None:
            dT = time.time() - self.tNow
            self.integral_linear = np.clip(self.integral_linear + (self.target_linear_velocity - current_velocity)*dT, -self.max_linear_integrator, self.max_linear_integrator)
            self.integral_angular = np.clip(self.integral_angular + (self.target_angular_velocity - current_angular_velocity)*dT, -self.max_angular_integrator, self.max_angular_integrator)
        else:
            self.integral_linear = np.zeros_like(target_linear_velocity)
            self.integral_angular = np.zeros_like(target_angular_velocity)

        # Proportional-Integral controller
        command_linear_velocity = self.KP_linear*target_linear_velocity + self.KI_linear*self.integral_linear
        command_angular_velocity = self.KP_angular*target_angular_velocity + self.KI_angular*self.integral_angular

        command_linear_velocity = np.clip(command_linear_velocity, -self.max_linear, self.max_linear)
        command_angular_velocity = np.clip(command_angular_velocity, -self.max_angular, self.max_angular)

        self.target_linear_velocity = target_linear_velocity
        self.target_angular_velocity = target_angular_velocity
        self.tNow = time.time()

        # Smooth the command
        self.command_linear_velocity = self.alpha*command_linear_velocity + (1-self.alpha)*self.command_linear_velocity
        self.command_angular_velocity = self.alpha*command_angular_velocity + (1-self.alpha)*self.command_angular_velocity

        return self.command_linear_velocity, self.command_angular_velocity