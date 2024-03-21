from __future__ import annotations
import datetime
import subprocess
import time

import cv2
import numpy as np
import pyrealsense2 as rs

# Definitions
def mean_depth_of_rectangle(rect):
        depth_values = []

        # from 1/4 to 3/4 of the height
        for x in range(rect[0] + rect[2] // 4, rect[0] + 3 * rect[2] // 4 + 1):
            for y in range(rect[1] + rect[3] // 4, rect[1] + 3 * rect[3] // 4 + 1):
                point = (x, y)
                depth_point = rs.rs2_project_color_pixel_to_depth_pixel(
                    depth_frame.get_data(), depth_scale,
                    depth_min, depth_max,
                    depth_intrin, color_intrin, depth_to_color_extrin, color_to_depth_extrin, point
                    )
                try:
                    depth_values.append(depth_image[int(depth_point[0])][int(depth_point[1])])
                except IndexError:
                    pass
        return np.mean(np.array(depth_values))

Speed: float
Omega: float
Rho: float

def drive_right(rate: float = 1.0):
    global Speed, Rho, Omega, text
    Speed = 0
    if SIDEWAYS_IS_OMEGA:
        Rho = 0
        Omega = -SIDEWAYS_SPEED * rate
    else:
        Rho = -SIDEWAYS_SPEED * rate
        Omega = 0
    text = "W prawo"

def drive_left(rate: float = 1.0):
    global Speed, Rho, Omega, text
    Speed = 0
    if SIDEWAYS_IS_OMEGA:
        Rho = 0
        Omega = SIDEWAYS_SPEED * rate
    else:
        Rho = SIDEWAYS_SPEED * rate
        Omega = 0
    text = "W lewo"

def drive_straight(rate: float = 1.0):
    global Speed, Rho, Omega, text
    Speed = SPEED * rate
    Rho = 0
    Omega = 0
    text = "Prosto"


# Actual code starts here
TESTING: bool = False
MANUAL_SPEED_CONTROL: bool = False

SPEED = 5  # forward speed
SIDEWAYS_IS_OMEGA = True  # if True, sideways speed is applied to omega, else to rho
SIDEWAYS_SPEED = 7.5  # sideways speed
N_POINTLESS = 5  # pointless frames, skip
TIME_SIMULATION = 15  # amount of time for the simulation
# N_ITERATIONS = 30 + N_POINTLESS
ACCEPTANCE_ZONE = 20  # pixels on each side of the middle of the camera - if the middle between objects is in this zone, go straight
MIN_DISTANCE_BETWEEN_OBJECTS = 200

if not TESTING:
    from src.UART import UART

    # Start communication
    communication = UART('/dev/serial/by-id/usb-Arduino_LLC_Arduino_Nano_Every_85B4DF415153543553202020FF190F4E-if00', 115200, 1)
    communication.sendMessage(0,0,0)

if not MANUAL_SPEED_CONTROL:
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))
    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Parameters for depth checking
    depth_scale = device.first_depth_sensor().get_depth_scale()
    depth_min = 0.11 #meter
    depth_max = 1.0 #meter

    depth_intrin = pipeline_profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
    color_intrin = pipeline_profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()

    depth_to_color_extrin =  pipeline_profile.get_stream(rs.stream.depth).as_video_stream_profile().get_extrinsics_to(
        pipeline_profile.get_stream(rs.stream.color)
        )
    color_to_depth_extrin =  pipeline_profile.get_stream(rs.stream.color).as_video_stream_profile().get_extrinsics_to(
        pipeline_profile.get_stream(rs.stream.depth)
        )

    # Start streaming
    pipeline.start(config)

