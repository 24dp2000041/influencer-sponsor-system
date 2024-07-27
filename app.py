import os
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField,FileField, RadioField, SelectField ,SubmitField
from wtforms.validators import Email, EqualTo, DataRequired
from werkzeug.utils import secure_filename
from os import path

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abcdefghijklm'
# Set session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=55)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
ALLOWED_MIME_TYPES = {'image/jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_mime_type(file):
    return file.mimetype in ALLOWED_MIME_TYPES

# Initialize the database
db = SQLAlchemy(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'sponsor_login'
login_manager.init_app(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)        
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    info = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(100), default='default.jpeg')
    rating = db.Column(db.Integer)
    earnings = db.Column(db.Float)

    @property
    def is_active(self):
        return True
    
    
# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    category = StringField('Category', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture', validators=[DataRequired()])
    info = TextAreaField('Info', validators=[DataRequired()])
    role = RadioField('Role', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer')], validators=[DataRequired()])
    submit = SubmitField('Submit')

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
    
    def __repr__(self):
        return f'<Campaign id={self.id} name={self.name}>'
    


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(500))  # Ensure this matches your schema
    status = db.Column(db.String(64), default='Pending')  # Added default status

    campaign = db.relationship('Campaign', backref='ad_requests')
    influencer = db.relationship('User', backref='ad_requests')
    
    def __repr__(self):
        return f'<AdRequest id={self.id} campaign_id={self.campaign_id} influencer_id={self.influencer_id} status={self.status}>'










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
        profile_pic = form.profile_pic.data
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
            profile_pic=filename,
            info=form.info.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('register'))
    return render_template('temp.html', form=form)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        print(f"Email: {email}, Password: {password}")  # Debugging statement
        if user and check_password_hash(user.password, password) and user.role == 'admin':
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    # Admin dashboard logic
    return render_template('admin_dashboard.html',fname=current_user.fname,profile_pic=current_user.profile_pic)


@app.route('/influencer_login', methods=['GET', 'POST'])
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

@app.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
     return render_template('influencer_dashboard.html',user=current_user,fname=current_user.fname,rating=current_user.rating, earnings=current_user.earnings,profile_pic=current_user.profile_pic)



@app.route('/update_user_details', methods=['POST'])
def update_user_details():
    user = current_user  # Assuming you're using Flask-Login and current_user is the logged-in user
    user.fname = request.form['fname']
    user.lname = request.form['lname']
    user.email = request.form['email']
    user.category = request.form['category']
    user.role = request.form['role']
    user.info = request.form['info']
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))


@app.route('/update_user_detail_influencer', methods=['POST'])
@login_required
def update_user_detail_influencer():
    user = current_user  # Assuming you're using Flask-Login and current_user is the logged-in user
    user.fname = request.form['fname']
    user.lname = request.form['lname']
    user.email = request.form['email']
    user.category = request.form['category']
    user.role = request.form['role']
    user.info = request.form['info']
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))


@app.route('/delete_requests', methods=['POST'])
@login_required
def delete_requests():
    request_ids = request.form.getlist('request_ids')
    if request_ids:
        AdRequest.query.filter(AdRequest.id.in_(request_ids)).delete(synchronize_session=False)
        db.session.commit()
        flash('Request deleted successfully!', 'success')
    return redirect(url_for('request_s'))

@app.route('/delete_requesti/<int:id>', methods=['POST'])
@login_required
def delete_requesti(id):
    request_to_delete = AdRequest.query.get_or_404(id)
    db.session.delete(request_to_delete)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('request_i'))


@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        User.profile_pic = filename
        db.session.commit()
        flash('Profile picture updated successfully')
        return redirect(url_for('influencer_dashboard'))

@app.route('/update_profile_pic1', methods=['POST'])
def update_profile_pic1():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        User.profile_pic = filename
        db.session.commit()
        flash('Profile picture updated successfully')
        return redirect(url_for('admin_dashboard'))

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
   return render_template('sponsor_dashboard.html',fname=current_user.fname,user=current_user)

