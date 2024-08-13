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

base_states = []
base_controls = []
times = []

linear_speed = 0.3
angular_speed = -np.pi/2 #*1.1*1.4
while tNow < 24:

    if tNow < 5:
        command_linear_velocity = np.array([linear_speed, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 6:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, angular_speed])

    elif tNow < 11:
        command_linear_velocity = np.array([linear_speed, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 12:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, angular_speed])

    elif tNow < 17:
        command_linear_velocity = np.array([linear_speed, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    elif tNow < 18:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, angular_speed])

    elif tNow < 23:
        command_linear_velocity = np.array([linear_speed, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    # command_linear_velocity = np.array([0.0, 0.0, 0.0])
    # if tNow<2: command_angular_velocity = np.array([0.0, 0.0, np.pi/8])
    # elif tNow<4: command_angular_velocity = np.array([0.0, 0.0, np.pi/4])
    # elif tNow<6: command_angular_velocity = np.array([0.0, 0.0, np.pi/2])
    # elif tNow<8: command_angular_velocity = np.array([0.0, 0.0, np.pi])

    else:
        command_linear_velocity = np.array([0.0, 0.0, 0.0])
        command_angular_velocity = np.array([0.0, 0.0, 0.0])

    print(command_linear_velocity[0], command_angular_velocity[2])

    tracer.SetMotionCommand(linear_vel=command_linear_velocity[0], angular_vel=command_angular_velocity[2])
    
    tNow = time.time() - t0

    base_controls.append([command_linear_velocity[0], command_angular_velocity[2]])
    base_states.append([tracer.GetLinearVelocity(), tracer.GetAngularVelocity()])
    times.append(tNow)
    
import datetime
file_name = datetime.datetime.now().strftime("%m_%d_%Y-%I:%M%p:%S.csv")
with open(f"log/{file_name}", "w") as f:
    f.write("Time [s],State Linear velocity [m/s],State Angular velocity [rad/s],Control Linear velocity [m/s],Control Angular velocity [rad/s]\n")

    for t, base_state, base_control in zip(times, base_states, base_controls):
        f.write(f"{t}, {base_state[0]}, {base_state[1]}, {base_control[0]}, {base_control[1]}\n")
