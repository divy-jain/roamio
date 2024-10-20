from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.itinerary import Itinerary
from app.models.activity import Activity  # Ensure you import Activity

bp = Blueprint('itinerary', __name__)

@bp.route('/')
@login_required
def list_itineraries():
    # Fetch itineraries for the current user
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('itinerary/list.html', itineraries=itineraries)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        
        # Create a new itinerary instance
        itinerary = Itinerary(name=name, user_id=current_user.id)
        db.session.add(itinerary)
        db.session.commit()
        flash('Itinerary created successfully!', 'success')
        return redirect(url_for('itinerary.list_itineraries'))
    
    return render_template('itinerary/create.html')

@bp.route('/<int:id>')
@login_required
def view_itinerary(id):
    # Fetch the specific itinerary
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        flash('You do not have permission to view this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))

    return render_template('itinerary/view.html', itinerary=itinerary)

@bp.route('/<int:id>/add_activity', methods=['POST'])
@login_required
def add_activity_to_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        flash('You do not have permission to modify this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))

    activity_id = request.form.get('activity_id')
    activity = Activity.query.get_or_404(activity_id)

    # Add the activity to the itinerary
    itinerary.activities.append(activity)
    db.session.commit()
    flash('Activity added to your itinerary!', 'success')

    return redirect(url_for('itinerary.view_itinerary', id=id))

@bp.route('/<int:id>/remove_activity/<int:activity_id>', methods=['POST'])
@login_required
def remove_activity_from_itinerary(id, activity_id):
    itinerary = Itinerary.query.get_or_404(id)

    if itinerary.user_id != current_user.id:
        flash('You do not have permission to modify this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))

    activity = Activity.query.get_or_404(activity_id)

    # Remove the activity from the itinerary
    itinerary.activities.remove(activity)
    db.session.commit()
    flash('Activity removed from your itinerary!', 'success')

    return redirect(url_for('itinerary.view_itinerary', id=id))