# Main loop
i = 0
picture_number = 0
start = time.time()
while not MANUAL_SPEED_CONTROL and time.time() - start < TIME_SIMULATION:
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not depth_frame or not color_frame or i < N_POINTLESS:
        print("Pointless frame")
        i += 1
        continue

    depth_image = np.asanyarray(depth_frame.get_data())
    depth_image = depth_image * 255 /depth_image.max()
    # cv2.imwrite(r"Test_photos/" + f"img_{i-N_POINTLESS}_depth.png", depth_image)  # Saving depth photos

    # Convert images to numpy arrays and change colorspace
    color_image = np.asanyarray(color_frame.get_data())
    color_image_base = color_image
    color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

    # Detecting color
    mask1 = cv2.inRange(color_image, (0, 160, 135), (15, 255, 255))
    mask2 =cv2.inRange(color_image, (150, 160, 135), (180, 255, 255))
    mask = cv2.bitwise_or(mask1, mask2)
    mask=cv2.medianBlur(mask,9)

    # Canny Edge Detection
    edges = cv2.Canny(image=mask, threshold1=100, threshold2=200) # Canny Edge Detection
    
    # Finding contours and filtering
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = [cv2.boundingRect(contour) for contour in contours]
    rectangles_but_good = []
    for rectangle in rectangles:
        area = rectangle[2] * rectangle[3]
        if area >= 1000 and area <= 60000:
            rectangles_but_good.append(rectangle)

    camera_middle_x = color_image.shape[1] // 2
    diff = 0
    text = "Unknown"
    if len(rectangles_but_good) > 1:
        # Decision
        rectangles_but_good.sort(key=mean_depth_of_rectangle)

        j: int = 0
        for count in rectangles_but_good:
            x,y,w,h = count
            
            # Calculate the area of the bounding box
            area = w * h
            
            # Draw the bounding box on the original image
            cv2.rectangle(color_image_base, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Display the area
            cv2.putText(color_image_base, f'Area: {area}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display a number depending on the distance
            cv2.putText(color_image_base, str(j), (x + w // 2, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            j += 1

        between_obstacles_x = rectangles_but_good[1][0] // 2 + (rectangles_but_good[0][0] + rectangles_but_good[0][2]) // 2
        obstacles_distance_between = abs(rectangles_but_good[1][0] - (rectangles_but_good[0][0] + rectangles_but_good[0][2]))  # NOWE
        cv2.putText(color_image_base, str(obstacles_distance_between), (between_obstacles_x, rectangles_but_good[1][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.line(color_image_base, (between_obstacles_x, 0), (between_obstacles_x, 480), (0, 0, 255))
        diff = between_obstacles_x - camera_middle_x

        if obstacles_distance_between > MIN_DISTANCE_BETWEEN_OBJECTS:
            if abs(diff) > ACCEPTANCE_ZONE:
                rate: float = 1.0
                if abs(diff) > 50:
                    rate = diff/50
                if diff > 0:
                    # Right
                    drive_right(rate)
                else:
                    # Left
                    drive_left(rate)
            else:
                # Straight
                drive_straight()
        else:  # The obstacles are too close - avoid both of them
            if diff > 0:
                # Left - avoiding both obstacles
                drive_left()
            else:
                # Right - avoiding both obstacles
                drive_right()
        cv2.line(color_image_base, (camera_middle_x - ACCEPTANCE_ZONE, 0), (camera_middle_x - ACCEPTANCE_ZONE, 480), (255, 0, 0))
        cv2.line(color_image_base, (camera_middle_x + ACCEPTANCE_ZONE, 0), (camera_middle_x + ACCEPTANCE_ZONE, 480), (255, 0, 0))
    elif len(rectangles_but_good) == 1:  # Only one obstacle
        obstacle_middle_x = (rectangles_but_good[0][0] + rectangles_but_good[0][2]) // 2
        diff = obstacle_middle_x - camera_middle_x
        if diff < 0:
            drive_right()
        else:
            drive_left()
    else:
        drive_straight()

    if not TESTING:
        communication.sendMessage(Speed, Rho, Omega)
    # time.sleep(0.2)
    end = time.time()
    print('Current time: ',end - start)
    cv2.putText(color_image_base, text, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    if (time.time() - start) > picture_number * 0.2:
        cv2.imwrite(r"Test_photos/" + f"img_{picture_number}.png", color_image_base)
        cv2.imwrite(r"Color_photos/" + f"img_{picture_number}.png", mask)
        cv2.imwrite(r"Blur_photos/" + f"img_{picture_number}.png", edges)
        picture_number += 1
    if TESTING:
        cv2.imshow("Detekcja", color_image_base)
        cv2.waitKey(1)

if MANUAL_SPEED_CONTROL:
    Speed = 0  # Straight
    Rho = 0  # Sideways
    Omega = 0  # Rotation
    start = time.time()
    communication.sendMessage(Speed, Rho, Omega)
    while time.time() - start < 10:
        print(time.time() - start)

if not MANUAL_SPEED_CONTROL:
    pipeline.stop()
# Resetting
if not TESTING:
    for _ in range(5):
        communication.sendMessage(0, 0, 0)
        time.sleep(0.1)
# subprocess.run(["ffmpeg", "-framerate", "5", "-start_number", "0", "-i", r"Test_photos/img_%d.png", "-c:v", "libx264", 
#                 "-r", "30", f"Test_photos/output{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"])
