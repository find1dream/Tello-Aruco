import cv2

aruco = cv2.aruco

# DICT_4X4_50は4ｘ4の格子でマーカ作成、ID50個
# drawMarker(dictionary, marker ID, marker_size[pix])
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
marker = aruco.drawMarker(dictionary, 4, 100)

cv2.imwrite('ar_marker.png', marker)

img = cv2.imread('ar_marker.png')
#img = cv2.resize(img, None, fx=0.05, fy=0.05)

corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)

aruco.drawDetectedMarkers(img, corners, ids)
cv2.imwrite('DetectedMarkers.png', img)
