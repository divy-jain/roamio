from app import db

user_preferences = db.Table('user_preferences',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('preference_id', db.Integer, db.ForeignKey('preferences.id'), primary_key=True)
)

class Preference(db.Model):
    __tablename__ = 'preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    users = db.relationship('User',
                          secondary=user_preferences,
                          back_populates='preferences')

    def __repr__(self):
        return f'<Preference {self.name}>'

# Define the 20 preference tags
DEFAULT_PREFERENCES = [
    "Outdoor", "Cultural", "Historical", "Adventure", "Relaxation",
    "Photography", "Nature", "Urban", "Food", "Shopping",
    "Art", "Music", "Sports", "Wildlife", "Beach",
    "Mountains", "Local", "Nightlife", "Festival", "Wellness"
]