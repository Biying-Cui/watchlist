from flask import Flask #从flask包导入Flask类
from flask import url_for
from flask import render_template

app = Flask(__name__) #通过实例化这个类，创建一个程序对象app

# @app.route('/') #注册处理函数（视图函数），使用app.route这个装饰器为函数绑定对应的URL：这里的/指根地址，完整URL是http://localhost:5000/
# @app.route('/index')
# @app.route('/home')
# def hello():
# 	# return '欢迎来到CBB的 Watchlist!'
# 	return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


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



@app.route('/')
def index():
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
	]
	
	return render_template('index.html',name=name,movies=movies)
