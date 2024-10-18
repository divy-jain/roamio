from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.review import Review
from app.models.activity import Activity

bp = Blueprint('review', __name__)

@bp.route('/reviews')
@login_required
def list_reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.rating.desc()).all()
    return render_template('review/list.html', reviews=reviews)

@bp.route('/review/create/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def create_review(activity_id):
    activity = Activity.query.