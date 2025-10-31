from picamera2 import Picamera2
import cv2
import time
import numpy

# helper scripts
import arucoHandling

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

aruco_mark_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
arucoHandling.generate_aruco_images(aruco_mark_dict)
det_param = cv2.aruco.DetectorParameters_create()

existing_mark_dict = dict()

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_mark_dict, parameters=det_param)

    if ids is not None:
        curr_point = [0, 0]
        for points in corners[0][0]:
            curr_point[0] += points[0]
            curr_point[1] += points[1]
        curr_point[0] /= 4
        curr_point[1] /= 4

        print(f"Marker {ids[0]} position: {curr_point}")

        for curr_id in ids:
            if curr_id[0] not in existing_mark_dict:
                print(type(curr_id[0]))
                existing_mark_dict[curr_id[0]] = [0, 0]

    cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Gracefully shutting down")
        break

picam2.stop()
cv2.destroyAllWindows()
