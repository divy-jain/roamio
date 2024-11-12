from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from app import db
from app.models.activity import Activity
from app.models.user import User
from app.forms import ActivityForm
from sqlalchemy import text, or_
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('activity', __name__, url_prefix='/activity')

@bp.route('/')
def list_activities():
    try:
        query = request.args.get('query', '')
        city = request.args.get('city', '')
        activity_type = request.args.get('activity_type', '')
        sort = request.args.get('sort', 'name')

        # Base query with privacy filter
        if current_user.is_authenticated:
            # Show public activities and own activities
            activities_query = Activity.query.join(User).filter(
                or_(
                    User.profile_visibility == True,  # Public users' activities
                    Activity.user_id == current_user.id  # User's own activities
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

        # Get distinct cities and activity types for filters (only from visible activities)
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

@bp.route('/new', methods=['GET', 'POST'])
@login_required  # Add this decorator
def new_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        try:
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
            db.session.commit()
            flash('Activity created successfully!', 'success')
            return redirect(url_for('activity.list_activities'))
        except Exception as e:
            logger.error(f"Error creating activity: {str(e)}")
            flash('An error occurred while creating the activity.', 'error')
            return render_template('activity/new.html', form=form)

    return render_template('activity/new.html', form=form)

@bp.route('/<int:id>')
def activity_detail(id):
    try:
        activity = Activity.query.get_or_404(id)
        
        # Check if user can view this activity
        if not activity.user.can_view_profile(current_user):
            flash('You do not have permission to view this activity.', 'error')
            return redirect(url_for('activity.list_activities'))
            
        return render_template('activity/detail.html', activity=activity)
    except Exception as e:
        logger.error(f"Error viewing activity {id}: {str(e)}")
        flash('An error occurred while loading the activity.', 'error')
        return redirect(url_for('activity.list_activities'))

# # app/routes/activity.py
# from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
# from flask_login import current_user
# from app import db
# from app.models.activity import Activity
# from app.forms import ActivityForm
# from sqlalchemy import text
# import logging

# logger = logging.getLogger(__name__)

# bp = Blueprint('activity', __name__, url_prefix='/activity')

# @bp.route('/')
# def list_activities():
#     try:
#         query = request.args.get('query', '')
#         city = request.args.get('city', '')
#         activity_type = request.args.get('activity_type', '')
#         sort = request.args.get('sort', 'name')

#         # Base query
#         activities_query = Activity.query

#         # Apply filters
#         if query:
#             activities_query = activities_query.filter(Activity.name.ilike(f'%{query}%'))
#         if city:
#             activities_query = activities_query.filter(Activity.city.ilike(f'%{city}%'))
#         if activity_type:
#             activities_query = activities_query.filter(Activity.activity_type == activity_type)

#         # Apply sorting
#         if sort == 'rating':
#             activities_query = activities_query.order_by(Activity.rating.desc())
#         else:
#             activities_query = activities_query.order_by(Activity.name)

#         activities = activities_query.all()

#         # Get distinct cities and activity types for filters
#         cities = db.session.query(Activity.city.distinct()).all()
#         activity_types = db.session.query(Activity.activity_type.distinct()).all()

#         return render_template('activity/list.html', 
#                              activities=activities,
#                              cities=[city[0] for city in cities],
#                              activity_types=[type[0] for type in activity_types])
                             
#     except Exception as e:
#         logger.error(f"Error listing activities: {str(e)}")
#         flash('An error occurred while loading activities.', 'error')
#         return render_template('activity/list.html', activities=[])

# @bp.route('/new', methods=['GET', 'POST'])  # Changed from /create to /new
# def new_activity():  # Changed from create_activity to new_activity
#     form = ActivityForm()
#     if form.validate_on_submit():
#         try:
#             activity = Activity(
#                 name=form.name.data,
#                 description=form.description.data,
#                 city=form.city.data,
#                 activity_type=form.activity_type.data,
#                 cost=form.cost.data,
#                 season=form.season.data,
#                 rating=float(form.rating.data),
#                 user_id=current_user.id  # Link activity to current user
#             )
#             db.session.add(activity)
#             db.session.commit()
#             flash('Activity created successfully!', 'success')
#             return redirect(url_for('activity.list_activities'))
#         except Exception as e:
#             logger.error(f"Error creating activity: {str(e)}")
#             flash('An error occurred while creating the activity.', 'error')
#             return render_template('activity/new.html', form=form)

#     return render_template('activity/new.html', form=form)

# @bp.route('/<int:id>')
# def activity_detail(id):
#     try:
#         activity = Activity.query.get_or_404(id)
#         return render_template('activity/detail.html', activity=activity)
#     except Exception as e:
#         logger.error(f"Error viewing activity {id}: {str(e)}")
#         flash('An error occurred while loading the activity.', 'error')
#         return redirect(url_for('activity.list_activities'))