import cv2
import numpy as np

aruco = cv2.aruco

# WEBカメラ
cap = cv2.VideoCapture(1)

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()
# CORNER_REFINE_NONE, no refinement. CORNER_REFINE_SUBPIX, do subpixel refinement. CORNER_REFINE_CONTOUR use contour-Points
#parameters.cornerRefinementMethod = aruco.CORNER_REFINE_CONTOUR

cameraMatrix = np.load('mtx.npy')
distCoeffs = np.load('dist.npy')

cap.set(cv2.CAP_PROP_FPS, 10)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

board = aruco.GridBoard_create(2, 3, 0.0485, 0.03, dictionary)

def main():

    ret, frame = cap.read()

    # 変換処理ループ
    while ret == True:
        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, dictionary, parameters=parameters)
        #print(corners)
        #print(ids)
        #print(rejectedImgPoints)

        aruco.drawDetectedMarkers(frame, corners, ids, (0,255,0))


        # int valid = estimatePoseBoard(corners, ids, board, cameraMatrix, distCoeffs, rvec, tvec);
        retval, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, cameraMatrix, distCoeffs)

        if retval != 0:
            aruco.drawAxis(frame, cameraMatrix, distCoeffs, rvec, tvec, 0.1)

        cv2.imshow('org', frame)

        # Escキーで終了
        key = cv2.waitKey(50)
        if key == 27: # ESC
            break

        # 次のフレーム読み込み
        ret, frame = cap.read()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
