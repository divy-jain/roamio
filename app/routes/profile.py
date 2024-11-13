from flask import Blueprint, render_template
from flask_login import login_required, current_user
# from app import db  # Ensure db is correctly imported
# from app.models import Activity  # Assuming Activity is defined in models

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/me')
@login_required
def my_profile():
    return render_template('profile/my_profile.html', user=current_user)

# @profile_bp.route('/my_activities')
# @login_required
# def my_activities():
#     # Query activities for the current user
#     activities = Activity.query.filter_by(user_id=current_user.id).all()
#     return render_template('profile/my_activities.html', activities=activities)
