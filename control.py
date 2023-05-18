from flask import render_template
from app import app_context

app_context.push()





# 完成后记得弹出应用程序上下文
app_context.pop()
