from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the username or email already exists
        existing_user = db.session.execute(
            'SELECT * FROM user WHERE username = :username OR email = :email',
            {'username': username, 'email': email}
        ).fetchone()

        if existing_user:
            flash('Username or email already exists!')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)

        # Insert the new user into the database
        db.session.execute(
            'INSERT INTO user (username, email, password) VALUES (:username, :email, :password)',
            {
                'username': user.username,
                'email': user.email,
                'password': user.password  # Ensure that the password is hashed before storing
            }
        )
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user by username
        user = db.session.execute(
            'SELECT * FROM user WHERE username = :username',
            {'username': username}
        ).fetchone()

        if user is None or not User.check_password(user['password'], password):  # Adjust this check as needed
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(User(**user))  # Create a User object from the fetched data
        return redirect(url_for('index'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
