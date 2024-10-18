from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.activity import Activity
from app.forms import ActivityForm

bp = Blueprint('activity', __name__)

@bp.route('/')
def list_activities():
    activities = Activity.query.all()
    return render_template('activity/list.html', activities=activities)

@bp.route('/<int:id>')
def activity_detail(id):
    activity = Activity.query.get_or_404(id)
    return render_template('activity/detail.html', activity=activity)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
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
        flash('Activity created successfully!')
        return redirect(url_for('activity.list_activities'))
    return render_template('activity/create.html', form=form)

@bp.route('/search')
def search_activities():
    query = request.args.get('query', '')
    activities = Activity.query.filter(Activity.name.ilike(f'%{query}%')).all()
    return render_template('activity/list.html', activities=activities)