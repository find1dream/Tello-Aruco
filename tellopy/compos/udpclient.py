import socket

udp_ip = "127.0.0.1"
udp_port = 5555
message = [0.0,4.0, 4.9]
message = " ".join(str(x) for x in message)
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    clientSock.sendto(message.encode(), (udp_ip, udp_port))
    # data, addr = serverSock.recvfrom(1024)
    # print("messages: ", data)
