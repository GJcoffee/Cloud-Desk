from flask import Flask
from datetime import timedelta
from utils.db_model import db, db_session
from flask_migrate import Migrate
from Blueprints.vm import vm_bp
from Blueprints.auth import auth_bp
from conf.setting import DB_URI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # 配置加密密钥
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 配置session过期时间为1小时
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# 配置数据库变更时是否发送信号到应用
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 注册蓝图
app.register_blueprint(vm_bp)
app.register_blueprint(auth_bp)

# 数据库相关操作
migrate = Migrate(app, db)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
