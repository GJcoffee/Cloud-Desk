import libvirt
import xml.etree.ElementTree as ET
import random


class VirtualMachine:
    def __init__(self, name, memory=512, vcpu=1, disk_size=10, mac_address=None):
        """
        初始化虚拟机对象。

        Args:
            name (str): 虚拟机名称
            memory (int, optional): 内存大小（MiB），默认为 512
            vcpu (int, optional): 虚拟 CPU 数量， 默认为 1
            disk_size (int, optional): 磁盘大小（GiB），默认为 10
        """
        self.name = name
        self.memory = memory
        self.vcpu = vcpu
        self.disk_size = disk_size
        self.mac_address = mac_address
        self.conn = libvirt.open()

    def create(self, memory=512, vcpu=1, disk_size=30, mac_address=None, ip_address=None, port=8080, os='windows'):
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
            :param disk_size: 虚拟机磁盘大小
            :param memory: 虚拟机内存大小
            :param vcpu: 虚拟机VCPU数量
        """
        # 生成随机 MAC 地址
        if mac_address:
            mac = mac_address
        else:
            mac = ':'.join(['52'] + [f'{random.randint(0x00, 0xff):02x}' for _ in range(5)])

        # 根据操作系统选择镜像路径
        if os == 'windows':
            image_path = '/var/lib/libvirt/images/windows.qcow2'
        elif os == 'linux':
            image_path = '/var/lib/libvirt/images/linux.qcow2'
        else:
            raise ValueError("Invalid operating system. Supported values are 'windows' and 'linux'.")

        # 定义虚拟机的 XML 描述
        xml_desc = """
            <domain type='kvm'>
                <name>{}</name>
                <memory unit='KiB'>{}</memory>
                <vcpu placement='static'>{}</vcpu>
                <devices>
                    <disk type='file' device='disk'>
                        <driver name='qemu' type='qcow2'/>
                        <source file='{}'/>
                        <target dev='vda' bus='virtio'/>
                        <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                    </disk>
                    <interface type='network'>
                        <mac address='{}'/>
                        <model type='virtio'/>
                        <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                        {}
                    </interface>
                </devices>
            </domain>
        """.format(self.name, memory * 1024, vcpu, image_path, mac,
                   f"<listen type='network' address='{ip_address}' port='{port}'/>" if ip_address and port else '')

        # 创建虚拟机并返回虚拟机对象
        domain = self.conn.createXML(xml_desc, 0)
        return domain

    def connect_rdp(self):
        """
        连接已创建的虚拟机的 RDP。

        Returns:
            str: RDP 连接字符串，格式为 "rdp://<hostname>:<port>"
        """
        domain = self.conn.lookupByName(self.name)
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

    def delete(self):
        """
        删除已创建的虚拟机。

        Returns:
            str: 成功删除虚拟机的信息
        """
        domain = self.conn.lookupByName(self.name)
        if domain.isActive() == 1:
            domain.destroy()  # 先停止虚拟机
        domain.undefine()  # 删除虚拟机
        return "Virtual machine {} has been deleted.".format(self.name)

    def start(self):
        """
        开启虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(self.name)
        # 发送启动指令
        domain.create()

    def shutdown(self):
        """
        关闭虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(self.name)
        # 发送关机指令
        domain.shutdown()

    def reboot(self):
        """
        重启虚拟机。
        """
        # 获取虚拟机对象
        domain = self.conn.lookupByName(self.name)
        # 发送重启指令
        domain.reboot()
