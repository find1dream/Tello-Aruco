import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time
import threading

frameA = None
run_recv_thread = True
def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

def init_logger():
    handler = StreamHandler()
    handler.setLevel(INFO)
    handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(INFO)

def recv_thread():
    global frameA
    global run_recv_thread
    global drone
    print('start recv_thread()')
    drone = tellopy.Tello()
    drone.connect()
    drone.wait_for_connection(60.0)
    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.set_video_encoder_rate(1)
    drone.set_loglevel(drone.LOG_WARN)
    container = av.open(drone.get_video_stream())
    run_recv_thread = True
    while run_recv_thread:
        print("haha")
        for f in container.decode(video=0):
            frameA = f
        time.sleep(0.01)

def task(v):
    getLogger().info("%s start", v)
    time.sleep(1.0)
    getLogger().info("%s end", v)

def main():
    try:
       
        threading.Thread(target = recv_thread).start()
        i = 0
        frameB = None
        while run_recv_thread:
            if frameA is None :
                time.sleep(0.1)
                print("debug: wait for video msg...")
            else:
                #time.sleep(0.1)
                #print(frameA)
            #    if i%4 == 0:
                im = numpy.array(frameA.to_image())
                #im = cv2.resize(im, (320,240)) #resize frame
                image = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
                cv2.imshow('Original', image)
                cv2.waitKey(10)
                print("debug: got frame")
#            i = 0
#            for frame in container.decode(video=0):
#                print(i)
#                i=i+1
#                if i>300: #skip first 300 frames
#                    if i%4==0: #do only 1/4 frames
#                        im = numpy.array(frame.to_image())
#                        #im = cv2.resize(im, (320,240)) #resize frame
#                        image = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
#                        cv2.imshow('Original', image)
#                        #cv2.imshow('Canny', cv2.Canny(image, 100, 200))
#                        if cv2.waitKey(30) == 27:
#                            name = str(i) + ".png"
#                            cv2.imwrite(name,image)
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
