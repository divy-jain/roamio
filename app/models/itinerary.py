from app import db

# Association table for the many-to-many relationship between itineraries and activities
itinerary_activities = db.Table('itinerary_activities',
    db.Column('itinerary_id', db.Integer, db.ForeignKey('itineraries.id'), primary_key=True),
    db.Column('activity_id', db.Integer, db.ForeignKey('activities.id'), primary_key=True)  # Note: activities.id, not activity.id
)

class Itinerary(db.Model):
    __tablename__ = 'itineraries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Many-to-many relationship with Activity model using the itinerary_activities table
    activities = db.relationship('Activity', secondary=itinerary_activities, back_populates='itineraries')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, default=0)
    user = db.relationship('User', back_populates='itineraries')

    def __repr__(self):
        return f'<Itinerary {self.name}>'
