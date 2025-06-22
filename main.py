import cv2 as cv
import time
import numpy

# helper scripts
import arucoHandling



# open default camera
cam = cv.VideoCapture(0)
print("Starting Camera feed capture")

aruco_mark_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
arucoHandling.generate_aruco_images(aruco_mark_dict)
det_param = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(aruco_mark_dict, det_param)

if not cam.isOpened():
    print("Cannot open camera")
    exit()

# declared variables
existing_mark_dict = dict()


while (cam.isOpened):
    ret, frame = cam.read()
    corners = list()

    # Image processing
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    if (len(corners) > 0):
        # evaluate one marker for position and rotational info
        curr_point = [0, 0]
        for points in corners[0][0]:
            curr_point[0] += points[0]
            curr_point[1] += points[1]

        curr_point[0] = curr_point[0] / 4
        curr_point[1] = curr_point[1] / 4
        print("printing out corners for marker: ", ids[0], 
                "marker pos: ", curr_point[0], " ", curr_point[1])
        for curr_id in ids:
            if len(existing_mark_dict) == 0:
                existing_mark_dict[curr_id] = [0, 0]
#            elif existing_mark_dict.get(curr_id) is None:


    cv.aruco.drawDetectedMarkers(frame, corners, ids)
    if ret == True:
        cv.imshow("Display window", frame)

    if cv.waitKey(1) == ord('q'):
        # key to exit
        print("Gracefully shutting down")
        break
    
cam.release
cv.destroyAllWindows()