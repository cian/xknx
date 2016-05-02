import socket
import struct
from .telegram import Telegram
from .address import Address

class Multicast:
    MCAST_GRP = '224.0.23.12'
    MCAST_PORT = 3671

    own_address_ = Address("15.15.250")
    #own_ip = "192.168.2.106"
    own_ip = "192.168.42.1"

    def __init__(self):
        pass

    def send(self, telegram):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.own_ip))

        sock.sendto(telegram.str(), (self.MCAST_GRP, self.MCAST_PORT))

    def recv(self, callback):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.own_ip))

        sock.bind(('', self.MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                             # to MCAST_GRP, not all groups on MCAST_PORT
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            telegram_data = sock.recv(10240)
            if telegram_data:
                telegram = Telegram()
                telegram.read(telegram_data)

                if telegram.sender == self.own_address_:
                    print("Ignoring own telegram")
                else:
                    callback(telegram)
