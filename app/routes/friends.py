from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, FriendRequest, FriendshipStatus
from app import db

bp = Blueprint('friends', __name__, url_prefix='/friends')

@bp.route('/')
@login_required
def friend_list():
    """Show list of friends and pending requests"""
    friends = current_user.get_friends()
    pending_requests = current_user.get_friend_requests()
    return render_template('friends/list.html', 
                         friends=friends, 
                         pending_requests=pending_requests)

@bp.route('/search')
@login_required
def search():
    """Search for users to add as friends"""
    query = request.args.get('query', '').strip()
    if query:
        users = User.query.filter(
            User.username.ilike(f'%{query}%'),
            User.id != current_user.id
        ).all()
    else:
        users = []
    return render_template('friends/search.html', users=users, query=query)

@bp.route('/send_request/<int:user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    """Send a friend request"""
    user = User.query.get_or_404(user_id)
    try:
        current_user.send_friend_request(user)
        flash('Friend request sent successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('friends.search'))

@bp.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """Accept a friend request"""
    try:
        current_user.accept_friend_request(request_id)
        flash('Friend request accepted!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('friends.friend_list'))

@bp.route('/reject_request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    """Reject a friend request"""
    try:
        current_user.reject_friend_request(request_id)
        flash('Friend request rejected!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('friends.friend_list'))

@bp.route('/remove/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    """Remove a friend"""
    friend = User.query.get_or_404(friend_id)
    # Find the accepted friend request in either direction
    request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) & 
         (FriendRequest.receiver_id == friend_id)) |
        ((FriendRequest.sender_id == friend_id) & 
         (FriendRequest.receiver_id == current_user.id)),
        FriendRequest.status == FriendshipStatus.ACCEPTED
    ).first()
    
    if request:
        db.session.delete(request)
        db.session.commit()
        flash('Friend removed successfully!', 'success')
    else:
        flash('Friend relationship not found!', 'error')
    return redirect(url_for('friends.friend_list'))