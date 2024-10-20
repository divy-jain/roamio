from app import db
from sqlalchemy import func
from app.models.review import Review  # Add this import

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.String(10), nullable=False)
    season = db.Column(db.String(20), nullable=False)

    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=True)

    reviews = db.relationship('Review', back_populates='activity', lazy='dynamic')

    @property
    def average_rating(self):
        return db.session.query(func.avg(Review.rating)).filter(Review.activity_id == self.id).scalar() or 0.0

    def __repr__(self):
        return f'<Activity {self.name}>'