from flask import Flask, abort, request, redirect, url_for, render_template, send_from_directory,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
import bcrypt
from datetime import datetime

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
    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    vehicle_name = db.Column(db.String(50), nullable=True)
    make = db.Column(db.String(60), nullable=True)
    model = db.Column(db.String(60), nullable=True)
    make_year = db.Column(db.Integer, nullable=True)
    licence_number = db.Column(db.String(20), nullable=True)

class RegistrationDocument(db.Model):
    __tablename__ = 'registration_documents'
    registration_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_name = db.Column(db.String(50), nullable=False)
    document_number = db.Column(db.String(20), unique=True, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    

class InsuranceDocument(db.Model):
    __tablename__ = 'insurance_documents'
    insurance_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    policy_number = db.Column(db.String(40), nullable=True)
    expire_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)

class EmissionDocument(db.Model):
    __tablename__ = 'emissiondocuments'
    emission_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    certificate_number = db.Column(db.String(30), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

# routes
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


@app.route('/add_vehicle',methods=['POST','GET'])
def add_vehicle():
    if request.method == 'POST':
        user_id =  session['user_id']
        vehicle_name = request.form['vehicle_name']
        make = request.form['make']
        model = request.form['model']
        make_year = request.form['make_year']
        licence_number = request.form['licence_number']

        vehicle=Vehicle(user_id=user_id,vehicle_name=vehicle_name,make=make,model=model,make_year=make_year,licence_number=licence_number)
        db.session.add(vehicle)
        db.session.commit()
        print("hi")
        vehicle_id = vehicle.vehicle_id
        return redirect(url_for('add_registeration', vehicle_id=vehicle_id))
    return render_template("/add_vehicle.html")


@app.route('/registeration/<int:vehicle_id>',methods=['POST','GET'])
def add_registeration( vehicle_id ):
    if request.method == 'POST':
        document_name = request.form['document_name']
        document_number = request.form['document_number']
        expiration_date = request.form['expiration_date']
        
        file = request.files['file_path']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return 'No file selected for uploading'
        
        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        
        new_document = RegistrationDocument(
            vehicle_id=vehicle_id,
            document_name=document_name,
            document_number=document_number,
            expiration_date=expiration_date,
            file_path=file_path
        )
        
        db.session.add(new_document)
        db.session.commit()
        return redirect(url_for("add_insurance",vehicle_id=vehicle_id))
    return render_template('/registeration.html',vehicle_id=vehicle_id)


@app.route('/insurance/<int:vehicle_id>',methods=['POST','GET'])
def add_insurance(vehicle_id):
    if request.method == 'POST':
        policy_number = request.form['policy_number']
        expire_date = request.form['expire_date']
        file_path = request.files['file_path']

        new_insurance = InsuranceDocument(
            vehicle_id=vehicle_id,
            policy_number=policy_number,
            expire_date=expire_date,
            file_path=file_path
        )

        db.session.add(new_insurance)
        db.session.commit()

        return redirect(url_for('add_emission', vehicle_id=vehicle_id))
    return render_template('/insurance.html',vehicle_id=vehicle_id)


@app.route('/emission<int:vehicle_id>',methods=['POST','GET'])
def add_emission(vehicle_id):
    if request.method == 'POST':
        certificate_number = request.form['certificate_number']
        issue_date = request.form['issue_date']
        expiration_date = request.form['expiration_date']
        file = request.files['file_path']
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return 'No file selected for uploading'
        
        if issue_date:
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        
        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        
        new_emission = EmissionDocument(
            vehicle_id=vehicle_id,
            certificate_number=certificate_number,
            issue_date=issue_date,
            expiration_date=expiration_date,
            file_path=file_path
        )
        db.session.add(new_emission)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('/emission.html',vehicle_id=vehicle_id)


@app.route('/view_documents/<int:vehicle_id>', methods=['GET'])
def view_documentts(vehicle_id):
    insurance_docs = InsuranceDocument.query.filter_by(vehicle_id=vehicle_id).all()
    registration_docs = RegistrationDocument.query.filter_by(vehicle_id=vehicle_id).all()
    emission_docs = EmissionDocument.query.filter_by(vehicle_id=vehicle_id).all()

    if not insurance_docs and not registration_docs and not emission_docs:
        abort(404, description="No documents found for the given vehicle ID")

    return render_template('display.html', 
                           vehicle_id=vehicle_id, 
                           insurance_docs=insurance_docs, 
                           registration_docs=registration_docs, 
                           emission_docs=emission_docs)


@app.route('/get_file/<path:file_path>')
def get_file(file_path):
    try:
        return send_from_directory(directory=os.path.dirname(file_path), 
                                   path=os.path.basename(file_path), 
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404, description="File not found")

@app.route('/admin')
def admin_users():
    users = User.query.all()
    return render_template('admin_user.html', users=users)


@app.route('/admin/users/<string:user_id>/vehicles')
def admin_user_vehicles(user_id):
    user = User.query.get_or_404(user_id)
    vehicles = Vehicle.query.filter_by(user_id=user_id).all()
    return render_template('admin_vehicle.html', user=user, vehicles=vehicles)


if __name__ == '__main__':
    app.run(debug=True)