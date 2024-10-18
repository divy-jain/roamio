from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.activity import Activity

bp = Blueprint('activity', __name__)


@bp.route('/activities')
def list_activities():
    activities = Activity.query.all()
    return render_template('activity/list.html', activities=activities)

@bp.route('/activity/<int:id>')
def activity_detail(id):
    activity = Activity.query.get_or_404(id)
    return render_template('activity/detail.html', activity=activity)

@bp.route('/activity/create', methods=['GET', 'POST'])
@login_required
def create_activity():
    if request.method == 'POST':
        activity = Activity(
            name=request.form['name'],
            description=request.form['description'],
            city=request.form['city'],
            activity_type=request.form['activity_type'],
            cost=request.form['cost'],
            season=request.form['season']
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activity created successfully!')
        return redirect(url_for('activity.list_activities'))
    return render_template('activity/create.html')

@bp.route('/activities/search')
def search_activities():
    query = request.args.get('query', '')
    activities = Activity.query.filter(Activity.name.ilike(f'%{query}%')).all()
    return render_template('activity/list.html', activities=activities)