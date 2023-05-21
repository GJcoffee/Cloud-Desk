import requests
from flask import Flask, request, jsonify
from utils.vm_utils import VirtualMachine

app = Flask(__name__)

# 控制节点的代理接口地址
CONTROL_NODE_PROXY_URL = 'http://123.60.179.0:8000/'
kvm = VirtualMachine()


@app.route('/create_vm', methods=['POST'])
def create_vm():
    """
    创建虚拟机的路由接口
    """
    # 获取请求参数
    data = request.get_json()
    vm_name = data.get('vm_name')
    memory = data.get('memory')
    vcpu = data.get('vcpu')
    disk_size = data.get('disk_size')
    mac_address = data.get('mac_address')
    ip_address = data.get('ip_address')
    port = data.get('port')
    os = data.get('os')

    # 调用 KVM 类中的创建虚拟机方法
    data = kvm.create(vm_name, memory, vcpu, disk_size, mac_address, ip_address, port, os)
    # 向agent请求创建虚拟机
    return jsonify(data), 200


@app.route('/delete_vm', methods=['POST'])
def delete_vm():
    """
    删除虚拟机的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 调用 KVM 类中的删除虚拟机方法
    kvm.delete(vm_name)

    # 返回响应
    return jsonify({'message': 'Virtual machine delete successfully.'}), 200


@app.route('/connect_vm', methods=['POST'])
def connect_vm():
    """
    连接虚拟机的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 调用 KVM 类中的连接虚拟机方法
    kvm.connect_rdp(vm_name)

    # 返回响应
    return jsonify({'message': 'Virtual machine connect successfully.'}), 200


@app.route('/start_vm', methods=['POST'])
def start_vm():
    """
    开启虚拟机的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 调用 KVM 类中的开启虚拟机方法
    kvm.start(vm_name)

    # 返回响应
    return jsonify({'message': 'Virtual machine start successfully.'}), 200


@app.route('/stop_vm', methods=['POST'])
def stop_vm():
    """
    关闭虚拟机的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 调用 KVM 类中的关闭虚拟机方法
    kvm.shutdown(vm_name)

    # 返回响应
    return jsonify({'message': 'Virtual machine close successfully.'}), 200


@app.route('/reboot_vm', methods=['POST'])
def reboot_vm():
    """
    重启虚拟机的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 调用 KVM 类中的重启虚拟机方法
    kvm.reboot(vm_name)

    # 返回响应
    return jsonify({'message': 'Virtual machine reboot successfully.'}), 200


@app.route('/adjust_vm', methods=['POST'])
def adjust_vm():
    """
    调整虚拟机配置的路由接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')
    memory = request.form.get('memory', int)
    vcpu = request.form.get('vcpu', int)
    disk_size = request.form.get('disk_size', int)

    # 调用 KVM 类中的调整虚拟机配置方法
    try:
        kvm.adjust_vm_config(vm_name, memory, vcpu, disk_size)
    except Exception:
        raise

    # 返回响应
    return jsonify({'message': 'Virtual machine change successfully.'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
