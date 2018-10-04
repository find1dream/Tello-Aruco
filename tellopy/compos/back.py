from time import sleep
import tellopy

import pygame, time
from pygame.locals import *
import sys



def handler(event, sender, data, **args):
        drone = sender
        if event is drone.EVENT_FLIGHT_DATA:
            print(data)
class DroneFly(tellopy.Tello):
    def init(self):
        pass
    
    def takeoff(self):
        try:
            print("msg: succeed to connect to tello, 5 seconds left...")
            sleep(5)
            print("msg: takeoff...")
            super().takeoff()
            print("msg: tring to keep balance, cannot controll now")
            sleep(3)
            print("msg: ok to input you commonds")
        except Exception as ex:
            print(ex)
        finally:
            self.drone.quit()
    def land(self):
        print("msg: landing...")
        self.drone.land()



if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    pygame.display.set_caption('key')
    pygame.mouse.set_visible(0)

    drone = tellopy.Tello()
    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)

    drone.connect()
    drone.wait_for_connection(60.0)
    drone.takeoff()
    
    while True:
     for event in pygame.event.get():
       if (event.type == KEYDOWN):
         if (event.key == pygame.K_LEFT):
             #drone.left(20)
             drone.clockwise(40)
             print ("left")
         
         if (event.key == pygame.K_RIGHT):
             #drone.right(80)
             drone.right(40)
             print("right")
         if (event.key == pygame.K_UP):
             drone.up(40)
             print("up")
         if (event.key == pygame.K_DOWN):
             drone.down(40)
             print("down")

         if (event.key == pygame.K_s):
             print("stop!!!!!")
             drone.land()
       if (event.type == KEYUP):

         if (event.key == pygame.K_LEFT):
             #drone.left(20)
             drone.clockwise(0)
             print ("left")
         
         if (event.key == pygame.K_RIGHT):
             drone.right(0)
             print("right")
         if (event.key == pygame.K_UP):
             drone.up(0)
             print("up")
         if (event.key == pygame.K_DOWN):
             drone.down(0)
             print("down")

         if (event.key == pygame.K_s):
             print("stop!!!!!")
             drone.land()
    #test()
