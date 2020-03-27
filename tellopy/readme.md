I will show you two types of installations: bottom-facing camera version and mirror version. 

## 1. Installation for bottom-facing camera
### 1.1 Tello with another camera.
#### 1.1.1 camera
This is the camera I used for this tutorial.
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4407.jpg)

![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4425.JPG)

You can choose similar analog cameras, which also should work.

#### 1.1.2 source for camera
Here I just use the source from circuit board of Tello.
![Initial state](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4408.jpg)

And then disasemble the drone.
![Disassembled Tello](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4411.jpg)

Here is the power outlet.
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4412.jpg)

And then weld the lead.
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4414.jpg)
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4415.jpg)
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4416.jpg)

Last, test the voltage, 3.667v is enough for the camera
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4417.jpg)


#### 1.1.3 attach the camera
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4419.jpg)
I used a glue gun to fix the camera
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4420.jpg)
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4421.jpg)
Load the battery, and the red led turns on.
![](https://github.com/find1dream/Tello-Aruco/blob/master/tellopy/photo/IMG_4423.jpg)
That's all for the Tello part


## 2. Calibration for the camera
Since the part is heavily depends on the hardware, so I suggest you first find out why and how to calibrate the camera on the net, and then you can refer to the code in [here](https://github.com/find1dream/Tello-Aruco/tree/master/tellopy/compos/camPara) to perform the calibration.

Last you will get `.npy` and `mtx.npy` two files that will be inputted into `cv2.aruco`


## 3. Library installation
1. preliminary
```python
sudo pip install av
sudo pip install image
sudo pip install opencv-contrib-python
```

2. go to the root directory, and then
```python
sudo bash install.sh
```
Then you can use `import tellopy` in anywhere.

## 4. Markers on the ground I’ve used
First we need to generate the markets. I used the [this site](http://chev.me/arucogen/), and the parameters I’ve used is 8\*8, each one was 200mm. You should attach them in orders, like, first row 0-7, second row 8-15 and so on.

## 5. Test if the hardware works
Turn on the TELLO, and connect the video receiver to the PC.  Then `cd xxx/Tello-Aruco/compos/`, then `python3 videoARPosTest.py`.

If you see the coordinates information shows on the screen, it means that your self-made hardware works. You can move the TELLO with bottom-facing camera to see the coordinates change.

## 6. Run the libary
```python
python3 tellofly.py
```
When you see a penguin with gun, click the penguin, and push `h`, then the drone will take off. Then push `a`, the drone will fly. Try to push `m` or `b`, it will fly to different place. Last, push `d` to landing.

### What’s the next step?
Since this project is heavily depends on the hardware, so there will be many `bugs` for you. The best way to use it is to understand how it works, and use some part of it in your project.

## 7. How it works
First you can view [this video](https://www.youtube.com/watch?v=G9H4TvE3mVE) to see what it can do.
### Overview
The system use several threads to accomplish  different tasks, and use feedback control algorithm to make the drone flies to target position.

### Multithread
The reason I choose multiple thread here is: CPU power is enough (in python, multiple thread don’t run in different CPUs, while easier)

Command receiving thread: this thread is to receive command from the UDP (I used a mobile device to send the command to it)

Video receiving thread:
Use this thread to receive videos of TELLO, if you don’t write this in thread or process, the code will be super slow.

Video sending thread:
I need to show the TELLO video on my mobile device, so I added this thread. It also uses UDP.

Direction controlling thread: 
I just put it on the thread because I’ve used head tracking once, and forget to put it in main thread. Anyway, the principle is the same, and should work for both.

Main thread:
This thread is used to calculate the target position, TELLO position, and PID outputs.

### Public shared state
Since the threads need to share the states of TELLO, I used shared state between the threads.

### Feedback control
The core part of this work is feedback control. It’s very simple while powerful. The inputs are drone state (position, direction, speed, etc), and the outputs of PID module is a vector (x, y, z speed) for control TELLO api, just like a joystick.
