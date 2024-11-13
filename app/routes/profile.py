from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.forms import EmptyForm
from app.models import Activity, Itinerary, Review
from app import db
from app.forms import EmptyForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/me')
@login_required
def my_profile():
    form = EmptyForm()  # Create form instance
    return render_template('profile/my_profile.html', user=current_user, form=form)

@profile_bp.route('/my_activities')
@login_required
def my_activities():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.name).all()
    return render_template('profile/my_activities.html', activities=activities)

@profile_bp.route('/my_itineraries')
@login_required
def my_itineraries():
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('profile/my_itineraries.html', itineraries=itineraries)

@profile_bp.route('/toggle_visibility', methods=['POST'])
@login_required
def toggle_visibility():
    form = EmptyForm()
    if form.validate_on_submit():
        try:
            current_user.profile_visibility = not current_user.profile_visibility
            db.session.commit()
            visibility_status = "public" if current_user.profile_visibility else "private"
            flash(f'Your profile is now {visibility_status}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile visibility.', 'error')
    return redirect(url_for('profile.my_profile'))

@profile_bp.route('/my_reviews')
@login_required
def my_reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile/my_reviews.html', reviews=reviews)