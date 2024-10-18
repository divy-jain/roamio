from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.itinerary import Itinerary
from app.models.activity import Activity

bp = Blueprint('itinerary', __name__)

@bp.route('/itineraries')
@login_required
def list_itineraries():
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('itinerary/list.html', itineraries=itineraries)

@bp.route('/itinerary/<int:id>')
@login_required
def itinerary_detail(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('You do not have permission to view this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))
    return render_template('itinerary/detail.html', itinerary=itinerary)

@bp.route('/itinerary/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    if request.method == 'POST':
        itinerary = Itinerary(name=request.form['name'], user_id=current_user.id)
        db.session.add(itinerary)
        db.session.commit()
        flash('Itinerary created successfully!')
        return redirect(url_for('itinerary.list_itineraries'))
    return render_template('itinerary/create.html')

@bp.route('/itinerary/<int:id>/add_activity/<int:activity_id>', methods=['POST'])
@login_required
def add_activity_to_itinerary(id, activity_id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('You do not have permission to modify this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))
    activity = Activity.query.get_or_404(activity_id)
    itinerary.activities.append(activity)
    db.session.commit()
    flash('Activity added to itinerary successfully!')
    return redirect(url_for('itinerary.itinerary_detail', id=id))