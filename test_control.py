from src.mobileBaseControl import MobileBaseControl

import numpy as np
import time

from tqdm import tqdm


import pyagxrobots

tracer = pyagxrobots.pysdkugv.TracerBase()
tracer.EnableCAN()
tracer.EnableCAN()
tracer.EnableCAN()

# Control parameters
K_linear = 1
K_angular = 1
max_linear = 0.4
max_angular = 1

base_controller = MobileBaseControl(K_linear=K_linear, K_angular=K_angular, max_linear=max_linear, max_angular=max_angular)

t0 = time.time()
tNow = time.time() - t0
while tNow < 20:

    if tNow < 4:
        command_linear_velocity = np.array([0.5, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 5:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, np.pi/2])

    elif tNow < 9:
        command_linear_velocity = np.array([0.5, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 10:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, np.pi/2])

    elif tNow < 14:
        command_linear_velocity = np.array([0.5, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 15:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, np.pi/2])

    elif tNow < 19:
        command_linear_velocity = np.array([0.5, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    else:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    tracer.SetMotionCommand(linear_vel=command_linear_velocity[0], angular_vel=command_angular_velocity[2])
    tNow = time.time() - t0

