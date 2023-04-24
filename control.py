from flask import Flask, request
import requests

app = Flask(__name__)


@app.route('/create_vm', methods=['POST'])
def create_vm():
    """
    创建虚拟机的接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')
    memory = request.form.get('memory')
    vcpu = request.form.get('vcpu')
    disk_size = request.form.get('disk_size')
    mac_address = request.form.get('mac_address')
    ip_address = request.form.get('ip_address')
    port = request.form.get('port')
    os = request.form.get('os')

    # 根据请求参数构建请求数据
    payload = {
        'vm_name': vm_name,
        'memory': memory,
        'vcpu': vcpu,
        'disk_size': disk_size,
        'mac_address': mac_address,
        'ip_address': ip_address,
        'port': port,
        'os': os
    }

    # 发送请求到服务器节点的代理接口
    response = requests.post('http://server_node_proxy/create_vm', data=payload)

    # 返回响应
    return response.text


@app.route('/delete_vm', methods=['POST'])
def delete_vm():
    """
    删除虚拟机的接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 根据请求参数构建请求数据
    payload = {
        'vm_name': vm_name
    }

    # 发送请求到服务器节点的代理接口
    response = requests.post('http://server_node_proxy/delete_vm', data=payload)

    # 返回响应
    return response.text


@app.route('/connect_vm', methods=['POST'])
def connect_vm():
    """
    连接虚拟机的接口
    """
    # 获取请求参数
    vm_name = request.form.get('vm_name')

    # 根据请求参数构建请求数据
    payload = {
        'vm_name': vm_name
    }

    # 发送请求到服务器节点的代理接口
    response = requests.post('http://server_node_proxy/connect_vm', data=payload)

    # 返回响应
    return response.text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
