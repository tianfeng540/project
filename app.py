from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return "<h1>这是我的项目首页<h1>"