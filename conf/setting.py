from control import app
# 虚拟机配置模板
vm_conf = """
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
            <driver name='qemu' type='qcow2' size='{}'/>
        </disk>
        <interface type='network'>
            <mac address='{}'/>
            <model type='virtio'/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
            {}
        </interface>
        <disk type='file' device='cdrom'>
            <driver name='qemu' type='raw'/>
            <source file='{}'/>
            <target dev='vdb' bus='virtio'/>
            <readonly/>
            <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
        </disk>
    </devices>
</domain>"""

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cloud_desk.db'  # 设置数据库连接URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 设置Flask应用的秘密密钥