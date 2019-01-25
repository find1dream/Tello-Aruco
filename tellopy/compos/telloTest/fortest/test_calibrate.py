
import cv2
from cv2 import aruco
import numpy as np
import glob
# Set this flsg True for calibrating camera and False for validating results real time
Calibrate_camera = True

# Set number of images taken using data_generation script.
numberOfImages = 41


# For validating results, show aruco board to camera.



aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )


#Provide length of the marker's side
markerLength = 3.3  # Here, measurement unit is centimetre.

# Provide separation betwee n markers
markerSeparation = 0.35   # Here, measurement unit is centimetre.



# create arUco board
board = aruco.GridBoard_create(5, 7, markerLength, markerSeparation, aruco_dict)


'''uncomment following block to draw and show the board'''
#img = board.draw((864,1080))
#cv2.imshow("aruco", img)




arucoParams = aruco.DetectorParameters_create()

if Calibrate_camera == True:
    
    img_list = []
    i = 0
    for path in glob.glob('*.png'):
        img = cv2.imread(path)
        img_list.append(img)
        h, w, c = img.shape

    counter = []
    corners_list = []
    id_list = []
    first = True
    for im in img_list:
    
        img_gray = cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img_gray, aruco_dict, parameters=arucoParams)
        if first == True:
            corners_list = corners
            print(type(corners))
            id_list = ids
            first = False
        else:
            corners_list = np.vstack((corners_list, corners))
            id_list = np.vstack((id_list,ids))
        counter.append(len(ids))
    
    counter = np.array(counter)
    print ("Calibrating camera .... Please wait...")
    #mat = np.zeros((3,3), float)
    ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraAruco(corners_list, id_list, counter, board, img_gray.shape, None, None )

    np.save('mtx.npy', mtx)
    np.save('dist.npy', dist)
    #print("Camera matrix is \n", mtx, "\n And is stored in calibration.yaml file along with distortion coefficients : \n", dist)
    #data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}
    #print(data)

else :

    camera = cv2.VideoCapture(0)
    ret, img = camera.read()


    with open('calibration.yaml') as f:
        loadeddict = yaml.load(f)
    mtx = loadeddict.get('camera_matrix')
    dist = loadeddict.get('dist_coeff')
    mtx = np.array(mtx)
    dist = np.array(dist)

    ret, img = camera.read()
    img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    h,  w = img_gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))



    pose_r = []
    pose_t = []
    count = 0
    while True:
        ret, img = camera.read()
        img_aruco = img
        im_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        h,  w = im_gray.shape[:2]
        dst = cv2.undistort(im_gray, mtx, dist, None, newcameramtx)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(dst, aruco_dict, parameters=arucoParams)
        #cv2.imshow("original", img_gray)
        if corners == None:
            print ("pass")
        else:

            ret, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, newcameramtx, dist) # For a board
            print ("Rotation ", rvec, "Translation", tvec)
            if ret != 0:
                img_aruco = aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))
                img_aruco = aruco.drawAxis(img_aruco, newcameramtx, dist, rvec, tvec, 10)    # axis length 100 can be changed according to your requirement


            if cv2.waitKey(0) & 0xFF == ord('q'):

                break;
        cv2.imshow("World co-ordinate frame axes", img_aruco)





cv2.destroyAllWindows()
