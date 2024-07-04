from flask import Flask, render_template, redirect, request
from flask import current_app as app

@app.route("/")
def home():
    return "<h1>hhuhuhu!</h1>"

@app.route("/login.html", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "1" and password == "1":
            return redirect(url_for('admins-dash.html'))
    return render_template("login.html")

@app.route('/admin-login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_databases()
        user_cursor = db.execute("select * from users where username= ? and password = ?", [username, password])
        user = user_cursor.fetchone()
        return redirect(url_for("home"))
    return render_template('login.html')

@app.route('/sponsor-register.html', methods=['POST', 'GET'])
def sponsor_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_databases()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)", [username, password])
        db.commit()
        return redirect(url_for('login.html'))
    return render_template('sponsor-register.html')

@app.route('/i_r.html', methods=['POST', 'GET'])
def i_r():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_databases()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)", [username, password])
        db.commit()
        return redirect(url_for('login.html'))
    return render_template('i_r.html')

@app.route('/campaigns')
def campaigns():
    return render_template('campaigns.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/admins-dash.html')
def admin_dash():
    return render_template('admins-dash.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/admin-login.html')
def admin_login():
    return render_template('admin-login.html')

@app.route('/s-r.html', methods=['GET', 'POST'])
def login_user():
    return render_template('s-r.html')