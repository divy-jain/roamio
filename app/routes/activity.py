from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.activity import Activity
from app.forms import ActivityForm
from sqlalchemy import text

bp = Blueprint('activity', __name__)

@bp.route('/')
def list_activities():
    query = request.args.get('query', '')
    city = request.args.get('city', '')
    activity_type = request.args.get('activity_type', '')
    sort = request.args.get('sort', 'name')

    # Base SQL query
    sql_query = """
        SELECT * FROM activities
        WHERE (:query IS NULL OR name ILIKE '%' || :query || '%')
        AND (:city IS NULL OR city = :city)
        AND (:activity_type IS NULL OR activity_type = :activity_type)
    """

    # Sorting logic
    if sort == 'rating':
        sql_query += " ORDER BY rating DESC"
    else:
        sql_query += " ORDER BY name ASC"

    # Execute the query with parameters
    activities = db.session.execute(
        text(sql_query),
        {'query': query if query else None, 'city': city if city else None, 'activity_type': activity_type if activity_type else None}
    ).fetchall()

    # Get distinct cities and activity types
    cities = db.session.execute(text("SELECT DISTINCT city FROM activities")).fetchall()
    cities = [city[0] for city in cities]

    activity_types = db.session.execute(text("SELECT DISTINCT activity_type FROM activities")).fetchall()
    activity_types = [type[0] for type in activity_types]

    return render_template('activity/list.html', activities=activities, cities=cities, activity_types=activity_types)

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
            season=form.season.data,
            rating=int(form.rating.data)
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