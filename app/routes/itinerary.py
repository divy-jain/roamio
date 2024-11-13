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

@bp.route('/')
def list_itineraries():
    try:
        if current_user.is_authenticated:
            # Show public itineraries, own itineraries, and friends' itineraries
            itineraries = Itinerary.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public users' itineraries
                    Itinerary.user_id == current_user.id,  # User's own itineraries
                    Itinerary.user_id.in_([friend.id for friend in current_user.get_friends()])  # Friends' itineraries
                )
            ).all()
        else:
            # Show only public itineraries
            itineraries = Itinerary.query.join(User).filter(User.profile_visibility == True).all()
            
        return render_template('itinerary/list.html', itineraries=itineraries)
    except Exception as e:
        logger.error(f"Error fetching itineraries: {str(e)}")
        flash('An error occurred while loading itineraries.', 'error')
        return render_template('itinerary/list.html', itineraries=[])

@bp.route('/<int:id>')
def view_itinerary(id):
    try:
        itinerary = Itinerary.query.get_or_404(id)
        
        # Check if user can view this itinerary
        if not itinerary.user.can_view_profile(current_user):
            flash('You do not have permission to view this itinerary.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
            
        # Get all activities that the user can see
        if current_user.is_authenticated:
            all_activities = Activity.query.join(User).filter(
                or_(
                    User.profile_visibility == True,
                    Activity.user_id == current_user.id,
                    Activity.user_id.in_([friend.id for friend in current_user.get_friends()])
                )
            ).all()
        else:
            all_activities = Activity.query.join(User).filter(User.profile_visibility == True).all()
            
        return render_template('itinerary/view.html', 
                             itinerary=itinerary, 
                             all_activities=all_activities)
    except Exception as e:
        logger.error(f"Error viewing itinerary {id}: {str(e)}")
        flash('An error occurred while loading the itinerary.', 'error')
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

@bp.route('/add_activity', methods=['POST'])
@login_required
def add_activity_to_itinerary():
    try:
        activity_id = request.form.get('activity_id')
        itinerary_id = request.form.get('itinerary_id')
        
        if not activity_id or not itinerary_id:
            flash('Missing activity or itinerary information.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))

        activity = Activity.query.get_or_404(activity_id)
        itinerary = Itinerary.query.get_or_404(itinerary_id)
        
        # Check if the user owns this itinerary
        if itinerary.user_id != current_user.id:
            flash('You can only add activities to your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))

        # Check if the activity is already in the itinerary
        if activity in itinerary.activities:
            flash('This activity is already in the itinerary!', 'warning')
        else:
            itinerary.activities.append(activity)
            db.session.commit()
            flash('Activity added to the itinerary!', 'success')

        return redirect(url_for('itinerary.view_itinerary', id=itinerary.id))

    except Exception as e:
        logger.error(f"Error adding activity to itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while adding the activity.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))

@bp.route('/<int:id>/remove_activity/<int:activity_id>', methods=['POST'])
@login_required
def remove_activity_from_itinerary(id, activity_id):
    try:
        itinerary = Itinerary.query.get_or_404(id)
        
        if itinerary.user_id != current_user.id:
            flash('You can only remove activities from your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
            
        activity = Activity.query.get_or_404(activity_id)

        if activity in itinerary.activities:
            itinerary.activities.remove(activity)
            db.session.commit()
            flash('Activity removed from your itinerary!', 'success')
        else:
            flash('Activity not found in this itinerary.', 'warning')

        return redirect(url_for('itinerary.view_itinerary', id=id))

    except Exception as e:
        logger.error(f"Error removing activity from itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while removing the activity.', 'error')
        return redirect(url_for('itinerary.view_itinerary', id=id))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def remove_itinerary(id):
    try:
        itinerary = Itinerary.query.get_or_404(id)
        
        if itinerary.user_id != current_user.id:
            flash('You can only delete your own itineraries.', 'error')
            return redirect(url_for('itinerary.list_itineraries'))
            
        db.session.delete(itinerary)
        db.session.commit()
        
        flash('Itinerary deleted successfully!', 'success')
        return redirect(url_for('itinerary.list_itineraries'))

    except Exception as e:
        logger.error(f"Error deleting itinerary: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting the itinerary.', 'error')
        return redirect(url_for('itinerary.list_itineraries'))