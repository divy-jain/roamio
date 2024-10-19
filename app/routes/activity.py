from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.activity import Activity
from app.forms import ActivityForm
from sqlalchemy import func

bp = Blueprint('activity', __name__)

@bp.route('/')
def list_activities():
    query = request.args.get('query', '')
    city = request.args.get('city', '')
    activity_type = request.args.get('activity_type', '')
    sort = request.args.get('sort', 'name')

    activities = Activity.query

    if query:
        activities = activities.filter(Activity.name.ilike(f'%{query}%'))
    if city:
        activities = activities.filter(Activity.city == city)
    if activity_type:
        activities = activities.filter(Activity.activity_type == activity_type)

    if sort == 'rating':
        activities = activities.order_by(Activity.average_rating.desc())
    else:
        activities = activities.order_by(Activity.name)

    cities = db.session.query(Activity.city.distinct()).all()
    cities = [city[0] for city in cities]
    activity_types = db.session.query(Activity.activity_type.distinct()).all()
    activity_types = [type[0] for type in activity_types]

    return render_template('activity/list.html', activities=activities.all(), cities=cities, activity_types=activity_types)

@bp.route('/create', methods=['GET', 'POST'])
def create_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(
            name=form.name.data,
            description=form.description.data,
            city=form.city.data,
            activity_type=form.activity_type.data,
            cost=form.cost.data,
            season=form.season.data
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activity created successfully!', 'success')
        return redirect(url_for('activity.list_activities'))
    return render_template('activity/create.html', form=form)

@bp.route('/<int:id>')
def activity_detail(id):
    activity = Activity.query.get_or_404(id)
    return render_template('activity/detail.html', activity=activity)