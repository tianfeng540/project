import os
import sys
import click

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'  # 如果是windows系统，三个斜杠
else:
    prefix = 'sqlite:////'  # Mac，Linux，四个斜杠

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)


# 创建数据库模型类
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 自定义initdb
@app.cli.command()
@click.option('--drop', is_flag=True, help='删除之后再创建')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('初始化数据库')


# 自定义命令forge，把数据写入数据库
@app.cli.command()
def forge():
    db.create_all()
    name = "Bruce"
    movies = [
        {'title': '杀破狼', 'year': '2003'},
        {'title': '扫毒', 'year': '2018'},
        {'title': '捉妖记', 'year': '2016'},
        {'title': '囧妈', 'year': '2020'},
        {'title': '葫芦娃', 'year': '1989'},
        {'title': '玻璃盒子', 'year': '2020'},
        {'title': '调酒师', 'year': '2020'},
        {'title': '釜山行', 'year': '2017'},
        {'title': '导火索', 'year': '2005'},
        {'title': '叶问', 'year': '2015'}
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('数据导入完成')


# 首页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取表单的数据
        title = request.form.get('title')
        year = request.form.get('year')

        # 验证title，year不为空，并且title长度不大于60，year的长度不大于4
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误')  # 错误提示
            return redirect(url_for('index'))  # 重定向回主页

        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('数据创建成功')
        return redirect(url_for('index'))

    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',movies=movies)


# 编辑电影信息页面
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误')
            return redirect(url_for('edit'), movie_id=movie_id)

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('电影信息已经更新')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


# 删除信息
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('删除数据成功')
    return redirect(url_for('index'))


#出来页面404错误
@app.errorhandler(404)  
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404


# 模板上下文处理函数，在多个模板内都需要使用的变量
@app.context_processor  
def inject_user():
    user = User.query.first()
    return dict(user=user)