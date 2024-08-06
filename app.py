from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个密钥来加密session数据

# 配置SQL Server数据库连接
def get_db_connection():
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=localhost;'
                          'Database=database1;'
                          'Trusted_Connection=yes;')

    return conn

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and hashlib.sha256(password.encode('utf-8')).hexdigest() == user.password:
            session['username'] = username  # 将用户名存入session
            conn.close()
            return redirect(url_for('index'))  # 登录成功后重定向到主页
        else:
            conn.close()
            return '登录失败，请检查用户名和密码。'

    return render_template('login.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return '该用户名已被使用，请选择其他用户名。'
        else:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                           (username, hashed_password, email))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

    return render_template('register.html')

# 主页
@app.route('/index')
def index():
    if 'username' in session:
        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            user_data = {
                'username': user.username,
                'email': user.email
            }
            conn.close()
            return render_template('index.html', user=user_data)
        else:
            conn.close()
            return '用户不存在'
    else:
        return redirect(url_for('login'))  # 如果未登录，重定向到登录页面

# 主页跳转
@app.route('/homepage')
def homepage():
    if 'username' in session:
        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            user_data = {
                'username': user.username,
                'email': user.email
            }
            conn.close()
            return render_template('homepage.html', user=user_data)
        else:
            conn.close()
            return '用户不存在'
    else:
        return redirect(url_for('login'))  # 如果未登录，重定向到登录页面


# 退出登录
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
