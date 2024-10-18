from app import create_app, db
from app.models.user import User
from app.models.activity import Activity
from app.models.itinerary import Itinerary
from app.models.review import Review

app = create_app()

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Check if there's already data in the database
        if User.query.first() is not None:
            print("Database already contains data. Skipping initialization.")
            return

        # Create sample users
        user1 = User(username="john_doe", email="john@example.com")
        user1.set_password("password123")
        user2 = User(username="jane_smith", email="jane@example.com")
        user2.set_password("password456")

        # Create sample activities
        activity1 = Activity(name="Eiffel Tower Visit", description="Visit the iconic Eiffel Tower", 
                             city="Paris", activity_type="Sightseeing", cost="$$", season="All Year")
        activity2 = Activity(name="Louvre Museum Tour", description="Explore world-famous artworks", 
                             city="Paris", activity_type="Culture", cost="$$", season="All Year")
        activity3 = Activity(name="Tokyo Skytree", description="Visit the tallest tower in Japan", 
                             city="Tokyo", activity_type="Sightseeing", cost="$$", season="All Year")

        # Create sample itineraries
        itinerary1 = Itinerary(name="Paris Adventure", user=user1)
        itinerary1.activities.extend([activity1, activity2])

        # Create sample reviews
        review1 = Review(content="Amazing view of Paris!", rating=5, user=user1, activity=activity1)
        review2 = Review(content="Crowded but worth it", rating=4, user=user2, activity=activity1)

        # Add all objects to the session and commit
        db.session.add_all([user1, user2, activity1, activity2, activity3, itinerary1, review1, review2])
        db.session.commit()

        print("Database initialized with sample data.")

if __name__ == "__main__":
    init_db()