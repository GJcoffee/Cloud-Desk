import rados

cluster = rados.Rados(conffile='/etc/ceph/ceph.conf')
cluster.connect()
ioctx = cluster.open_ioctx('rbd')
ioctx.write('test.txt', 'Hello, World!')
