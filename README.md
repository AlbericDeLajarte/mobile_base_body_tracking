# mobile_base_body_tracking

## Description
A simple repo to estimate the full pose of an ArUco marker and drive an omniwheel mobile base

## Installation
```
pip install -r requirements.txt
pip uninstall opencv-python
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
Just run the script `run.py` to get the pose of the marker `ARUCO.pdf` and compute target velocity
