from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.chat import Message
from app.models.user import User

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
@login_required
def chat_list():
    # Get all unique users the current user has chatted with
    users = db.session.query(User).join(
        Message,
        ((Message.sender_id == User.id) & (Message.recipient_id == current_user.id)) |
        ((Message.recipient_id == User.id) & (Message.sender_id == current_user.id))
    ).distinct().all()
    
    return render_template('chat/list.html', users=users)

@bp.route('/<int:user_id>')
@login_required
def chat_detail(user_id):
    other_user = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.recipient_id == current_user.id) & (Message.sender_id == user_id))
    ).order_by(Message.created_at).all()
    
    return render_template('chat/detail.html', other_user=other_user, messages=messages)

@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    if not recipient_id or not content:
        return jsonify({'error': 'Missing required fields'}), 400
        
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/unread-count')
@login_required
def unread_count():
    count = Message.query.filter_by(
        recipient_id=current_user.id,
        read=False
    ).count()
    return jsonify({'count': count})