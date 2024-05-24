from flask import Flask, request, redirect, url_for, render_template, send_from_directory,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
import bcrypt

app = Flask(__name__)
app.secret_key="secret"
# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/web_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

db = SQLAlchemy(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=True)
    phone_no = db.Column(db.String(14), nullable=True)
    address = db.Column(db.String(60), nullable=True)
    userpass = db.Column(db.String(255), nullable=False)

    def __init__(self,user_name,phone_no,address,email,userpass):
        self.user_name=user_name
        self.phone_no=phone_no
        self.address=address
        self.email=email
        self.userpass=userpass
    # bcrypt.hashpw(userpass.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
    def check_password(self,userpass):
        return bcrypt.checkpw(userpass.encode('utf-8'),self.userpass.encode('utf-8'))

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    vehicle_name = db.Column(db.String(50), nullable=True)
    vehicle_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    make = db.Column(db.String(60), nullable=True)
    model = db.Column(db.String(60), nullable=True)
    make_year = db.Column(db.Integer, nullable=True)
    licence_number = db.Column(db.String(20), nullable=True)

class RegistrationDocument(db.Model):
    __tablename__ = 'registration_documents'
    registration_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_name = db.Column(db.String(50), nullable=False)
    document_number = db.Column(db.String(20), unique=True, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)

class InsuranceDocument(db.Model):
    __tablename__ = 'insurance_documents'
    insurance_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    policy_number = db.Column(db.String(40), nullable=True)
    expire_date = db.Column(db.Date, nullable=True)
    upload_date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    file_path = db.Column(db.String(255), nullable=False)

class EmissionDocument(db.Model):
    __tablename__ = 'emissiondocuments'
    emission_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    certificate_number = db.Column(db.String(30), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)

# Create the tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user=User.query.filter_by(email=email).first()
        
        if user and user.userpass==password:
            print("valid")
            session['email']=email
            session['user_id']=user.user_id
            return redirect(url_for("home"))
        else:
            print("invalid")
            error="Incorrect Password"
            return render_template('/login.html',error=error)
    return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def home():
    if session['user_id']:
        user_id=session['user_id']
        user=User.query.filter_by(user_id=user_id).first()
        vehicles = Vehicle.query.filter_by(user_id=user_id).all()
        # print(user)
        # print(complaints_on_me )
        # print("Personal Complaints:", personal_complaints)
        # print("Department Complaints:", department_complaints)
        # print("Complaints On Me:", complaints_on_me)
        return render_template('/homepage.html',user=user,vehicles=vehicles)

    return render_template("homepage.html")



@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        user_name=request.form['user_name']
        phone_no=request.form['phone_no']
        address=request.form['address']
        email=request.form['email']
        user_password=request.form['user_password']
        
        user_exist=User.query.filter_by(email=email).first()
        if user_exist:
            error="User already Exists"
            return render_template('./sign_up.html',error=error)

        user=User(user_name=user_name,phone_no=phone_no,address=address,email=email,userpass=user_password)
        db.session.add(user)
        db.session.commit() 
        sucess="Registered Sucessfull Please login"
        return render_template('/sign_up.html',sucess=sucess)

    return render_template('/sign_up.html')

if __name__ == '__main__':
    app.run(debug=True)