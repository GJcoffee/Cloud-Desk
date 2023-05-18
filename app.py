import hashlib

from flask import Flask, redirect, url_for
from datetime import timedelta
from flask_migrate import Migrate
from Blueprints.vm import vm_bp
from Blueprints.auth import auth_bp
from conf.setting import DB_URI
from conf.exsits import db
from utils.db_model import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # 配置加密密钥
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 配置session过期时间为1小时
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# 配置数据库变更时是否发送信号到应用
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.template_folder = 'templates'

# 注册蓝图
app.register_blueprint(vm_bp)
app.register_blueprint(auth_bp)

# 数据库相关操作
db.init_app(app)
db_session = db.session
migrate = Migrate(app, db)

app_context = app.app_context()
app_context.push()
# 在应用程序上下文中执行数据库操作
db.create_all()
# 完成后记得弹出应用程序上下文
app_context.pop()


# 首页路由
@app.route('/')
def index():
    # 重定向到登录路由
    return redirect(url_for('auth.login'))

# 首次安装时生成 root 用户
@app.before_first_request
def create_root_user():
    # 判断数据库是否存在 root 用户，如果存在则不创建
    root_user = db_session.query(User).filter_by(username='root').first()
    if not root_user:
        # 随机生成用户名和密码
        username = 'root'
        password = 'cloud@Desk'
        # 创建 root 用户并保存到数据库
        root_user = User(username=username, password=password)
        db_session.add(root_user)
        db_session.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
