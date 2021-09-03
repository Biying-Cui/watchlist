import os
import sys

import click

from flask import Flask #从flask包导入Flask类
from flask import url_for
from flask import render_template

from flask_sqlalchemy import SQLAlchemy # 导入扩展类

WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统，使用三个斜线
	prefix = 'sqlite:///'
else: # 否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__) #通过实例化这个类，创建一个程序对象app


# @app.route('/') #注册处理函数（视图函数），使用app.route这个装饰器为函数绑定对应的URL：这里的/指根地址，完整URL是http://localhost:5000/
# @app.route('/index')
# @app.route('/home')
# def hello():
# 	# return '欢迎来到CBB的 Watchlist!'
# 	return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址：
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控

# 在扩展类实例化前加载配置
db = SQLAlchemy(app) # 初始化扩展，传入程序实例 app

# @app.route('/user/<name>')
def user_page(name):
	return 'User: %s' %name
# # 整个请求的处理过程如下所示：
# # 1. 当用户在浏览器地址栏访问这个地址，在这里即 http://localhost:5000/
# # 2. 服务器解析请求，发现请求 URL 匹配的 URL 规则是 / ，因此调用对应的处
# # 理函数 hello()
# # 3. 获取 hello() 函数的返回值，处理后返回给客户端（浏览器）
# # 4. 浏览器接受响应，将其显示在窗口上

@app.route('/test')
def test_url_for():
	# 下面是一些调用示例（请在命令行窗口查看输出的 URL）：
	# print(url_for('hello'))   # 输出：/
	print(url_for('user_page', name='greyli')) # 输出：/user/greyli
	print(url_for('test_url_for')) # 输出：/test
# 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL后面。
	print(url_for('test_url_for', num=2)) # 输出：/test?num=2
	return 'Test page'



# @app.route('/')
# def index():
# 	# name = 'CBB'
# 	# movies = [
# 	# {'title': 'My Neighbor Totoro', 'year': '1988'},
# 	# {'title': 'Dead Poets Society', 'year': '1989'},
# 	# {'title': 'A Perfect World', 'year': '1993'},
# 	# {'title': 'Leon', 'year': '1994'},
# 	# {'title': 'Mahjong', 'year': '1996'},
# 	# {'title': 'Swallowtail Butterfly', 'year': '1996'},
# 	# {'title': 'King of Comedy', 'year': '1999'},
# 	# {'title': 'Devils on the Doorstep', 'year': '1999'},
# 	# {'title': 'WALL-E', 'year': '2008'},
# 	# {'title': 'The Pork of Music', 'year': '2012'},
# 	# ]
# 	user = User.query.first()
# 	movies = Movie.query.all()
# 	return render_template('index.html', user=user, movies=movies)

@app.cli.command()
@click.option('--drop', is_flag = True, help = 'Create after drop')

def initdb(drop): 
	if drop:
		db.drop_all()
	db.create_all()
	click.echo('Initialized database.') 




#创建数据库模型：
class User(db.Model): # 表名将会是 user（自动生成，小写处理）
	id = db.Column(db.Integer, primary_key=True) # 主键
	name = db.Column(db.String(20)) # 名字

class Movie(db.Model): # 表名将会是 movie
	id = db.Column(db.Integer, primary_key=True) # 主键
	title = db.Column(db.String(60)) # 电影标题
	year = db.Column(db.String(4)) # 电影年份

@app.cli.command()
def forge():
	"""Generate fake data."""
	db.create_all()
	# 全局的两个变量移动到这个函数内
	name = 'CBB'
	movies = [
		{'title': 'My Neighbor Totoro', 'year': '1988'},
		{'title': 'Dead Poets Society', 'year': '1989'},
		{'title': 'A Perfect World', 'year': '1993'},
		{'title': 'Leon', 'year': '1994'},
		{'title': 'Mahjong', 'year': '1996'},
		{'title': 'Swallowtail Butterfly', 'year': '1996'},
		{'title': 'King of Comedy', 'year': '1999'},
		{'title': 'Devils on the Doorstep', 'year': '1999'},
		{'title': 'WALL-E', 'year': '2008'},
		{'title': 'The Pork of Music', 'year': '2012'},
		{'title': '令人伤心的阳锅', 'year': '2021'},
	]
	user = User(name=name)
	db.session.add(user)
	for m in movies:
		movie = Movie(title=m['title'], year=m['year'])
		db.session.add(movie)
	db.session.commit()
	click.echo('Done.')


#404错误处理函数
# @app.errorhandler(404) # 传入要处理的错误代码
# def page_not_found(e): # 接受异常对象作为参数
# 	user = User.query.first()
# 	return render_template('404.html', user=user), 404 # 返回模板和状态码

#对于多个模板内都需要使用的变量，我们可以使用 app.context_processor 装饰器注册一个模板上下文处理函数
@app.context_processor
def inject_user(): # 函数名可以随意修改
	user = User.query.first()
	return dict(user=user) # 需要返回字典，等同于return {'user': user}

#以删除 404 错误处理函数和主页视图函数中的 user 变量定义，并删除在 render_template() 函数里传入的关键字参数
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route('/')
def index():
	movies = Movie.query.all()
	return render_template('index.html', movies=movies)
