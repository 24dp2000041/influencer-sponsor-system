from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from database import get_databases
from models import User, Campaign, AdRequest
from werkzeug.security import generate_password_hash,  check_password_hash

# def init_app():
app = Flask(__name__)
# #     app.debug = True
#     print("hihihih")
#     return app

# app = init_app()
# from backend.controllers import *

@app.route("/")
@app.route("/home")
def home():
    return render_template('admins-dash.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def login():
        # Handle login logic here
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        # sql entry dhd
        db = get_databases()
        user_cursor= db.execute("select * from users where username= ? and password = ?" ,  [username, password])
        user =  user_cursor.fetchone()
        # make change permanent
        # db.commit()
        return redirect(url_for("home"))
    
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collectinf from form
        username = request.form['username']
        password = request.form['password']
        # sql entry dhd
        db = get_databases()
        db.execute("INSERT INTO users (username, password) VALUE (?,?)", [username, password])
        # make change permanent
        db.commit()
        return redirect(url_for('login.html'))
    return render_template('influencer-register.html')




@app.route('/admin/dashboard')
def admin_dashboard():
    # Admin dashboard logic
    return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/admin-login.html')
def admin_login():
    return render_template('admin-login.html')





if __name__ == '__main__':
    app.run(debug=True)