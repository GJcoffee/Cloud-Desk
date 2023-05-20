from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from conf.exsits import db


# 创建ORM模型
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(10), unique=True)
    password = Column(String(255))
    is_admin = Column(Integer, default=0)
    virtual_machines = relationship('VirtualMachine', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username


class VirtualMachine(db.Model):
    __tablename__ = 'virtual_machines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    memory = Column(Integer)
    vcpu = Column(Integer)
    disk_size = Column(Integer)
    mac_address = Column(String(30))
    ip_address = Column(String(30))
    port = Column(Integer)
    os = Column(String(30))
    desk_username = Column(String(30))
    desk_password = Column(String(30))
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship("User", back_populates="virtual_machines")


class DesktopApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100))
    vm_name = db.Column(db.String(100))
    desk_username = db.Column(db.String(100))
    desk_password = db.Column(db.String(100))
    memory = db.Column(db.Integer)
    vcpu = db.Column(db.Integer)
    disk_size = db.Column(db.Integer)
    os = db.Column(db.String(100))
    approval_status = db.Column(db.Integer, default=0)
