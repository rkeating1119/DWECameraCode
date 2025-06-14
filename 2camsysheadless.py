import cv2
import time
import datetime
import os

# -- Camera Parameters --
CAM_DEVICE_MAP = {
    1: 0,  # Camera 1 -> /dev/video0
    2: 2   # Camera 2 -> /dev/video2
}

WIDTH = 1920
HEIGHT = 1080
FPS = 30
MJPG = cv2.VideoWriter_fourcc(*'MJPG')

# Base Output Directory
BASE_OUTPUT_DIR = "/home/summerfieldwork/Main/savedrecordings"

# Recording duration (in seconds)
INTERVAL_SECONDS = 1800  # 30 minutes

def get_output_filename(label):
    cam_folder = f"cam{label}"
    output_dir = os.path.join(BASE_OUTPUT_DIR, cam_folder)
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return os.path.join(output_dir, f"recording_cam{label}_{timestamp}.avi")

print('Starting video recording from both cameras :}')

cams = {}
outs = {}
start_times = {}
active_cams = {1, 2}

# Initialize both cameras
for label, device_index in CAM_DEVICE_MAP.items():
    cam = cv2.VideoCapture(device_index)
    cam.set(cv2.CAP_PROP_FOURCC, MJPG)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cam.set(cv2.CAP_PROP_FPS, FPS)
    time.sleep(2)

    if not cam.isOpened():
        print(f'Error: Could not open Camera {label} (device {device_index}) :{{')
        cams[label] = None
        outs[label] = None
        continue

    filename = get_output_filename(label)
    out = cv2.VideoWriter(filename, MJPG, FPS, (WIDTH, HEIGHT))
    print(f"Recording started on Camera {label}: {filename}")
    cams[label] = cam
    outs[label] = out
    start_times[label] = time.time()

# Main recording loop
while active_cams:
    for label in list(active_cams):
        cam = cams[label]
        out = outs[label]
        if cam is None or out is None:
            active_cams.discard(label)
            continue

        ret, frame = cam.read()
        if not ret:
            print(f'Error: Frame capture failed on Camera {label} :{{')
            active_cams.discard(label)
            continue

        # Overlay timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, f'Recording - Camera {label}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, timestamp, (10, HEIGHT - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2, cv2.LINE_AA)

        out.write(frame)

        # Check if it's time to rotate to a new file
        current_time = time.time()
        if current_time - start_times[label] >= INTERVAL_SECONDS:
            out.release()
            filename = get_output_filename(label)
            outs[label] = cv2.VideoWriter(filename, MJPG, FPS, (WIDTH, HEIGHT))
            start_times[label] = current_time
            print(f"Started new clip for Camera {label}: {filename}")

# Cleanup (technically unreachable in this loop unless you build in a stop signal)
for label in cams:
    if cams[label]:
        cams[label].release()
    if outs[label]:
        outs[label].release()

print("All recordings finished. Exiting.")
