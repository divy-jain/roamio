from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.itinerary import Itinerary

bp = Blueprint('itinerary', __name__)

@bp.route('/')
@login_required
def list_itineraries():
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('itinerary/list.html', itineraries=itineraries)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    # Implement create itinerary logic here
    pass

@bp.route('/<int:id>')
@login_required
def view_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('You do not have permission to view this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))
    return render_template('itinerary/view.html', itinerary=itinerary)

# Add more routes as needed