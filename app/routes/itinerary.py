from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.itinerary import Itinerary

bp = Blueprint('itinerary', __name__)

@bp.route('/')
@login_required
def list_itineraries():
    # Fetch itineraries for the current user using raw SQL
    itineraries = db.session.execute(
        'SELECT * FROM itinerary WHERE user_id = :user_id',
        {'user_id': current_user.id}
    ).fetchall()
    
    # Convert the result to a list of Itinerary objects
    itinerary_list = [Itinerary(**dict(itinerary)) for itinerary in itineraries]
    return render_template('itinerary/list.html', itineraries=itinerary_list)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    if request.method == 'POST':
        # Get data from the form
        title = request.form['title']
        description = request.form['description']
        
        # Insert the new itinerary into the database
        db.session.execute(
            'INSERT INTO itinerary (title, description, user_id) VALUES (:title, :description, :user_id)',
            {
                'title': title,
                'description': description,
                'user_id': current_user.id
            }
        )
        db.session.commit()
        flash('Itinerary created successfully!', 'success')
        return redirect(url_for('itinerary.list_itineraries'))
    
    return render_template('itinerary/create.html')

@bp.route('/<int:id>')
@login_required
def view_itinerary(id):
    # Fetch the specific itinerary using raw SQL
    itinerary = db.session.execute(
        'SELECT * FROM itinerary WHERE id = :id AND user_id = :user_id',
        {'id': id, 'user_id': current_user.id}
    ).fetchone()

    if itinerary is None:
        flash('You do not have permission to view this itinerary.')
        return redirect(url_for('itinerary.list_itineraries'))

    return render_template('itinerary/view.html', itinerary=Itinerary(**dict(itinerary)))

# Add more routes as needed
