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

## 4. Run the libary
```python
python3 xxx/Tello-Aruco/tellopy/compos/tellofly.py
```

## How it works


| Class Name | Description (What does the class do?) |
----|---- 
| *PlayerController* | Enable user to move player gameobject. |
| *BackgroundScroller* | Scroll background image permanently. |
| *ComponentExtension* | Extension of ***Component*** class. |
| [*SingletonMonoBehaviour< T >*](https://qiita.com/okuhiiro/items/3d69c602b8538c04a479) | This class makes ***class T*** singleton in the scene. |
