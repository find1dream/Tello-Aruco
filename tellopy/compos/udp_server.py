from socket import *
import numpy as np

class getPosData():
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 3333
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print("udp initialization complete...")

    def rcvRawdata(self):
        data, _ = self.socket.recvfrom(512)
        #data = "9 33 74 66"
        data = data.decode()
        data = np.array([int(m) for m in data.split()])
        num = data[0]
        data = data[1:]
        try:
            if num != 9:
                for index, value in enumerate(data):
                     if value > 150:
                         data[index] = 150
                     if value < 15:
                         data[index] = 15
                
                return num, data
            else:
                return num, 0
        except:
            print("plese chekck data length...")
            self.close()

    def getmsg(self):
        cmd, pos = self.rcvRawdata()

        if cmd != 9:
            return cmd, pos
        else:
            return cmd, 0

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    udpRead = getPosData()
    while True:

        mm,n = udpRead.rcvRawdata()
        print(mm,n)

