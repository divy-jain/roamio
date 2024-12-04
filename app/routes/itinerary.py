from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.itinerary import Itinerary, itinerary_activities
from app.models.activity import Activity
from app.models.user import User
import logging
from app.forms import CreateItineraryForm

logger = logging.getLogger(__name__)

bp = Blueprint('itinerary', __name__, url_prefix='/itinerary')

# Lists itineraries based on the user's visibility, showing public itineraries, the user's own, and friends' itineraries if logged in.
@bp.route('/')
def list_itineraries():
    """List itineraries based on user authentication and visibility settings."""
    try:
        if current_user.is_authenticated:
            # Fetch public, personal, and friends' itineraries for logged-in users.
            itineraries = Itinerary.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public itineraries.
                    Itinerary.user_id == current_user.id,  # User's own itineraries.
                    Itinerary.user_id.in_([friend.id for friend in current_user.get_friends()])  # Friends' itineraries.
                )
            ).all()
        else:
            # Fetch only public itineraries for unauthenticated users.
            itineraries = Itinerary.query.join(User).filter(
                User.profile_visibility == True
            ).all()
        
        # Render the itineraries in the template.
        return render_template('itinerary/list.html', itineraries=itineraries)
    
    except Exception as e:
        # Log the error and notify the user if something goes wrong.
        logger.error(f"Error fetching itineraries: {str(e)}")
        flash('An error occurred while loading itineraries.', 'error')
        return render_template('itinerary/list.html', itineraries=[])  # Return an empty list on error.

# Displays the details of a specific itinerary if the user has permission.
@bp.route('/<int:id>')
def view_itinerary(id):
    """View details of a specific itinerary if permitted."""
    try:
        # Fetch the itinerary or return a 404 error if not found.
        itinerary = Itinerary.query.get_or_404(id)
        
        # Check if the current user has permission to view the itinerary.
        if not itinerary.user.can_view_profile(current_user):
            flash('You do not have permission to view this itinerary.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
        
        # Fetch activities visible to the current user.
        if current_user.is_authenticated:
            all_activities = Activity.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public activities.
                    Activity.user_id == current_user.id,  # User's own activities.
                    Activity.user_id.in_([friend.id for friend in current_user.get_friends()])  # Friends' activities.
                )
            ).all()
        else:
            # For unauthenticated users, only public activities are visible.
            all_activities = Activity.query.join(User).filter(
                User.profile_visibility == True
            ).all()
        
        # Render the itinerary and associated activities in the template.
        return render_template('itinerary/view.html', 
                               itinerary=itinerary, 
                               all_activities=all_activities)
    except Exception as e:
        # Log the error and notify the user if an error occurs.
        logger.error(f"Error viewing itinerary {id}: {str(e)}")
        flash('An error occurred while loading the itinerary.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))

# Handles the creation of a new itinerary by authenticated users and saves it to the database.
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    """Allow authenticated users to create a new itinerary."""
    form = CreateItineraryForm()
    logger.debug(f"Form initialized: {form}")

    if form.validate_on_submit():
        logger.debug("Form validation successful")
        try:
            # Create and save a new itinerary
            itinerary = Itinerary(
                name=form.name.data,
                user_id=current_user.id
            )
            logger.debug(f"New itinerary created: {itinerary.name}")
            db.session.add(itinerary)
            db.session.commit()
            logger.debug("Itinerary saved to database")

            flash('Itinerary created successfully!', 'success')
            return redirect(url_for('itinerary.list_itineraries'))
        
        except Exception as e:
            # Log the error, rollback the transaction, and inform the user
            logger.error(f"Error creating itinerary: {str(e)}")
            db.session.rollback()
            flash('An error occurred while creating the itinerary.', 'error')
    else:
        logger.debug(f"Form validation failed with errors: {form.errors}")

    # Render the itinerary creation form
    return render_template('itinerary/create.html', form=form)

@bp.route('/add_activity', methods=['POST'])
@login_required
def add_activity_to_itinerary():
    """Add an activity to a specific itinerary if the user is the owner and the activity isn't already included."""
    try:
        # Get the activity and itinerary IDs from the form data
        activity_id = request.form.get('activity_id')
        itinerary_id = request.form.get('itinerary_id')
        
        # Check for missing activity or itinerary information
        if not activity_id or not itinerary_id:
            flash('Missing activity or itinerary information.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))

        # Retrieve the activity and itinerary from the database or raise a 404 error
        activity = Activity.query.get_or_404(activity_id)
        itinerary = Itinerary.query.get_or_404(itinerary_id)
        
        # Ensure the user can only add activities to their own itineraries
        if itinerary.user_id != current_user.id:
            flash('You can only add activities to your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))

        # Check if the activity is already part of the itinerary
        if activity in itinerary.activities:
            flash('This activity is already in the itinerary!', 'warning')
        else:
            # Add the activity to the itinerary and commit the changes to the database
            itinerary.activities.append(activity)
            db.session.commit()
            flash('Activity added to the itinerary!', 'success')

        # Redirect to the view page of the itinerary
        return redirect(url_for('itinerary.view_itinerary', id=itinerary.id))

    except Exception as e:
        # Log any errors and roll back the session in case of failure
        logger.error(f"Error adding activity to itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while adding the activity.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))

@bp.route('/<int:id>/remove_activity/<int:activity_id>', methods=['POST'])
@login_required
def remove_activity_from_itinerary(id, activity_id):
    """Remove an activity from a specific itinerary if the user is the owner and the activity is part of it."""
    try:
        # Retrieve the itinerary from the database or raise a 404 error
        itinerary = Itinerary.query.get_or_404(id)
        
        # Ensure the user can only remove activities from their own itineraries
        if itinerary.user_id != current_user.id:
            flash('You can only remove activities from your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
        
        # Retrieve the activity from the database or raise a 404 error
        activity = Activity.query.get_or_404(activity_id)

        # Check if the activity exists in the itinerary and remove it
        if activity in itinerary.activities:
            itinerary.activities.remove(activity)
            db.session.commit()
            flash('Activity removed from your itinerary!', 'success')
        else:
            flash('Activity not found in this itinerary.', 'warning')

        # Redirect to the view page of the itinerary
        return redirect(url_for('itinerary.view_itinerary', id=id))

    except Exception as e:
        # Log any errors and roll back the session in case of failure
        logger.error(f"Error removing activity from itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while removing the activity.', 'error')
        return redirect(url_for('itinerary.view_itinerary', id=id))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def remove_itinerary(id):
    """Delete a specific itinerary if the user is the owner."""
    try:
        # Retrieve the itinerary by ID or return a 404 if not found
        itinerary = Itinerary.query.get_or_404(id)
        
        # Ensure the current user is the owner of the itinerary before deletion
        if itinerary.user_id != current_user.id:
            flash('You can only delete your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
        
        # Proceed to delete the itinerary and commit the changes to the database
        db.session.delete(itinerary)
        db.session.commit()
        
        flash('Itinerary deleted successfully!', 'success')
        return redirect(url_for('itinerary.list_itineraries'))

    except Exception as e:
        # Log the error and roll back any changes in case of failure
        logger.error(f"Error deleting itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting the itinerary.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))
