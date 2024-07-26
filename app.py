from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField, SelectField
from wtforms.validators import Email, EqualTo, InputRequired
from os import path

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abcdefghijklm'
# Set session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'sponsor_login'
login_manager.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    info = db.Column(db.Text, nullable=True)

    @property
    def is_active(self):
        return True

class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[InputRequired()])
    lname = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    category = SelectField('Category', choices=[('it', 'I.T'), ('food', 'Food'), ('bank', 'Bank'), ('medicine', 'Medicine'), ('vehicles', 'Vehicles'), ('others', 'Others')], validators=[InputRequired()])
    role = RadioField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')], validators=[InputRequired()])
    info = TextAreaField('Info')

# Define the Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String(64))
    goals = db.Column(db.String(256))
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Define the AdRequest model
class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    messages = db.Column(db.String(256))
    requirements = db.Column(db.String(256))
    payment_amount = db.Column(db.Float)
    status = db.Column(db.String(64))

# Main routes
@app.route("/")
@app.route("/home")
def home():
    return render_template('sponsor-login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(
            fname=form.fname.data,
            lname=form.lname.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
            category=form.category.data,
            role=form.role.data,
            info=form.info.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password) and user.role == 'admin':
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin-login.html')

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    # Admin dashboard logic
    return render_template('admin_dashboard.html')


@app.route('/influencer-login', methods=['GET', 'POST'])
def influencer_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        print(f"Email: {email}, Password: {password}")  # Debugging statement
        if user and check_password_hash(user.password, password) and user.role == 'influencer':
            login_user(user)
            return redirect(url_for("influencer_dashboard"))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('influencer_login'))
    return render_template('influencer-login.html')

@app.route('/influencer-dashboard')
@login_required
def influencer_dashboard():
   return render_template('influencer_dashboard.html')


@app.route('/sponsor-login', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        print(f"Email: {email}, Password: {password}")  # Debugging statement
        if user and check_password_hash(user.password, password) and user.role == 'sponsor':
            login_user(user)
            return redirect(url_for("sponsor_dashboard"))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('sponsor_login'))
    return render_template('sponsor-login.html')

@app.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
   return render_template('sponsor_dashboard.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

# Authentication Blueprint
auth = Blueprint('auth', __name__)

# Create database and tables if they do not exist
if not path.exists('database.sqlite3'):
    with app.app_context():
        db.create_all()
        print('Database and tables created!')

if __name__ == '__main__':
    app.run(debug=True)
