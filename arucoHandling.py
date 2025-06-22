import cv2 as cv

def generate_aruco_images(aruco_mark_dict):
    marker_image = cv.aruco.generateImageMarker(aruco_mark_dict, 23, 200, 1)
    cv.imwrite("marker23.png", marker_image)