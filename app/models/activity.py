from app import db

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    average_rating = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Activity {self.name}>'