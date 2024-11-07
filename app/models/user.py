from ..extensions import db  # Importing the database instance from extensions
from flask_login import UserMixin #Useful for user authentication.
from werkzeug.security import generate_password_hash, check_password_hash #securely store and check user passwords by hashing them.

#All Registered Users
class User(UserMixin, db.Model):
    #id| username |email |passowrd_hash| 
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_visibility = db.Column(db.Boolean, default=True, nullable = False)  # True = public, False = private

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
    #reviews = db.relationship('Review', back_populates='user', lazy='dynamic')  # String reference