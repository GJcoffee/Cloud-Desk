import requests


def get_data():
    res = requests.get(url='http://127.0.0.1:8000/api/certificate/tasks')
    return res.json()


def insert_data(json_data):
    res = requests.put(url='http://127.0.0.1:8000/api/certificate/tasks/add_task', json=json_data)
    return res.json()


def up_load_task():
    res = requests.post(url='http://127.0.0.1:8000/api/certificate/tasks')
    res.json()
