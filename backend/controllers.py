<<<<<<< Current
from flask import Flask, render_template,redirect,request
=======
from flask import Flask, render_template, redirect, request


>>>>>>> Suggested by Tabnine
from flask import current_app as app

http://127.0.0.1:3000/admin-login



@app.route('/admin-login' methods=['GET' , 'POST'])
def admin-login():
    return render_template('admin-dash.html')

if __name__ == '__main__':
<<<<<<< Current
    app.run()


@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
=======
>>>>>>> Suggested by Tabnine
