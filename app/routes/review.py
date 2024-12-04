from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from app import db
from app.models.review import Review
from app.models.activity import Activity
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('review', __name__)

@bp.route('/reviews')
def list_reviews():
    """List reviews visible to the current user based on their authentication and permissions."""
    try:
        if current_user.is_authenticated:
            # Show public reviews, own reviews, and friends' reviews
            reviews = Review.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public users' reviews
                    Review.user_id == current_user.id,  # User's own reviews
                    Review.user_id.in_([friend.id for friend in current_user.get_friends()])  # Friends' reviews
                )
            ).order_by(Review.created_at.desc()).all()
        else:
            # Show only public reviews
            reviews = Review.query.join(User).filter(
                User.profile_visibility == True
            ).order_by(Review.created_at.desc()).all()
            
        return render_template('review/list.html', reviews=reviews)
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        flash('An error occurred while loading reviews.', 'error')
        return render_template('review/list.html', reviews=[])


@bp.route('/review/create/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def create_review(activity_id):
    """Create a new review for a given activity, ensuring user authorization and input validation."""
    activity = Activity.query.get_or_404(activity_id)
    
    # Check if user can view this activity before reviewing
    if not activity.user.can_view_profile(current_user):
        flash('You do not have permission to review this activity.', 'error')
        return redirect(url_for('activity.list_activities'))
    
    # Check if the user has already reviewed this activity
    existing_review = Review.query.filter_by(
        user_id=current_user.id, 
        activity_id=activity_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this activity. You can edit your existing review.')
        return redirect(url_for('review.edit_review', id=existing_review.id))
    
    if request.method == 'POST':
        try:
            content = request.form['content']
            rating = float(request.form['rating'])
            
            # Validate rating range
            if not (0 <= rating <= 10):
                raise ValueError("Rating must be between 0 and 10")
            
            review = Review(
                content=content,
                rating=rating,
                user_id=current_user.id,
                activity_id=activity_id
            )
            
            db.session.add(review)
            db.session.commit()
            
            # Update average rating of the activity
            update_activity_average_rating(activity_id)
            
            flash('Your review has been added successfully!')
            return redirect(url_for('activity.activity_detail', id=activity_id))
            
        except ValueError as e:
            flash(f'Invalid rating value: {str(e)}')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the review.')
            logger.error(f"Error creating review: {str(e)}")
            
    return render_template('review/create.html', activity=activity)


@bp.route('/review/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    """Edit an existing review, ensuring user authorization and input validation."""
    review = Review.query.get_or_404(id)
    
    # Check if the user has permission to edit this review
    if review.user_id != current_user.id:
        flash('You do not have permission to edit this review.')
        return redirect(url_for('review.list_reviews'))
    
    if request.method == 'POST':
        try:
            review.content = request.form['content']
            rating = float(request.form['rating'])
            
            # Validate rating range
            if not (0 <= rating <= 10):
                raise ValueError("Rating must be between 0 and 10")
                
            review.rating = rating
            db.session.commit()
            
            # Update average rating for the activity associated with the review
            update_activity_average_rating(review.activity_id)
            
            flash('Your review has been updated successfully!')
            return redirect(url_for('activity.activity_detail', id=review.activity_id))
            
        except ValueError as e:
            flash(f'Invalid rating value: {str(e)}')
            return redirect(url_for('review.edit_review', id=id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the review.')
            print(f"Error updating review: {str(e)}")
            return redirect(url_for('review.edit_review', id=id))
    
    return render_template('review/edit.html', review=review)

@bp.route('/review/delete/<int:id>', methods=['POST'])
@login_required
def delete_review(id):
    """Delete a review, ensuring user authorization and updating the activity's average rating."""
    review = Review.query.get_or_404(id)
    
    # Check if the user has permission to delete this review
    if review.user_id != current_user.id:
        flash('You do not have permission to delete this review.')
        return redirect(url_for('review.list_reviews'))
    
    activity_id = review.activity_id
    try:
        db.session.delete(review)
        db.session.commit()
        
        # Update average rating for the activity after review deletion
        update_activity_average_rating(activity_id)
        
        flash('Your review has been deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the review.')
        print(f"Error deleting review: {str(e)}")
    
    return redirect(url_for('activity.activity_detail', id=activity_id))


def update_activity_average_rating(activity_id):
    """Update the average rating of the activity efficiently."""
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return

        result = db.session.query(
            func.count(Review.id).label('count'),
            func.avg(Review.rating).label('average')
        ).filter(Review.activity_id == activity_id).first()
        
        if result.count > 0:
            activity.rating = int(round(result.average))
            activity.review_count = result.count
        else:
            activity.rating = 0
            activity.review_count = 0
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating average rating: {str(e)}")