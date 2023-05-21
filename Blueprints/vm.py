import json

import requests
from flask import request, jsonify, Blueprint, session
from utils.db_model import User, VirtualMachine, DesktopApplication
from conf.exsits import db
from Blueprints.auth import vm_list

vm_bp = Blueprint('vm', __name__, url_prefix='/vm')


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


# 路由：获取当前用户已申请的虚拟机列表
@vm_bp.route('/api/vm', methods=['GET'])
def get_vm():
    username = request.cookies.get('username')  # 获取当前用户账号
    vm_list = get_vm_list(username)  # 获取当前用户的虚拟机列表
    return jsonify(vm_list), 200


# 路由：删除虚拟机
@vm_bp.route('/api/delete_vm', methods=['POST'])
def delete_vm():
    # 获取请求参数
    data = request.get_json()
    vm_name = data.get('vm_name')

    # 查询虚拟机信息
    vm = VirtualMachine.query.filter_by(name=vm_name).first()
    if not vm:
        return {'error': 'Virtual machine not found'}, 404

    user = vm.user  # 查询虚拟机所属用户信息

    if not user.is_admin and vm not in user.virtual_machines:
        # 非管理员不能删除其他用户的虚拟机，普通用户只能删除自己的虚拟机
        return {'error': 'Unauthorized'}, 401

    db.session.delete(vm)  # 删除虚拟机
    db.session.commit()

    return {'message': 'Virtual machine deleted'}, 200


# 路由：关闭虚拟机
@vm_bp.route('/close_vm', methods=['POST'])
def close_vm():
    # 获取请求参数
    data = request.get_json()
    vm_name = data.get('vm_name')

    # 查询虚拟机信息
    vm = VirtualMachine.query.filter_by(name=vm_name).first()
    if not vm:
        return {'error': 'Virtual machine not found'}, 404

    user = vm.user  # 查询虚拟机所属用户信息

    if not user.is_admin and vm not in user.virtual_machines:
        # 非管理员不能删除其他用户的虚拟机，普通用户只能删除自己的虚拟机
        return {'error': 'Unauthorized'}, 401

    # 向agent请求创建虚拟机
    response = requests.post('http://121.37.183.211:8080/stop_vm', data={'vm_name': data.get('vm_name')})
    if response.status_code == 200:
        return {'message': 'Virtual machine closed'}, 200
    return {'message': 'Virtual machine close failed'}


# 路由：获取用户虚拟机列表
@vm_bp.route('/api/vms', methods=['GET'])
def get_vms():
    return vm_list()


# 路由：申请虚拟机
@vm_bp.route('/apply_vm', methods=['POST'])
def apply_vm():
    username = session.get('username')  # 获取当前用户账号
    if is_vm_limit_reached(username):
        return jsonify({'message': 'You have reached the maximum limit of virtual machines.'}), 400
    vm_name = request.form['vm_name']
    desk_username = request.form['desk_username']
    desk_password = request.form['desk_password']
    memory = int(request.form['memory'])
    vcpu = int(request.form['vcpu'])
    disk_size = int(request.form['disk_size'])
    os = request.form['os']

    application = DesktopApplication(vm_name=vm_name, username=username, desk_username=desk_username,
                                     desk_password=desk_password, memory=memory, vcpu=vcpu, disk_size=disk_size, os=os)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Desktop application submitted successfully.'}), 200


@vm_bp.route('/approve', methods=['POST'])
def approve_vm():
    data = request.get_json()
    user_name = data.get('username')

    # 查询用户
    user = User.query.get(user_name)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    # 查询用户当前的虚拟机数量
    current_vms = VirtualMachine.query.filter_by(user_id=user.id).count()
    if current_vms >= 3:
        return jsonify({'status': 'error', 'message': 'User has reached maximum number of virtual machines'})

    # 向agent请求创建虚拟机
    response = requests.post('http://121.37.183.211:8080/create_vm', data={
        'vm_name': data.get('vm_name'),
        'memory': data.get('memory'),
        'vcpu': data.get('vcpu'),
        'disk_size': data.get('disk_size'),
        'mac_address': data.get('mac_address'),
        'ip_address': data.get('ip_address'),
        'port': data.get('port', ''),
        'os': data.get('os')
    })

    if response.status_code == 200:
        # 创建虚拟机
        data = json.loads(response.text)
        vm = VirtualMachine(name=data.get('vm_name'),
                            memory=data.get('memory'),
                            vcpu=data.get('vcpu'),
                            disk_size=data.get('disk_size'),
                            mac_address=data.get('mac_address'),
                            ip_address=data.get('ip_address'),
                            port=data.get('port'),
                            os=data.get('os'),
                            desk_username=data.get('desk_username', 'root'),
                            desk_password=data.get('desk_password', 'cloud@desk'),
                            user_id=user.id)
        db.session.add(vm)
        db.session.commit()

    return jsonify({'status': 'ok', 'message': 'Virtual machine created'}), 200
