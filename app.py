from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///instance/school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    parent_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    subject = db.Column(db.String(50))
    class_name = db.Column(db.String(20))
    contact_number = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database tables
def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123', role='admin')
            db.session.add(admin)
            db.session.commit()
        print("Database initialized successfully!")

# Call init_db when the app starts
init_db()

@app.route('/')
@login_required
def dashboard():
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    return render_template('dashboard.html', 
                          student_count=student_count, 
                          teacher_count=teacher_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/students')
@login_required
def students():
    all_students = Student.query.all()
    return render_template('students.html', students=all_students)

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    email = request.form['email']
    class_name = request.form['class']
    section = request.form['section']
    parent_name = request.form['parent_name']
    contact_number = request.form['contact_number']
    
    new_student = Student(
        name=name,
        email=email,
        class_name=class_name,
        section=section,
        parent_name=parent_name,
        contact_number=contact_number
    )
    
    db.session.add(new_student)
    db.session.commit()
    flash('Student added successfully!')
    return redirect(url_for('students'))

@app.route('/teachers')
@login_required
def teachers():
    all_teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=all_teachers)

@app.route('/add_teacher', methods=['POST'])
@login_required
def add_teacher():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    class_name = request.form['class']
    contact_number = request.form['contact_number']
    
    new_teacher = Teacher(
        name=name,
        email=email,
        subject=subject,
        class_name=class_name,
        contact_number=contact_number
    )
    
    db.session.add(new_teacher)
    db.session.commit()
    flash('Teacher added successfully!')
    return redirect(url_for('teachers'))

if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(debug=True)