@app.route('/request_s')
@login_required
def request_s():
    requests = AdRequest.query.all()
    return render_template('request_s.html', requests=requests)

@app.route('/request_i')
@login_required
def request_i():
    requests = AdRequest.query.all()
    return render_template('request_i.html', requests=requests)





@app.route('/campaigni')
@login_required
def campaigni():
    # Fetch all campaigns from the database
    all_campaigns = Campaign.query.all()
    return render_template('campaigni.html', campaigns=all_campaigns)


@app.route('/campaigns')
@login_required
def campaigns():
    # Fetch all campaigns from the database
    all_campaigns = Campaign.query.all()
    return render_template('campaigns.html', campaigns=all_campaigns)


@app.route('/register_campaign', methods=['POST'])
@login_required
def register_campaign():
    campaign_name = request.form['campaign_name']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    budget = request.form['budget']
    visibility = request.form['visibility']
    goals = request.form['goals']
    
    new_campaign = Campaign(
        name=campaign_name,
        description=description,
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
        budget=float(budget),
        visibility=visibility,
        goals=goals,
        sponsor_id=current_user.id
    )
    
    db.session.add(new_campaign)
    db.session.commit()
    
    flash('Campaign registered successfully!', 'success')
    return redirect(url_for('campaigns'))


@app.route('/find_influencer', methods=['GET', 'POST'])
@login_required
def find_influencer():
    search_query = request.args.get('search', '')
    influencers = None
    if search_query:
        influencers = User.query.filter(
            User.role == 'Influencer',
            (User.fname.ilike(f'%{search_query}%') | 
            User.lname.ilike(f'%{search_query}%') |
            User.email.ilike(f'%{search_query}%'))
        ).all()
    else:
        influencers = User.query.filter_by(role='Influencer').all()

    return render_template('find_influencer.html', influencers=influencers)









@app.route('/find_sponsor', methods=['GET', 'POST'])
@login_required
def find_sponsor():
    search_query = request.args.get('search', '')
    
    if search_query:
        # Search in Campaigns
        campaigns = Campaign.query.filter(
            Campaign.name.ilike(f'%{search_query}%') |
            Campaign.description.ilike(f'%{search_query}%')
        ).all()

        # Search in Influencers
        influencers = User.query.filter(
            (User.fname.ilike(f'%{search_query}%')) |
            (User.lname.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        ).filter(User.role == 'influencer').all()
    else:
        # If no search query, fetch all data
        campaigns = Campaign.query.all()
        influencers = User.query.filter(User.role == 'influencer').all()

    return render_template('find_sponsor.html', campaigns=campaigns, influencers=influencers)




@app.route('/find_admin', methods=['GET'])
@login_required
def find_admin():
    search_query = request.args.get('find_admin')
    
    # Search in Campaigns
    campaigns = Campaign.query.filter(
        Campaign.name.ilike(f'%{search_query}%') |
        Campaign.description.ilike(f'%{search_query}%')
    ).all()

    # Search in Influencers
    influencers = User.query.filter(
        (User.fname.ilike(f'%{search_query}%')) |
        (User.lname.ilike(f'%{search_query}%')) |
        (User.email.ilike(f'%{search_query}%'))
    ).filter(User.role == 'admin').all()

    return render_template('find_admin.html', campaigns=campaigns, influencers=influencers)




# Route to update campaign
@app.route('/update_campaign/<int:id>', methods=['POST'])
@login_required
def update_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    campaign.name = request.form['name']
    campaign.description = request.form['description']
    
    # Convert string to date object
    campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    
    campaign.budget = float(request.form['budget'])  # Convert budget to float
    campaign.visibility = request.form['visibility']
    campaign.goals = request.form['goals']
    
    db.session.commit()
    flash('Campaign updated successfully!', 'success')
    return redirect(url_for('campaigns'))

# Route to delete campaign
@app.route('/delete_campaign/<int:id>', methods=['POST'])
@login_required
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('campaigns'))

