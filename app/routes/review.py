from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models.review import Review
from app.models.activity import Activity

bp = Blueprint('review', __name__)

@bp.route('/reviews')
def list_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('review/list.html', reviews=reviews)

@bp.route('/review/create/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def create_review(activity_id):
    activity = Activity.query.get_or_404(activity_id)
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
            if not (0 <= rating <= 5):
                raise ValueError("Rating must be between 0 and 5")
            
            review = Review(
                content=content,
                rating=rating,
                user_id=current_user.id,
                activity_id=activity_id
            )
            
            db.session.add(review)
            db.session.commit()
            
            # Try to update average rating but don't fail if it doesn't work
            try:
                update_activity_average_rating(activity_id)
            except Exception as e:
                print(f"Error updating average rating: {str(e)}")
                # Don't roll back or show error to user - the review was saved successfully
            
            flash('Your review has been added successfully!')
            return redirect(url_for('activity.activity_detail', id=activity_id))
            
        except ValueError as e:
            flash(f'Invalid rating value: {str(e)}')
            return redirect(url_for('review.create_review', activity_id=activity_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the review.')
            print(f"Error creating review: {str(e)}")
            return redirect(url_for('review.create_review', activity_id=activity_id))
    
    return render_template('review/create.html', activity=activity)

@bp.route('/review/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    review = Review.query.get_or_404(id)
    if review.user_id != current_user.id:
        flash('You do not have permission to edit this review.')
        return redirect(url_for('review.list_reviews'))
    
    if request.method == 'POST':
        try:
            review.content = request.form['content']
            rating = float(request.form['rating'])
            
            # Validate rating range
            if not (0 <= rating <= 5):
                raise ValueError("Rating must be between 0 and 5")
                
            review.rating = rating
            db.session.commit()
            
            # Update average rating
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
    review = Review.query.get_or_404(id)
    if review.user_id != current_user.id:
        flash('You do not have permission to delete this review.')
        return redirect(url_for('review.list_reviews'))
    
    activity_id = review.activity_id
    try:
        db.session.delete(review)
        db.session.commit()
        
        # Update activity's average rating
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
            # Use the existing 'rating' column instead of 'average_rating'
            activity.rating = int(round(result.average))  # Convert to integer since rating is INTEGER
            activity.review_count = result.count
        else:
            activity.rating = 0
            activity.review_count = 0
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating average rating: {str(e)}")
        # Don't raise the exception since the review was saved successfully
        # Just log it for debugging


# from flask import Blueprint, render_template, redirect, url_for, request, flash
# from flask_login import login_required, current_user
# from app import db
# from app.models.review import Review
# from app.models.activity import Activity

# bp = Blueprint('review', __name__)

# @bp.route('/reviews')
# @login_required
# def list_reviews():
#     reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.rating.desc()).all()
#     return render_template('review/list.html', reviews=reviews)

# @bp.route('/review/create/<int:activity_id>', methods=['GET', 'POST'])
# @login_required
# def create_review(activity_id):
#     activity = Activity.query.get_or_404(activity_id)
#     existing_review = Review.query.filter_by(user_id=current_user.id, activity_id=activity_id).first()
    
#     if existing_review:
#         flash('You have already reviewed this activity. You can edit your existing review.')
#         return redirect(url_for('review.edit_review', id=existing_review.id))
    
#     if request.method == 'POST':
#         content = request.form['content']
#         try:
#             rating = float(request.form['rating'])
#         except ValueError:
#             flash('Invalid rating value. Please enter a number.')
#             return redirect(url_for('review.create_review', activity_id=activity_id))
        
#         review = Review(content=content, rating=rating, user_id=current_user.id, activity_id=activity_id)
#         db.session.add(review)
#         db.session.commit()
        
#         # Update activity's average rating
#         update_activity_average_rating(activity_id)
        
#         flash('Your review has been added successfully!')
#         return redirect(url_for('activity.activity_detail', id=activity_id))
    
#     return render_template('review/create.html', activity=activity)

# @bp.route('/review/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_review(id):
#     review = Review.query.get_or_404(id)
#     if review.user_id != current_user.id:
#         flash('You do not have permission to edit this review.')
#         return redirect(url_for('review.list_reviews'))
    
#     if request.method == 'POST':
#         review.content = request.form['content']
#         try:
#             review.rating = float(request.form['rating'])
#         except ValueError:
#             flash('Invalid rating value. Please enter a number.')
#             return redirect(url_for('review.edit_review', id=id))
        
#         db.session.commit()
        
#         # Update activity's average rating
#         update_activity_average_rating(review.activity_id)
        
#         flash('Your review has been updated successfully!')
#         return redirect(url_for('activity.activity_detail', id=review.activity_id))
    
#     return render_template('review/edit.html', review=review)

# @bp.route('/review/delete/<int:id>', methods=['POST'])
# @login_required
# def delete_review(id):
#     review = Review.query.get_or_404(id)
#     if review.user_id != current_user.id:
#         flash('You do not have permission to delete this review.')
#         return redirect(url_for('review.list_reviews'))
    
#     activity_id = review.activity_id
#     db.session.delete(review)
#     db.session.commit()
    
#     # Update activity's average rating
#     update_activity_average_rating(activity_id)
    
#     flash('Your review has been deleted successfully!')
#     return redirect(url_for('activity.activity_detail', id=activity_id))

# def update_activity_average_rating(activity_id):
#     """Update the average rating of the activity."""
#     average_rating = db.session.query(db.func.avg(Review.rating)).filter_by(activity_id=activity_id).scalar()
#     activity = Activity.query.get(activity_id)
#     activity.average_rating = average_rating if average_rating is not None else 0  # Handle None case
#     db.session.commit()