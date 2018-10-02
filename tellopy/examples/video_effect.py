import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time


def main():
    drone = tellopy.Tello()

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(drone.get_video_stream())
        # skip first 300 frames
        #frame_skip = 300



        while True:
            i = 0
            for frame in container.decode(video=0):
                print(i)
                i=i+1
                if i>300: #skip first 300 frames
                    if i%4==0: #do only 1/4 frames
                        im = numpy.array(frame.to_image())
                        im = cv2.resize(im, (320,240)) #resize frame
                        image = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
                        cv2.imshow('Original', image)
                        #cv2.imshow('Canny', cv2.Canny(image, 100, 200))
                        if cv2.waitKey(30) == 27:
                            name = str(i) + ".png"
                            cv2.imwrite(name,image)
 #       while True:
 #           for frame in container.decode(video=0):
 #               if 0 < frame_skip:
 #                   frame_skip = frame_skip - 1
 #                   continue
 #               start_time = time.time()
 #               image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
 #               cv2.imshow('Original', image)
 #               #cv2.imshow('Canny', cv2.Canny(image, 100, 200))
 #               cv2.waitKey(1)
 #               frame_skip = int((time.time() - start_time)/frame.time_base)

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
