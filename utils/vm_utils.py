import os
import libvirt
import xml.etree.ElementTree as ET
import random
from conf.setting import vm_conf


class VirtualMachine:
    def __init__(self):
        """
        初始化虚拟机对象。

        Args:
            name (str): 虚拟机名称
        """
        self.conn = libvirt.open()

    def create(self, name, memory=512, vcpu=1, disk_size=30, mac_address=None, ip_address=None, port=None, sys='windows10'):
        """
        创建虚拟机。

        Args:
            ip_address (str, optional): 虚拟机的 IP 地址， 默认为 None
            port (int, optional): RDP 连接的端口号，默认为 8080
            os (str, optional): 虚拟机的操作系统，默认为 'windows'

        Returns:
            domain (libvirt.virDomain): 创建的虚拟机对象
            :param port: 虚拟机端口
            :param ip_address: 虚拟机IP地址
            :param mac_address: 虚拟机MAC地址
            :param disk_size: 虚拟机磁盘大小默认30G
            :param memory: 虚拟机内存大小
            :param vcpu: 虚拟机VCPU数量
        """
        # 生成随机 MAC 地址
        if mac_address:
            mac = mac_address
        else:
            mac = ':'.join(['52'] + [f'{random.randint(0x00, 0xff):02x}' for _ in range(5)])
        print(1)
        # 根据操作系统选择镜像路径
        if sys == 'windows10':
            image_path = '/var/lib/libvirt/images/windows.iso'  # Windows 镜像文件路径
        elif sys == 'windows7':
            image_path = '/var/lib/libvirt/images/linux.iso'  # Linux 镜像文件路径
        else:
            raise ValueError("Invalid operating system. Supported values are 'windows' and 'linux'.")
        print(2)
        disk_size = disk_size * 1024 * 1024 * 1024  # 磁盘大小30GB

        # 验证并创建磁盘存放路径
        disk_path = f'/var/lib/libvirt/VM/{name}/{name}.qcow2'  # 磁盘文件存放地址
        if not os.path.exists(os.path.dirname(disk_path)):
            os.makedirs(os.path.dirname(disk_path))
        print(disk_path)
        # 生成随机端口
        port = port if port else random.randint(1024, 65535)

        # ip配置
        ip_conf = f"<listen type='network' address='{ip_address}' port='{port}'/>" if ip_address and port else ''

        # 定义虚拟机的 XML 描述
        xml_desc = vm_conf.format(name, memory * 1024, vcpu, disk_path, disk_size, mac, ip_conf, image_path)
        print(xml_desc)
        # 创建虚拟机并返回虚拟机对象
        domain = self.conn.createXML(xml_desc, 0)

        ip = self.get_vm_ip_address(domain)
        ret_dict = {
            'vm_name': name,
            'memory': memory,
            'vcpu': vcpu,
            'disk_size': disk_size,
            'mac_address': mac_address,
            'ip_address': ip,
            'port': port,
            'os': os
        }
        return ret_dict

    def connect_rdp(self, name):
        """
        连接已创建的虚拟机的 RDP。

        Returns:
            str: RDP 连接字符串，格式为 "rdp://<hostname>:<port>"
        """
        domain = self.conn.lookupByName(name)
        if domain.isActive() == 1:
            xml_desc = domain.XMLDesc()
            graphics_elem = ET.fromstring(xml_desc).find(".//devices/graphics[@type='rdp']")
            if graphics_elem is not None:
                port = graphics_elem.get('port')
                return "rdp://{}:{}".format(self.conn.getHostname(), port)
            else:
                return "RDP not enabled for this virtual machine."
        else:
            return "Virtual machine is not running."

    def delete(self, name):
        """
        删除已创建的虚拟机。

        Returns:
            str: 成功删除虚拟机的信息
        """
        domain = self.conn.lookupByName(name)
        if domain.isActive() == 1:
            domain.destroy()  # 先停止虚拟机
        domain.undefine()  # 删除虚拟机
        return "Virtual machine {} has been deleted.".format(name)

    def start(self, name):
        """
        开启虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(name)
        # 发送启动指令
        domain.create()

    def shutdown(self, name):
        """
        关闭虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(name)
        # 发送关机指令
        domain.shutdown()

    def reboot(self, name):
        """
        重启虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(name)
        # 发送重启指令
        domain.reboot()

    def is_running(self, name):
        """
        检查虚拟机是否运行中。

        Returns:
            bool: 如果虚拟机运行中返回 True，否则返回 False。
        """
        domain = self.conn.lookupByName(name)
        return domain.isActive()

    def adjust_vm_config(self, name, memory=None, vcpu=None, disk_size=None):
        """
        调整虚拟机配置。

        Args:
            memory (int): 新的虚拟机内存大小（单位：MB）。
            vcpu (int): 新的虚拟机VCPU数量。
            disk_size (int): 新的虚拟机磁盘大小（单位：GB）。

        Returns:
            bool: 如果调整成功返回 True，否则返回 False。
        """
        domain = self.conn.lookupByName(name)
        if not self.is_running(name):
            if memory is not None:
                domain.xmlDesc().find('memory').text = str(memory * 1024)
                domain.xmlDesc().find('currentMemory').text = str(memory * 1024)
            if vcpu is not None:
                domain.xmlDesc().find('vcpu').text = str(vcpu)
            if disk_size is not None:
                current_disk_size = domain.blockInfo('/var/lib/libvirt/images/windows.qcow2')[0] / (
                            1024 * 1024 * 1024)
                if disk_size > current_disk_size:
                    domain.blockResize('/var/lib/libvirt/images/windows.qcow2', disk_size * 1024 * 1024 * 1024)
                else:
                    print("磁盘大小只能调大，不能调小。")
                    return False
            domain.reconnect(0)
            return True
        else:
            print("虚拟机正在运行中，无法调整配置。")
            return False

    def get_vm_ip_address(self, vm):
        """
        获取虚拟机的IP地址。

        Args:
            vm (libvirt.virDomain): 虚拟机对象。

        Returns:
            str: 虚拟机的IP地址，如果无法获取则返回 None。
        """
        # 获取虚拟机的 XML 描述
        xml_desc = vm.XMLDesc()

        # 解析 XML 描述，提取网络接口配置信息
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(xml_desc)
        interfaces = tree.findall('.//devices/interface')

        for interface in interfaces:
            mac_element = interface.find('mac')
            mac_address = mac_element.get('address')

            # 获取IP地址
            network_element = interface.find('source').get('network')
            network = vm._conn.networkLookupByName(network_element)
            lease = network.DHCPLeases(mac_address)

            if lease:
                ip_address = lease[0]['ipaddr']
                return ip_address

        return None
