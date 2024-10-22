from app import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    activity = db.relationship('Activity', back_populates='reviews')  # String reference

    def __repr__(self):
        return f'<Review {self.id}>'
