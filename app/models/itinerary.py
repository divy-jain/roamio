from app import db

itinerary_activities = db.Table('itinerary_activities',
    db.Column('itinerary_id', db.Integer, db.ForeignKey('itinerary.id'), primary_key=True),
    db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'), primary_key=True)
)

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activities = db.relationship('Activity', secondary=itinerary_activities, lazy='subquery',
                                 backref=db.backref('itineraries', lazy=True))

    def __repr__(self):
        return f'<Itinerary {self.name}>'