# Route to send request to influencer
@app.route('/send_request/<int:id>', methods=['POST'])
@login_required
def send_request(id):
    influencer = User.query.get_or_404(id)
    message = request.form['message']
    # Handle sending the request here (e.g., save to database, send email, etc.)
    flash(f'Request sent to {influencer.fname} {influencer.lname}!', 'success')
    return redirect(url_for('find_sponsor'))

@app.route('/send_requesti/<int:id>', methods=['POST'])
@login_required
def send_requesti(id):
    influencer = User.query.get_or_404(id)
    message = request.form['message']
    # Handle sending the request here (e.g., save to database, send email, etc.)
    flash(f'Request sent to {influencer.fname} {influencer.lname}!', 'success')
    return redirect(url_for('find_influencer'))



@app.route('/send_request1', methods=['POST'])
@login_required
def send_request1():
    influencer_id = request.form.get('influencer_id')
    message = request.form.get('message')
    campaign_id = request.form.get('campaign_id')  # Assuming you are sending a campaign_id as well

    # Logic to create a new AdRequest
    new_request = AdRequest(
        influencer_id=influencer_id,
        campaign_id=campaign_id,
        message=message,
        status='Pending'
    )
    db.session.add(new_request)
    db.session.commit()

    return redirect(url_for('request_s'))





@app.route('/send_requestt/<int:campaign_id>', methods=['POST'])
@login_required
def send_requestt(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    message = request.form['message']
    
    # Create a new AdRequest
    new_request = AdRequest(
        campaign_id=campaign.id,
        influencer_id=current_user.id,
        message=message,
        status='Pending'
    )
    db.session.add(new_request)
    db.session.commit()
    
    flash(f'Request sent to the campaign {campaign.name}!', 'success')
    return redirect(url_for('campaigni'))


@app.route('/update_request_status/<int:request_id>/<status>', methods=['POST'])
@login_required
def update_request_status(request_id, status):
    valid_statuses = ['Accepted', 'Rejected']
    if status not in valid_statuses:
        return redirect(url_for('request_s'))

    request_entry = AdRequest.query.get_or_404(request_id)
    request_entry.status = status
    db.session.commit()

    return redirect(url_for('request_s'))




@app.route('/some_route', methods=['POST'])
def some_route():
    # Some logic
    flash('Your message here', 'success')
    return redirect(url_for('request_s'))


@app.route('/stats_admin')
@login_required
def stats_admin():
    # Query the database to get counts
    accepted_count = AdRequest.query.filter_by(status='Accepted').count()
    rejected_count = AdRequest.query.filter_by(status='Rejected').count()
    pending_count = AdRequest.query.filter_by(status='Pending').count()

    # Render the template with the queried data
    return render_template('stats_admin.html', 
                           accepted_count=accepted_count, 
                           rejected_count=rejected_count, 
                           pending_count=pending_count)





@app.route('/stats_sponsor')
@login_required
def stats_sponsor():
    # Query the database to get counts
    accepted_count = AdRequest.query.filter_by(status='Accepted').count()
    rejected_count = AdRequest.query.filter_by(status='Rejected').count()
    pending_count = AdRequest.query.filter_by(status='Pending').count()

    # Render the template with the queried data
    return render_template('stats_sponsor.html', 
                           accepted_count=accepted_count, 
                           rejected_count=rejected_count, 
                           pending_count=pending_count)





@app.route('/stats_influencer')
@login_required
def stats_influencer():
    # Query the database to get counts
    accepted_count = AdRequest.query.filter_by(status='Accepted').count()
    rejected_count = AdRequest.query.filter_by(status='Rejected').count()
    pending_count = AdRequest.query.filter_by(status='Pending').count()

    # Render the template with the queried data
    return render_template('stats_influencer.html', 
                           accepted_count=accepted_count, 
                           rejected_count=rejected_count, 
                           pending_count=pending_count)





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
