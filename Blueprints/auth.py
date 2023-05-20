import hashlib
from flask import request, session, redirect, url_for, make_response, Blueprint, render_template
from datetime import timedelta
import datetime
from utils.db_model import User
from conf.exsits import db
from utils.time_utils import DateUtils

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def write_time(url='auth.login'):
    last_active = str(session.get('last_active'))[:19].replace('-', '').replace(' ', '').replace(':', '').replace(
        'None', '')
    last_active = last_active if last_active else 0
    if not last_active:
        # 如果是第一次请求，则记录当前时间为最后活跃时间
        session['last_active'] = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S"))
    else:
        # 计算当前时间和最后活跃时间之间的差值
        inactive_time = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S")) - int(last_active)
        if inactive_time > 100000000:
            # 如果用户已经超过60分钟没有活动，则让用户自动登出
            session.pop('username', None)
            session.pop('last_active', None)
            return redirect(url_for(url))
    # 更新最后活跃时间
    session['last_active'] = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S"))


@auth_bp.before_request
def before_request():
    if 'username' in session:
        last_active = str(session.get('last_active'))[:19].replace('-', '').replace(' ', '').replace(':', '').replace(
            'None', '')
        last_active = last_active if last_active else 0
        if not last_active:
            # 如果是第一次请求，则记录当前时间为最后活跃时间
            session['last_active'] = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S"))
        else:
            # 计算当前时间和最后活跃时间之间的差值
            inactive_time = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S")) - int(last_active)
            if inactive_time > 100000000:
                # 如果用户已经超过60分钟没有活动，则让用户自动登出
                session.pop('username', None)
                session.pop('last_active', None)
                return redirect(url_for(url))
        # 更新最后活跃时间
        session['last_active'] = int(DateUtils.get_current_format_time(date_format="%Y%m%d%H%M%S"))
    elif request.endpoint == 'auth.approval_login':
        return
    elif request.endpoint != 'auth.login':
        # 用户未认证并且访问的不是登录接口，重定向到登录接口
        return redirect(url_for('auth.login'))


@auth_bp.route('/approval_login', methods=['GET', 'POST'])
def approval_login():
    """审批登录接口"""
    if request.method == 'POST':
        # 获取用户提交的表单数据
        username = request.form['username']
        password = request.form['password']
        # 验证用户信息
        user = db.session.query(User).filter_by(username=username, password=password).first()
        if user:
            if user.is_admin or session['username'] == 'root':
                # 管理员登录成功
                session['username'] = user.username
                session['is_admin'] = True
                # 从数据库检索需要审批的数据
                applications = db.session.query(DesktopApplication).filter_by(status=0).all()
                return render_template('approval_dashboard.html', applications=applications)
        else:
            return
    else:
        return render_template('approve_login.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录接口"""
    if request.method == 'POST':
        # 获取用户提交的表单数据
        username = request.form['username']
        password = request.form['password']
        # 验证用户信息
        user = db.session.query(User).filter_by(username=username, password=password).first()
        if user:
            # 认证成功，保存用户信息到session
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            # 检查用户是否拥有虚拟机
            virtual_machines = get_user_virtual_machines()
            if len(virtual_machines) > 0:
                # 用户拥有虚拟机，返回虚拟机列表页面
                return vm_list()
            else:
                # 用户没有虚拟机，返回虚拟机申请页面
                return render_template('vm_application.html')
        else:
            # 认证失败，返回错误提示
            return 'Invalid username or password'
    else:
        # 返回登录页面
        return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """用户注销接口"""
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))


# 管理员账号创建普通用户
@auth_bp.route('/api/create_user', methods=['POST'])
def create_user():
    # 验证用户是否为管理员
    # 省略验证代码
    # 获取请求参数
    username = request.json.get('username')
    password = request.json.get('password')
    # 验证密码是否符合规则

    # 创建普通用户并保存到数据库
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return make_response('User created', 200)


def get_user_virtual_machines():
    # 获取当前用户的用户名
    username = session.get('username')

    # 查询数据库以获取用户对象
    user = User.query.filter_by(username=username).first()

    # 如果用户存在，则获取用户拥有的虚拟机列表
    if user:
        virtual_machines = user.virtual_machines
        return virtual_machines

    # 如果用户不存在或未拥有任何虚拟机，则返回空列表
    return []


def vm_list():
    # 获取用户虚拟机列表
    virtual_machines = get_user_virtual_machines()

    # 渲染虚拟机列表模板，并传递虚拟机列表作为参数
    return render_template('vm_list.html', virtual_machines=virtual_machines)
