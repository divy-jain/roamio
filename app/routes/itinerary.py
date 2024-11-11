from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.itinerary import Itinerary, itinerary_activities
from app.models.activity import Activity
from app.models.user import User
import logging
from app.forms import CreateItineraryForm  


# Create a logger for this module
logger = logging.getLogger(__name__)

# Change the blueprint name to avoid conflicts
bp = Blueprint('itinerary', __name__, url_prefix='/itinerary')

@bp.route('/')
def list_itineraries():
    try:
        # Fetch all itineraries from the database
        itineraries = Itinerary.query.all()
        return render_template('itinerary/list.html', itineraries=itineraries)
    except Exception as e:
        logger.error(f"Error fetching itineraries: {str(e)}")
        flash('An error occurred while loading itineraries.', 'error')
        return render_template('itinerary/list.html', itineraries=[])

@bp.route('/<int:id>')
def view_itinerary(id):
    try:
        # Fetch the specific itinerary from the database
        itinerary = Itinerary.query.get_or_404(id)
        all_activities = Activity.query.all()  # Get all available activities
        return render_template('itinerary/view.html', 
                             itinerary=itinerary, 
                             all_activities=all_activities)
    except Exception as e:
        logger.error(f"Error viewing itinerary {id}: {str(e)}")
        flash('An error occurred while loading the itinerary.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))

@bp.route('/add_activity', methods=['POST'])
def add_activity_to_itinerary():
    try:
        activity_id = request.form.get('activity_id')
        if not activity_id:
            flash('No activity selected.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))

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
            
            itinerary = Itinerary(name="Public Itinerary")
            if hasattr(itinerary, 'user_id'):  # Check if user_id field exists
                itinerary.user_id = default_user.id
            db.session.add(itinerary)
            db.session.commit()

        # Check if the activity is already in the itinerary
        if activity in itinerary.activities:
            flash('This activity is already in the itinerary!', 'warning')
        else:
            itinerary.activities.append(activity)
            db.session.commit()
            flash('Activity added to the itinerary!', 'success')

        return redirect(url_for('activity.activity_detail', id=activity.id))

    except Exception as e:
        logger.error(f"Error adding activity to itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while adding the activity.', 'error')
        return redirect(url_for('activity.list_activities'))

@bp.route('/<int:id>/remove_activity/<int:activity_id>', methods=['POST'])
def remove_activity_from_itinerary(id, activity_id):
    try:
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

    except Exception as e:
        logger.error(f"Error removing activity {activity_id} from itinerary {id}: {str(e)}")
        db.session.rollback()
        flash('An error occurred while removing the activity.', 'error')
        return redirect(url_for('itinerary.view_itinerary', id=id))

@bp.route('/<int:id>/delete', methods=['POST'])
def remove_itinerary(id):
    try:
        itinerary = Itinerary.query.get_or_404(id)
        
        db.session.delete(itinerary)
        db.session.commit()
        
        flash('Itinerary deleted successfully!', 'success')
        return redirect(url_for('itinerary.list_itineraries'))

    except Exception as e:
        logger.error(f"Error deleting itinerary {id}: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting the itinerary.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    form = CreateItineraryForm()
    logger.debug(f"Form created: {form}")
    
    if form.validate_on_submit():
        logger.debug("Form validated successfully")
        try:
            itinerary = Itinerary(
                name=form.name.data,
                user_id=current_user.id
            )
            logger.debug(f"Created itinerary object: {itinerary.name}")
            db.session.add(itinerary)
            db.session.commit()
            logger.debug("Itinerary saved to database")
            
            flash('Itinerary created successfully!', 'success')
            return redirect(url_for('itinerary.list_itineraries'))
        
        except Exception as e:
            logger.error(f"Error creating itinerary: {str(e)}")
            db.session.rollback()
            flash('An error occurred while creating the itinerary.', 'error')
    else:
        logger.debug(f"Form validation failed. Errors: {form.errors}")
    
    return render_template('itinerary/create.html', form=form)

# # For future implementation of user-specific itineraries
# @bp.route('/create', methods=['GET', 'POST'])
# def create_itinerary():
#     if request.method == 'POST':
#         try:
#             name = request.form.get('name')
#             if not name:
#                 flash('Please provide an itinerary name.', 'error')
#                 return render_template('itinerary/create.html')

#             itinerary = Itinerary(name=name, user_id=current_user.id)  # Associate with user
#             # itinerary = Itinerary(name=name)
#             # if hasattr(itinerary, 'user_id') and hasattr(current_user, 'id'):
#             #     itinerary.user_id = current_user.id
            

#             db.session.add(itinerary)
#             db.session.commit()
            
#             flash('Itinerary created successfully!', 'success')
#             return redirect(url_for('itinerary.list_itineraries'))

#         except Exception as e:
#             logger.error(f"Error creating itinerary: {str(e)}")
#             db.session.rollback()
#             flash('An error occurred while creating the itinerary.', 'error')
#             return render_template('itinerary/create.html')

#     return render_template('itinerary/create.html')