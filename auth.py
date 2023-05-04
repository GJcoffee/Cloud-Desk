import random
import string
import hashlib
from flask import request, session, redirect, url_for, make_response
from datetime import timedelta, datetime
from db_model import db_session, User
from app import app


@app.before_request
def before_request():
    if 'username' in session:
        last_active = session.get('last_active')
        if not last_active:
            # 如果是第一次请求，则记录当前时间为最后活跃时间
            session['last_active'] = datetime.now()
        else:
            # 计算当前时间和最后活跃时间之间的差值
            inactive_time = datetime.now() - last_active
            if inactive_time > timedelta(minutes=60):
                # 如果用户已经超过60分钟没有活动，则让用户自动登出
                session.pop('username', None)
                session.pop('last_active', None)
                return redirect(url_for('login'))
        # 更新最后活跃时间
        session['last_active'] = datetime.now()
    elif request.endpoint != 'login':
        # 用户未认证并且访问的不是登录接口，重定向到登录接口
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录接口"""
    if request.method == 'POST':
        # 获取用户提交的表单数据
        username = request.form['username']
        password = request.form['password']
        # 验证用户信息
        user = db_session.query(User).filter_by(username=username, password=password).first()
        if user:
            # 认证成功，保存用户信息到session
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('index'))
        else:
            # 认证失败，返回错误提示
            return 'Invalid username or password'
    else:
        # 返回登录页面
        return '''
            <form method="post">
                <input type="text" name="username" placeholder="username" required><br>
                <input type="password" name="password" placeholder="password" required><br>
                <input type="submit" value="Login">
            </form>
        '''


@app.route('/logout')
def logout():
    """用户注销接口"""
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))


# 首次安装时生成 root 用户
@app.before_first_request
def create_root_user():
    # 判断数据库是否存在 root 用户，如果存在则不创建
    root_user = db_session.query(User).filter_by(username='root').first()
    if not root_user:
        # 随机生成用户名和密码
        username = ''.join(random.choices(string.digits, k=10))
        password = 'cloud@Desk'
        # 对密码进行哈希加密
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        # 创建 root 用户并保存到数据库
        root_user = User(username=username, password=password_hash)
        db_session.add(root_user)
        db_session.commit()


# 管理员账号创建普通用户
@app.route('/api/create_user', methods=['POST'])
def create_user():
    # 验证用户是否为管理员
    # 省略验证代码
    # 获取请求参数
    username = request.json.get('username')
    password = request.json.get('password')
    # 验证密码是否符合规则
    # 省略验证代码
    # 对密码进行哈希加密
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    # 创建普通用户并保存到数据库
    user = User(username=username, password=password_hash)
    db_session.add(user)
    db_session.commit()
    return make_response('User created', 200)
