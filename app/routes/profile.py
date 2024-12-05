from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.forms import EmptyForm
from app.models import Activity, Itinerary, Review, Preference
from app import db
from app.forms import EmptyForm
from app.models.user import User

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/me')
@login_required
def my_profile():
    """Render the current user's profile page."""
    form = EmptyForm()  # Create form instance
    return render_template('profile/my_profile.html', user=current_user, form=form)

@profile_bp.route('/my_activities')
@login_required
def my_activities():
    """Display a list of activities created by the current user."""
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.name).all()
    return render_template('profile/my_activities.html', activities=activities)

@profile_bp.route('/my_itineraries')
@login_required
def my_itineraries():
    """Display a list of itineraries created by the current user."""
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('profile/my_itineraries.html', itineraries=itineraries)


@profile_bp.route('/toggle_visibility', methods=['POST'])
@login_required
def toggle_visibility():
    """Toggle the visibility status of the current user's profile."""
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
    """Display a list of reviews written by the current user, ordered by creation date."""
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile/my_reviews.html', reviews=reviews)

@profile_bp.route('/user/<username>')
@login_required
def view_profile(username):
    """View the profile of a specified user, with permission checks for visibility."""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if the viewer has permission to view this profile
    if not user.can_view_profile(current_user):
        flash('You do not have permission to view this profile.', 'error')
        return redirect(url_for('profile.my_profile'))
        
    # Get the user's activities, itineraries, and reviews
    activities = Activity.query.filter_by(user_id=user.id).all()
    itineraries = Itinerary.query.filter_by(user_id=user.id).all()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    
    return render_template('profile/view_profile.html',
                         user=user,
                         activities=activities,
                         itineraries=itineraries,
                         reviews=reviews)

@profile_bp.route('/manage_preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update the preferences of the current user."""
    form = EmptyForm()
    if form.validate_on_submit():
        try:
            # Get selected preference IDs from form
            selected_ids = request.form.getlist('preferences')
            print(f"Selected IDs: {selected_ids}")  # Debugging line
            
            # Validate number of selections
            if len(selected_ids) > 5:
                flash('You can only select up to 5 preferences.', 'error')
            else:
                # Clear existing preferences
                current_user.preferences = []

                # Add new preferences
                selected_preferences = Preference.query.filter(
                    Preference.id.in_(selected_ids)
                ).all()
                current_user.preferences.extend(selected_preferences)

                db.session.commit()

                # Dynamic flash message
                if selected_preferences:
                    preference_names = ', '.join([pref.name for pref in selected_preferences])
                    flash(f'Preferences updated successfully! Selected: {preference_names}', 'success')
                else:
                    flash('All preferences cleared.', 'info')

                return redirect(url_for('profile.my_profile'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('An error occurred while updating preferences.', 'error')

    flash('Failed to validate the form. Please try again.', 'error')
    return redirect(url_for('profile.manage_preferences'))

@profile_bp.route('/preferences', methods=['GET'])
@login_required
def manage_preferences():
    """Display the preferences management page."""
    form = EmptyForm()
    all_preferences = Preference.query.all()
    return render_template(
        'profile/preferences.html',
        form=form,
        preferences=all_preferences,
        user_preferences=current_user.preferences,
    )