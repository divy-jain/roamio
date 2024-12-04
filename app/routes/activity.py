from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from app import db
from app.models.activity import Activity
from app.models.itinerary import Itinerary
from app.models.user import User
from app.forms import ActivityForm
from sqlalchemy import text, or_
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('activity', __name__, url_prefix='/activity')

# Route for listing all activities.
@bp.route('/')
def list_activities():
    try:
        query = request.args.get('query', '')
        city = request.args.get('city', '')
        activity_type = request.args.get('activity_type', '')
        sort = request.args.get('sort', 'name')

        # Base query with privacy filter
        if current_user.is_authenticated:
            # Show public activities, own activities, and friends' activities
            activities_query = Activity.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public users' activities
                    Activity.user_id == current_user.id,  # User's own activities
                    Activity.user_id.in_([friend.id for friend in current_user.get_friends()])  # Friends' activities
                )
            )
        else:
            # Show only public activities
            activities_query = Activity.query.join(User).filter(User.profile_visibility == True)

        # Apply filters
        if query:
            activities_query = activities_query.filter(Activity.name.ilike(f'%{query}%'))
        if city:
            activities_query = activities_query.filter(Activity.city.ilike(f'%{city}%'))
        if activity_type:
            activities_query = activities_query.filter(Activity.activity_type == activity_type)

        # Apply sorting
        if sort == 'rating':
            activities_query = activities_query.order_by(Activity.rating.desc())
        else:
            activities_query = activities_query.order_by(Activity.name)

        activities = activities_query.all()

        # Get distinct cities and activity types from visible activities
        if current_user.is_authenticated:
            cities = db.session.query(Activity.city.distinct())\
                .join(User)\
                .filter(
                    or_(
                        User.profile_visibility == True,
                        Activity.user_id == current_user.id,
                        Activity.user_id.in_([friend.id for friend in current_user.get_friends()])
                    )
                ).all()
                
            activity_types = db.session.query(Activity.activity_type.distinct())\
                .join(User)\
                .filter(
                    or_(
                        User.profile_visibility == True,
                        Activity.user_id == current_user.id,
                        Activity.user_id.in_([friend.id for friend in current_user.get_friends()])
                    )
                ).all()
        else:
            cities = db.session.query(Activity.city.distinct())\
                .join(User)\
                .filter(User.profile_visibility == True).all()
            activity_types = db.session.query(Activity.activity_type.distinct())\
                .join(User)\
                .filter(User.profile_visibility == True).all()

        return render_template('activity/list.html', 
                             activities=activities,
                             cities=[city[0] for city in cities],
                             activity_types=[type[0] for type in activity_types])
                             
    except Exception as e:
        logger.error(f"Error listing activities: {str(e)}")
        flash('An error occurred while loading activities.', 'error')
        return render_template('activity/list.html', activities=[])

# Route for creating a new activity, accessible via GET and POST methods.
@bp.route('/new', methods=['GET', 'POST'])
@login_required  # User must be logged in to access.
def new_activity():
    form = ActivityForm()  # Form for user input.

    if form.validate_on_submit():  # Handle form submission.
        try:
            # Create and save a new activity based on form data.
            activity = Activity(
                name=form.name.data,
                description=form.description.data,
                city=form.city.data,
                activity_type=form.activity_type.data,
                cost=form.cost.data,
                season=form.season.data,
                rating=float(form.rating.data),
                user_id=current_user.id
            )
            db.session.add(activity)
            db.session.commit()  # Commit changes to the database.
            flash('Activity created successfully!', 'success')  # Notify user.
            return redirect(url_for('activity.list_activities'))
        except Exception as e:
            logger.error(f"Error creating activity: {str(e)}")  # Log any errors.
            flash('An error occurred while creating the activity.', 'error')

    # Render the form for GET requests or if submission fails.
    return render_template('activity/new.html', form=form)

# Route for viewing the activity details for each activity.
@bp.route('/<int:id>')
def activity_detail(id):
    try:
        print("Starting activity_detail route")  # Basic print for debugging
        logger.info("Starting activity_detail route")  # Logger version
        
        activity = Activity.query.get_or_404(id)
        
        # Check if user can view this activity
        if not activity.user.can_view_profile(current_user):
            flash('You do not have permission to view this activity.', 'error')
            return redirect(url_for('activity.list_activities'))
        
        # Add explicit debug prints
        print(f"Current user authenticated: {current_user.is_authenticated}")
        print(f"Current user id: {current_user.id}")
        
        # Get itineraries with debug prints
        if current_user.is_authenticated:
            print(f"Querying itineraries for user_id: {current_user.id}")
            itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
            print(f"Found {len(itineraries)} itineraries")
            
            # Print each itinerary
            for itin in itineraries:
                print(f"Itinerary found - ID: {itin.id}, Name: {itin.name}, User ID: {itin.user_id}")
        else:
            itineraries = []
            print("No user authenticated, setting empty itineraries list")
                
        return render_template('activity/detail.html', 
                             activity=activity, 
                             itineraries=itineraries)
                             
    except Exception as e:
        print(f"Error in activity_detail: {str(e)}")  # Print the error
        logger.error(f"Error viewing activity {id}: {str(e)}")
        flash('An error occurred while loading the activity.', 'error')
        return redirect(url_for('activity.list_activities'))