from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, FriendRequest, FriendshipStatus
from app import db

bp = Blueprint('friends', __name__, url_prefix='/friends')

# Route to display the list of friends and pending friend requests.
@bp.route('/')
@login_required
def friend_list():
    """Show list of friends and pending requests."""
    friends = current_user.get_friends()  # Fetch user's friends.
    pending_requests = current_user.get_friend_requests()  # Fetch pending friend requests.
    return render_template('friends/list.html', friends=friends, pending_requests=pending_requests)

# Route to search for users to add as friends.
@bp.route('/search')
@login_required
def search():
    """Search for users to add as friends."""
    query = request.args.get('query', '').strip()  # Retrieve and clean search query.
    if query:
        # Search for users with matching usernames, excluding the current user.
        users = User.query.filter(
            User.username.ilike(f'%{query}%'),
            User.id != current_user.id
        ).all()
    else:
        users = []  # Return an empty list if no query is provided.
    return render_template('friends/search.html', users=users, query=query)

# Route to send a friend request to a user.
@bp.route('/send_request/<int:user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    """Send a friend request."""
    user = User.query.get_or_404(user_id)  # Fetch the user or return 404.
    try:
        current_user.send_friend_request(user)  # Send the friend request.
        flash('Friend request sent successfully!', 'success')
    except ValueError as e:  # Handle any errors during the request.
        flash(str(e), 'error')
    return redirect(url_for('friends.search'))

# Route to accept a pending friend request.
@bp.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """Accept a friend request."""
    try:
        current_user.accept_friend_request(request_id)  # Accept the friend request.
        flash('Friend request accepted!', 'success')
    except ValueError as e:  # Handle any errors during acceptance.
        flash(str(e), 'error')
    return redirect(url_for('friends.friend_list'))

# Route to reject a pending friend request.
@bp.route('/reject_request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    """Reject a friend request."""
    try:
        current_user.reject_friend_request(request_id)  # Reject the friend request.
        flash('Friend request rejected!', 'success')
    except ValueError as e:  # Handle any errors during rejection.
        flash(str(e), 'error')
    return redirect(url_for('friends.friend_list'))

# Route to remove a friend from the user's friend list.
@bp.route('/remove/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    """Remove a friend."""
    friend = User.query.get_or_404(friend_id)  # Fetch the friend or return 404 if not found.
    
    # Find the accepted friend request representing the friendship in either direction.
    request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) & 
         (FriendRequest.receiver_id == friend_id)) |  # Check if the current user sent the request.
        ((FriendRequest.sender_id == friend_id) & 
         (FriendRequest.receiver_id == current_user.id)),  # Or if the current user received it.
        FriendRequest.status == FriendshipStatus.ACCEPTED  # Ensure the request was accepted.
    ).first()
    
    if request:
        db.session.delete(request)  # Delete the friendship from the database.
        db.session.commit()  # Commit the changes to make it permanent.
        flash('Friend removed successfully!', 'success')  # Notify the user of success.
    else:
        flash('Friend relationship not found!', 'error')  # Handle case where no friendship exists.
    
    return redirect(url_for('friends.friend_list'))  # Redirect back to the friend list.
