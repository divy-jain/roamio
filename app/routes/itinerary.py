from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.itinerary import Itinerary, itinerary_activities
from app.models.activity import Activity
from app.models.user import User

bp = Blueprint('itinerary', __name__)

@bp.route('/')
def list_itineraries():
    # Fetch all itineraries from the database
    itineraries = Itinerary.query.all()
    return render_template('itinerary/list.html', itineraries=itineraries)

@bp.route('/<int:id>')
def view_itinerary(id):
    # Fetch the specific itinerary from the database
    itinerary = Itinerary.query.get_or_404(id)
    all_activities = Activity.query.all()  # Get all available activities

    return render_template('itinerary/view.html', itinerary=itinerary, all_activities=all_activities)

@bp.route('/add_activity', methods=['POST'])
def add_activity_to_itinerary():
    activity_id = request.form['activity_id']
    activity = Activity.query.get_or_404(activity_id)

    # Get or create the public itinerary
    itinerary = Itinerary.query.filter_by(name="Public Itinerary").first()
    if not itinerary:
        default_user = User.query.first()
        if not default_user:
            default_user = User(username="default", email="default@example.com")
            default_user.set_password("default_password")
            db.session.add(default_user)
            db.session.commit()
        
        itinerary = Itinerary(name="Public Itinerary", user_id=default_user.id)
        db.session.add(itinerary)
        db.session.commit()

    # Check if the activity is already in the itinerary
    if activity in itinerary.activities:
        flash('This activity is already in the itinerary!', 'warning')
    else:
        itinerary.activities.append(activity)
        db.session.commit()
        flash('Activity added to the itinerary!', 'success')

    return redirect(url_for('activity.activity_detail', id=activity.id))  # Use 'activity.activity_detail'

@bp.route('/<int:id>/remove_activity/<int:activity_id>', methods=['POST'])
def remove_activity_from_itinerary(id, activity_id):
    itinerary = Itinerary.query.get_or_404(id)
    activity = Activity.query.get_or_404(activity_id)

    # Remove the activity from the itinerary
    if activity in itinerary.activities:
        itinerary.activities.remove(activity)
        db.session.commit()
        flash('Activity removed from your itinerary!', 'success')
    else:
        flash('Activity not found in this itinerary.', 'warning')

    return redirect(url_for('itinerary.view_itinerary', id=id))


@bp.route('/<int:id>/delete', methods=['POST'])
def remove_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    
    db.session.delete(itinerary)
    db.session.commit()
    
    flash('Itinerary deleted successfully!', 'success')
    return redirect(url_for('itinerary.list_itineraries'))

# If you want to implement user-specific itineraries in the future, you can uncomment and modify these routes

# @bp.route('/user_itineraries')
# @login_required
# def list_user_itineraries():
#     itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
#     return render_template('itinerary/user_list.html', itineraries=itineraries)

# @bp.route('/create_user_itinerary', methods=['GET', 'POST'])
# @login_required
# def create_user_itinerary():
#     if request.method == 'POST':
#         name = request.form['name']
#         itinerary = Itinerary(name=name, user_id=current_user.id)
#         db.session.add(itinerary)
#         db.session.commit()
#         flash('Your itinerary has been created!', 'success')
#         return redirect(url_for('itinerary.list_user_itineraries'))
#     return render_template('itinerary/create_user.html')

# @bp.route('/user_itinerary/<int:id>')
# @login_required
# def view_user_itinerary(id):
#     itinerary = Itinerary.query.get_or_404(id)
#     if itinerary.user_id != current_user.id:
#         flash('You do not have permission to view this itinerary.', 'danger')
#         return redirect(url_for('itinerary.list_user_itineraries'))
#     return render_template('itinerary/view_user.html', itinerary=itinerary)