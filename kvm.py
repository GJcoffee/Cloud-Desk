import libvirt

conn = libvirt.open()
xml = """
<domain type='kvm'>
  <name>testvm</name>
  <memory unit='KiB'>1048576</memory>
  <vcpu placement='static'>1</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.8'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/var/lib/libvirt/images/testvm.qcow2'/>
      <target dev='vda' bus='virtio'/>
    </disk>
  </devices>
</domain>
"""
conn.createXML(xml, 0)
