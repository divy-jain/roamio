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
    activity = Activity.query.get_or_404(activity_id)
    existing_review = Review.query.filter_by(user_id=current_user.id, activity_id=activity_id).first()
    
    if existing_review:
        flash('You have already reviewed this activity. You can edit your existing review.')
        return redirect(url_for('review.edit_review', id=existing_review.id))
    
    if request.method == 'POST':
        content = request.form['content']
        rating = float(request.form['rating'])
        
        review = Review(content=content, rating=rating, user_id=current_user.id, activity_id=activity_id)
        db.session.add(review)
        db.session.commit()
        
        # Update activity's average rating
        activity.average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(activity_id=activity_id).scalar()
        db.session.commit()
        
        flash('Your review has been added successfully!')
        return redirect(url_for('activity.activity_detail', id=activity_id))
    
    return render_template('review/create.html', activity=activity)

@bp.route('/review/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    review = Review.query.get_or_404(id)
    if review.user_id != current_user.id:
        flash('You do not have permission to edit this review.')
        return redirect(url_for('review.list_reviews'))
    
    if request.method == 'POST':
        review.content = request.form['content']
        review.rating = float(request.form['rating'])
        db.session.commit()
        
        # Update activity's average rating
        activity = Activity.query.get(review.activity_id)
        activity.average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(activity_id=review.activity_id).scalar()
        db.session.commit()
        
        flash('Your review has been updated successfully!')
        return redirect(url_for('activity.activity_detail', id=review.activity_id))
    
    return render_template('review/edit.html', review=review)

@bp.route('/review/delete/<int:id>', methods=['POST'])
@login_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    if review.user_id != current_user.id:
        flash('You do not have permission to delete this review.')
        return redirect(url_for('review.list_reviews'))
    
    activity_id = review.activity_id
    db.session.delete(review)
    db.session.commit()
    
    # Update activity's average rating
    activity = Activity.query.get(activity_id)
    activity.average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(activity_id=activity_id).scalar()
    db.session.commit()
    
    flash('Your review has been deleted successfully!')
    return redirect(url_for('activity.activity_detail', id=activity_id))