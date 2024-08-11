import numpy as np

class KalmanFilter():

    def __init__(self, sigma_a, sigma_opt):

        self.x = np.array([0, 0, 0, 0]) # [vx, vy, px, py]
        self.P = np.eye(4)*0.0

        self.sigma_a = sigma_a
        self.sigma_opt = sigma_opt

        self.update_matrices(0.0)
    

    def update_matrices(self, dT):

        self.Fk = np.array([[1,     0,  0,  0],
                            [0,     1,  0,  0],
                            [dT,    0,  1,  0],
                            [0,     dT, 0,  1]])
        
        self.Bk = np.array([[dT,        0],
                            [0,         dT],
                            [0.5*dT**2, 0],
                            [0,         0.5*dT**2]])
        
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
        
        self.Q = np.array([ [dT,    0,  0,          0],
                            [0,     dT, 0,          0],
                            [0,     0,  0.5*dT**2,  0],
                            [0,     0,  0,          0.5*dT**2]])*self.sigma_a
        
        self.R = np.eye(2)*self.sigma_opt


    def predict(self, dT, acceleration):
        self.update_matrices(dT)

        self.x = self.Fk @ self.x + self.Bk @ acceleration
        self.P = self.Fk @ self.P @ self.Fk.T + self.Q

    def update(self, optical_flow):
        y = optical_flow - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

kf = KalmanFilter(sigma_a=1.5e-3, sigma_opt=1e-2)
