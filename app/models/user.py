from datetime import datetime
from ..extensions import db  
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash 
from .friendship import FriendRequest, FriendshipStatus
from .preference import Preference, user_preferences

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_visibility = db.Column(db.Boolean, default=True, nullable=False)  # True = public, False = private

    activities = db.relationship('Activity', back_populates='user')
    itineraries = db.relationship('Itinerary', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')

    sent_requests = db.relationship('FriendRequest',
        foreign_keys='FriendRequest.sender_id',
        back_populates='sender',
        lazy='dynamic'
    )
    
    received_requests = db.relationship('FriendRequest',
        foreign_keys='FriendRequest.receiver_id',
        back_populates='receiver',
        lazy='dynamic'
    )

    preferences = db.relationship('Preference',
                               secondary=user_preferences,
                               back_populates='users')
    def is_public(self):
        return self.profile_visibility

    def can_view_profile(self, viewer):
        # Users can always view their own profile
        if viewer and viewer.id == self.id:
            return True
        # Public profiles can be viewed by anyone
        if self.profile_visibility:
            return True
        # Private profiles can only be viewed by friends
        return viewer and self.is_friend_with(viewer)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def send_friend_request(self, receiver):
        """Send a friend request to another user"""
        if receiver.id == self.id:
            raise ValueError("Cannot send friend request to yourself")
            
        # Check if a request already exists in either direction
        existing_request = FriendRequest.query.filter(
            ((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == receiver.id)) |
            ((FriendRequest.sender_id == receiver.id) & (FriendRequest.receiver_id == self.id))
        ).first()
        
        if existing_request:
            if existing_request.status == FriendshipStatus.PENDING:
                raise ValueError("Friend request already pending")
            elif existing_request.status == FriendshipStatus.ACCEPTED:
                raise ValueError("Already friends")
            else:  # REJECTED - allow new request
                existing_request.status = FriendshipStatus.PENDING
                existing_request.sender_id = self.id
                existing_request.receiver_id = receiver.id
                db.session.commit()
                return existing_request
        
        friend_request = FriendRequest(sender_id=self.id, receiver_id=receiver.id)
        db.session.add(friend_request)
        db.session.commit()
        return friend_request

    def get_friend_requests(self):
        """Get all pending friend requests received by the user"""
        return self.received_requests.filter_by(status=FriendshipStatus.PENDING).all()

    def accept_friend_request(self, request_id):
        """Accept a friend request"""
        request = FriendRequest.query.get_or_404(request_id)
        if request.receiver_id != self.id:
            raise ValueError("Cannot accept this request")
        request.status = FriendshipStatus.ACCEPTED
        db.session.commit()
        return request

    def reject_friend_request(self, request_id):
        """Reject a friend request"""
        request = FriendRequest.query.get_or_404(request_id)
        if request.receiver_id != self.id:
            raise ValueError("Cannot reject this request")
        request.status = FriendshipStatus.REJECTED
        db.session.commit()
        return request

    def get_friends(self):
        """Get list of all friends"""
        accepted_sent = self.sent_requests.filter_by(
            status=FriendshipStatus.ACCEPTED
        ).all()
        accepted_received = self.received_requests.filter_by(
            status=FriendshipStatus.ACCEPTED
        ).all()
        
        friends = []
        for request in accepted_sent:
            friends.append(request.receiver)
        for request in accepted_received:
            friends.append(request.sender)
        return friends

    def is_friend_with(self, user):
        """Check if this user is friends with another user"""
        return user in self.get_friends()

    def __repr__(self):
        return f'<User {self.username}>'
    
    def add_preference(self, preference):
        if len(self.preferences) >= 5:
            return False
        if preference not in self.preferences:
            self.preferences.append(preference)
            return True
        return False

    def remove_preference(self, preference):
        if preference in self.preferences:
            self.preferences.remove(preference)
            return True
        return False