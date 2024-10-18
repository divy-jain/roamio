from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    activity = db.relationship('Activity', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return f'<Review {self.id}>'