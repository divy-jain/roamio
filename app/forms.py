from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ActivityForm(FlaskForm):
    name = StringField('Activity Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    activity_type = SelectField('Activity Type', choices=[
        ('Sightseeing', 'Sightseeing'),
        ('Adventure', 'Adventure'),
        ('Culture', 'Culture'),
        ('Relaxation', 'Relaxation'),
        ('Food & Drink', 'Food & Drink')
    ], validators=[DataRequired()])
    cost = SelectField('Cost', choices=[
        ('$', '$'),
        ('$$', '$$'),
        ('$$$', '$$$'),
        ('$$$$', '$$$$')
    ], validators=[DataRequired()])
    season = SelectField('Season', choices=[
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Autumn', 'Autumn'),
        ('Winter', 'Winter'),
        ('All Year', 'All Year')
    ], validators=[DataRequired()])
    rating = IntegerField('Rating (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Create Activity')

class AddToItineraryForm(FlaskForm):
    activity_id = SelectField('Select Activity', coerce=int)  # Populate this field dynamically
    submit = SubmitField('Add to Itinerary')

class AddActivityForm(FlaskForm):
    activity_id = SelectField('Activity', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Activity')

# New Itinerary Form
class CreateItineraryForm(FlaskForm):
    name = StringField('Itinerary Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Create Itinerary')
