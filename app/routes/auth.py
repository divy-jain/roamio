from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User
from ..forms import RegistrationForm, LoginForm
import logging
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    try:
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Logout error: {e}")
        flash('An error occurred during logout.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            existing_user = User.query.filter_by(
                username=form.username.data).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return render_template('auth/register.html', 
                                    title='Register', form=form)

            existing_email = User.query.filter_by(
                email=form.email.data).first()
            if existing_email:
                flash('Email already registered', 'danger')
                return render_template('auth/register.html', 
                                    title='Register', form=form)

            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                profile_visibility=form.profile_visibility.data  # Capture visibility setting
            )
            user.set_password(form.password.data)
            
            # Add and commit within a transaction
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error: {e}")
                flash('Registration failed. Please try again.', 'danger')
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)