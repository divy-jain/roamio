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

# Route for user login, supports GET (to display the form) and POST (to handle form submission).
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect authenticated users directly to the main index.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()  # Create an instance of the login form.

    if form.validate_on_submit():  # Check if the form submission is valid.
        try:
            # Fetch the user from the database based on the submitted username.
            user = User.query.filter_by(username=form.username.data).first()
            
            # If user does not exist or password check fails, show an error message.
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))  # Reload the login page.
            
            # Log the user in and optionally remember their session.
            login_user(user, remember=form.remember_me.data)

            # Redirect to the requested page or the main index by default.
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        except Exception as e:  # Handle unexpected errors.
            logger.error(f"Login error: {e}")  # Log the error for debugging.
            flash('An error occurred during login. Please try again.', 'danger')

    # Render the login page with the form for GET requests or on failure.
    return render_template('auth/login.html', title='Sign In', form=form)


# Route for logging out the user.
@bp.route('/logout')
def logout():
    try:
        logout_user()  # Log out the current user.
        flash('You have been logged out successfully.', 'info')  # Notify the user.
        return redirect(url_for('main.index'))  # Redirect to the main page.
    except Exception as e:  # Handle any unexpected errors.
        logger.error(f"Logout error: {e}")  # Log the error for debugging.
        flash('An error occurred during logout.', 'danger')  # Notify the user of the issue.
        return redirect(url_for('main.index'))  # Redirect to the main page regardless.


# Route for user registration, supports GET (to display the form) and POST (to handle submission).
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect authenticated users to the main page.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()  # Instantiate the registration form.

    if form.validate_on_submit():  # Handle form submission.
        try:
            # Check if the username is already taken.
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return render_template('auth/register.html', title='Register', form=form)

            # Check if the email is already registered.
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered', 'danger')
                return render_template('auth/register.html', title='Register', form=form)

            # Create a new user with the submitted data.
            user = User(
                username=form.username.data,
                email=form.email.data,
                profile_visibility=form.profile_visibility.data
            )
            user.set_password(form.password.data)  # Hash and set the password.

            # Add the user to the database and commit.
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except SQLAlchemyError as e:  # Rollback if a database error occurs.
                db.session.rollback()
                logger.error(f"Database error: {e}")
                flash('Registration failed. Please try again.', 'danger')

        except Exception as e:  # Handle unexpected errors.
            logger.error(f"Registration error: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')

    # Render the registration form for GET requests or on failure.
    return render_template('auth/register.html', title='Register', form=form)
