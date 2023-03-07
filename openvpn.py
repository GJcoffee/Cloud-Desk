import openvpn

# 创建OpenVPN客户端配置
client_config = openvpn.Config(
    {
        'remote': 'vpn.example.com',
        'port': '1194',
        'proto': 'udp',
        'dev': 'tun',
        'auth': 'SHA256',
        'cipher': 'AES-256-CBC',
        'persist-key': '',
        'persist-tun': '',
        'ca': '/path/to/ca.crt',
        'cert': '/path/to/client.crt',
        'key': '/path/to/client.key',
        'tls-auth': '/path/to/ta.key',
    }
)

# 创建OpenVPN客户端实例
client = openvpn.Client(client_config)

# 连接到OpenVPN服务器
client.connect()

# 发送数据
client.send('Hello, world!')

# 从服务器接收数据
data = client.recv()

# 断开连接
client.disconnect()
