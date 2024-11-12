from datetime import datetime
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

    activities = db.relationship('Activity', back_populates='user')
    itineraries = db.relationship('Itinerary', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')

    friends = db.relationship('User', 
        secondary='friendships',
        primaryjoin='User.id==friendships.c.user_id',
        secondaryjoin='User.id==friendships.c.friend_id',
        backref='friended_by'
    )
# Add helper methods to User class
    def is_public(self):
        return self.profile_visibility

    def is_friend(self, user):
        return user in self.friends

    def can_view_profile(self, viewer):
    # Users can always view their own profile
        if viewer and viewer.id == self.id:
            return True
    # Public profiles can be viewed by anyone
        if self.profile_visibility:
            return True
    # Private profiles can only be viewed by friends
        return viewer and self in viewer.friends

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    

# Add this new model for friendships
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

#reviews = db.relationship('Review', back_populates='user', lazy='dynamic')  # String reference