import ipaddress
import random
import socket
import fcntl
import struct
import os

def get_host_network_info():
    # 获取默认网络接口
    default_interface = os.environ.get('DEFAULT_INTERFACE', 'eth0')

    # 获取网络接口信息
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_fd = sock.fileno()
    ifname = bytes(default_interface, 'utf-8')
    try:
        # 获取网络接口的IP地址和子网掩码
        ip_address = socket.inet_ntoa(fcntl.ioctl(sock_fd, 0x8915, struct.pack('256s', ifname[:15]))[20:24])
        netmask = socket.inet_ntoa(fcntl.ioctl(sock_fd, 0x891b, struct.pack('256s', ifname[:15]))[20:24])

        return ip_address, netmask
    except IOError:
        raise RuntimeError(f"Failed to get network information for interface '{default_interface}'")


def generate_random_ip():
    host_ip, host_subnet = get_host_network_info()
    network = ipaddress.IPv4Network(f"{host_ip}/{host_subnet}", strict=False)
    # 从网络范围中排除网络地址和广播地址
    usable_network = network.network_address + 1
    usable_broadcast = network.broadcast_address - 1

    # 生成随机IP地址
    while True:
        random_ip = ipaddress.IPv4Address(random.randint(int(usable_network), int(usable_broadcast)))
        if random_ip != network.network_address and random_ip != network.broadcast_address:
            return str(random_ip)
