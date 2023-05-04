from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app import app

db = SQLAlchemy(app)


# 创建ORM模型
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(10), unique=True)
    password = Column(String(255))
    is_admin = Column(Integer, default=0)
    virtual_machines = relationship('VirtualMachine', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username


class VirtualMachine(db.model):
    __tablename__ = 'virtual_machines'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'))


# 创建数据访问会话
db.create_all()
db_session = db.session
