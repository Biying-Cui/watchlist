import os
import sys

import click

from flask import Flask #从flask包导入Flask类
from flask import url_for
from flask import render_template
from flask import request  #请求触发后把请求信息放到request对象里
from flask import flash  #flash()函数用于在视图函数里向模板传递提示消息
from flask import redirect

from flask_sqlalchemy import SQLAlchemy # 导入扩展类

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_required, logout_user
from flask_login import current_user
from flask_login import login_user

WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统，使用三个斜线
	prefix = 'sqlite:///'
else: # 否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__) #通过实例化这个类，创建一个程序对象app
app.config['SECRET_KEY'] = 'dev'

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户 ID 作为参数
	user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
	return user   # 返回用户对象

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
#@click.option('--drop', is_flag = True, help = 'Create after drop')
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')

#执行 flask admin 命令，输入用户名和密码后，即可创建管理员账户。
def admin(username, password):
	"""Create user."""
	db.create_all()

	user = User.query.first()
	if user is not None:
		click.echo('Updating user...')
		user.username = username
		user.set_password(password) #设置密码
	else:
		click.echo('Creating user...')
		user = User(username = username, name = 'Admin')
		user.set_password(password)
		db.session.add(user)

	db.session.commit() #提交数据库会话
	click.echo('Done.')

def initdb(drop): 
	if drop:
		db.drop_all()
	db.create_all()
	click.echo('Initialized database.') 




#创建数据库模型：
#让存储用户的 User 模型类继承 Flask-Login 提供的 UserMixin类,
class User(db.Model, UserMixin): # 表名将会是 user（自动生成，小写处理） 
	id = db.Column(db.Integer, primary_key=True) # 主键
	name = db.Column(db.String(20)) # 名字
	username = db.Column(db.String(20)) #用户名
	password_hash = db.Column(db.String(128)) #密码散列值

	def set_password(self, password): # 用来设置密码的方法，接受密码作为参数
		self.password_hash = generate_password_hash(password) #将生成的密码保持到对应字段
	
	def validate_password(self, password): # 用于验证密码的方法，接受密码作为参数
		return check_password_hash(self.password_hash, password) #返回布尔值

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
		{'title': '可爱的CBB', 'year': '2021'},

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

@app.route('/', methods = ['GET', 'POST'])
def index():
	if request.method == 'POST':  #判断是否是POST请求
		#获取表单数据
		
		if not current_user.is_authenticated: # 如果当前用户未认证
			return redirect(url_for('index'))

		title = request.form.get('title')
		year = request.form.get('year')

		#输入数据为空或者长度不符合要求
		if not title or not year or len(year)>4 or len(title)>60:
			flash('Invalid input.') #显示错误提示
			return redirect(url_for('index')) #重新定向回主页
		#保存表单数据到数据库
		movie = Movie(title=title, year=year)
		db.session.add(movie) #添加到数据库会话
		db.session.commit() #提交数据库会话
		flash('Item created.')
		return redirect(url_for('index'))

	user = User.query.first()
	movies = Movie.query.all()
	return render_template('index.html', user = user, movies = movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
@login_required
def edit(movie_id): #编辑条目
	movie = Movie.query.get_or_404(movie_id) #get_or_404()方法：返回对应主键的记录，没找到则返回404错误相应

	if request.method == 'POST':
		title = request.form['title']
		year = request.form['year']

		if not title or not year or len(year)>4 or len(title)>60:
			flash('Invalid input.') #显示错误提示
			return redirect(url_for('edit', movie_id=movie_id)) #重新定向回对应的编辑页面
		#保存表单数据到数据库
		movie.title = title #更新标题
		movie.year = year  #更新年份
		
		db.session.commit() #提交数据库会话
		flash('Item updated.')
		return redirect(url_for('index'))

	return render_template('edit.html', movie = movie) 


@app.route('/movie/delete/<int:movie_id>', methods=['POST']) #限定只接受 POST 请求
@login_required
def delete(movie_id):
	movie = Movie.query.get_or_404(movie_id) # 获取电影记录
	db.session.delete(movie) # 删除对应的记录
	db.session.commit() # 提交数据库会话
	flash('Item deleted.')
	return redirect(url_for('index')) # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		if not username or not password:
			flash('Invalid input.')
			return redirect(url_for('login'))

		user = User.query.first()
		if username == user.username and user.validate_password(password):
			login_user(user)
			flash('Login success.')
			return redirect(url_for('index'))

		flash('Invalid username or password.') # 如果验证失败，显示错误消息
		return redirect(url_for('login'))

	return render_template('login.html')

@app.route('/logout')
@login_required #用于视图保护
def logout():
	logout_user() #登出用户
	flash('Goodbye.')
	return redirect(url_for('index'))

@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
	if request.method == 'POST':
		name = request.form['name']

		if not name or len(name) > 20:
			flash('Invalid input.')
			return redirect(url_for('settings'))

		current_user.name = name
		# current_user会返回当前登录用户的数据库记录对象
		# 等同于下面的用法：
		# user = User.query.first()
		# user.name = name
		db.session.commit()
		flash('Settings updated.')
		return redirect(url_for('index'))

	return render_template('settings.html')
