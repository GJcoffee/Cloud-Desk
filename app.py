from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # 配置加密密钥
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 配置session过期时间为1小时
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@hostname/database'
# 配置数据库变更时是否发送信号到应用
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine('sqlite:///cloud_desktops.db')
Session = sessionmaker(bind=engine)


@app.route('/desktops', methods=['POST'])
def create_desktop():
    name = request.json['name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    disk = request.json['disk']
    desktop = Desktop(name=name, cpu=cpu, memory=memory, disk=disk)
    session = Session()
    session.add(desktop)
    session.commit()
    session.close()
    return {'status': 'success'}
