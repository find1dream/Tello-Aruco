from socket import *
import numpy as np

class getPosData():
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 35601
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print("udp initialization complete...")

    def recvdata(self):
        data, _ = self.socket.recvfrom(512)
        #data = "9 33 74 66"
        data = data.decode()
        data = [int(m) for m in data.split()]

        try:
            if data[0] != 9:
                return data[0], np.array([data[1],data[2],data[3]])
            else:
                return data[0], 0
        except:
            print("plese chekck data length...")

    def processdata(self, cmd, data):
        pass

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    udpRead = getPosData()
    mm, nn = udpRead.recvdata()
    print(mm,nn)

