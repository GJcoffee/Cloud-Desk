import random
import string
import requests
from flask import request, jsonify
from db_model import db, User, VirtualMachine
from app import app


# 根据用户账号获取虚拟机数量
def get_vm_count(username):
    user = User.query.filter_by(username=username).first()
    return len(user.virtual_machines)


# 根据用户账号获取虚拟机列表
def get_vm_list(username):
    user = User.query.filter_by(username=username).first()
    return [vm.name for vm in user.virtual_machines]


# 根据虚拟机名称获取用户账号
def get_username_by_vm(vm_name):
    vm = VirtualMachine.query.filter_by(name=vm_name).first()
    return vm.user.username


# 虚拟机数量是否已达到上限
def is_vm_limit_reached(username):
    return get_vm_count(username) >= 3


# 路由：申请虚拟机
@app.route('/api/vm', methods=['POST'])
def apply_vm():
    username = request.cookies.get('username')  # 获取当前用户账号
    if is_vm_limit_reached(username):
        return jsonify({'message': 'You have reached the maximum limit of virtual machines.'}), 400

    # 获取请求参数
    vm_name = request.form.get('vm_name')
    memory = request.form.get('memory')
    vcpu = request.form.get('vcpu')
    disk_size = request.form.get('disk_size')
    mac_address = request.form.get('mac_address')
    ip_address = request.form.get('ip_address')
    port = request.form.get('port')
    os = request.form.get('os')

    # 向agent请求创建虚拟机
    response = requests.post('http://agent/create_vm', data={
        'vm_name': vm_name,
        'memory': memory,
        'vcpu': vcpu,
        'disk_size': disk_size,
        'mac_address': mac_address,
        'ip_address': ip_address,
        'port': port,
        'os': os
    })

    if response.status_code == 200:
        # 创建虚拟机记录
        vm = VirtualMachine(name=vm_name, user_id=User.query.filter_by(username=username).first().id)
        db.session.add(vm)
        db.session.commit()
        return jsonify({'message': 'Virtual machine created successfully.'}), 200
    else:
        return jsonify({'message': 'Failed to create virtual machine.'}), 500


# 路由：获取当前用户已申请的虚拟机列表
@app.route('/api/vm', methods=['GET'])
def get_vm():
    username = request.cookies.get('username')  # 获取当前用户账号
    vm_list = get_vm_list(username)  # 获取当前用户的虚拟机列表
    return jsonify(vm_list), 200


# 路由：删除虚拟机
@app.route('/api/vm/<int:vm_id>', methods=['DELETE'])
def delete_vm(vm_id):
    vm = VirtualMachine.query.get_or_404(vm_id)  # 查询虚拟机信息
    user = vm.user  # 查询虚拟机所属用户信息

    if not user.is_admin and vm not in user.vms:
        # 非管理员不能删除其他用户的虚拟机，普通用户只能删除自己的虚拟机
        return {'error': 'Unauthorized'}, 401

    db.session.delete(vm)  # 删除虚拟机
    user.vm_count -= 1  # 用户虚拟机资源池余量加1
    db.session.commit()

    return {'message': 'Deleted'}, 204


# 路由：创建虚拟机
@app.route('/api/vm', methods=['POST'])
def create_vm():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'User not found'}, 404

    if user.vm_count >= 3:
        return {'error': 'VM count exceeded'}, 400

    vm = VirtualMachine(name='VM{}'.format(user.vm_count + 1), user=user)
    user.vm_count += 1
    db.session.add(vm)
    db.session.commit()

    return {'message': 'Created', 'vm_id': vm.id}, 201


# 路由：获取用户虚拟机列表
@app.route('/api/vms', methods=['GET'])
def get_vms():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'User not found'}, 404

    vms = [{'id': vm.id, 'name': vm.name} for vm in user.vms]
    return {'vms': vms}


@app.route('/approve', methods=['POST'])
def approve_vm():
    data = request.get_json()
    user_id = data.get('user_id')
    vm_name = data.get('vm_name')

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    # 查询用户当前的虚拟机数量
    current_vms = VirtualMachine.query.filter_by(user_id=user_id).count()
    if current_vms >= 3:
        return jsonify({'status': 'error', 'message': 'User has reached maximum number of virtual machines'})

    # 创建虚拟机
    vm = VirtualMachine(name=vm_name, user_id=user_id)
    db.session.add(vm)
    db.session.commit()

    return jsonify({'status': 'ok', 'message': 'Virtual machine created'})
