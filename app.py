from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Desktop

app = Flask(__name__)
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
