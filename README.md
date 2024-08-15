# mobile_base_body_tracking

## Description
This repository is used to control the position of a mobile base by following the motion of a human.
It contains two demos:
- `run_markerPositionTracker.py`: To run on the robot computer, will track a marker held by the user to keep the same realtive position and orientation between the robot and user
- `run_velocityTrackerServer.py` and `run_velocityTrackerClient.py`: The server runs on the robot and the client on the teleoperator's computer. Here the velocity of the teleoperator is estimated with an IMU and optical flow, then sent as commands to the robot

## Installation
For both demos:
```
pip install -r requirements.txt
```

## Calibration
In the folder `calibration/`
Run the script `webcam_photo.py` to collect multiple pictures of a chessboard using the image `pattern.png`. The parameters of the chessboard have to be adjusted in the script. Press space for each new picture, and esc to stop.

```
cd calibration
python webcam_photo.py
```

Then run the script `calibration.py` to compute the calibration matrix and save it in `calibration_chessboard.yaml`

## Run
sudo ip link set can0 up type can bitrate 500000
Just run the script `run.py` to get the pose of the marker `ARUCO.pdf` and compute target velocity
