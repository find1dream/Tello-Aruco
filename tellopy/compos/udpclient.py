import socket
import time
udp_ip = "127.0.0.1"
udp_port = 5555
message = [0.0,4.0, 4.9]
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

i=0.0
while True:
    i += 0.1
    message = [i, i , i]
    message = " ".join(str(x) for x in message)
    clientSock.sendto(message.encode(), (udp_ip, udp_port))
    time.sleep(0.5)
    # data, addr = serverSock.recvfrom(1024)
    print("messages: ", message)
