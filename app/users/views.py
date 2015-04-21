# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template, render_template_string
from flask import request, url_for, current_app
from flask_user import current_user, login_required, SQLAlchemyAdapter, roles_required
from flask_user.emails import _render_email
from app.app_and_db import app, db, stripe_keys
from app.users.forms import UserProfileForm, TaskForm, ReportForm, EditTaskForm
from app.users.models import Task, Report, User, Role
from wtforms import RadioField, SubmitField
from flask_wtf import Form
from datetime import date, timedelta

import requests


#
# Home page
#
commonDataStruct = {}
@app.route('/')
def home_page():
    print url_for('callback')
    tasks_due_today = None
    tasks_due_tomorrow = None
    streak = None
    print url_for('create_report', task="task")
    if current_user.is_authenticated():
        tasks = Task.query.filter_by(user_id = current_user.user_profile.id).all()
        today = date.today()
        tommorrow = today + timedelta(days=1)
        tasks_due_today = [task for task in tasks if task.due_date == today]
        tasks_due_tomorrow = [task for task in tasks if task.due_date == tommorrow]
        streak = current_user.streak
    return render_template('pages/home_page.html', tasks_today = tasks_due_today, tasks_tomorrow = tasks_due_tomorrow,
     streak = streak)

@app.route('/approve', methods=['GET', 'POST'])
@roles_required('admin')
def approve():
    if request.method == 'POST':
        for report_status in request.form:
            report_id, approved = report_status.split('|')
            report = Report.query.filter_by(id=report_id).first()
            task = Task.query.filter_by(id=report.task_id).first()
            if task == None:
                db.session.delete(report)
                db.session.commit()
                break
            report.task.due_date = date.today() + timedelta(days=task.repeat_frequency)
            report.active = True
            if approved == "approved":
                report.approved = True
            elif approved == "rejected":
                report.rejected = True
        db.session.commit()
    user_profile = current_user.user_profile
    reports = Report.query.filter_by(approved = False, rejected=False).all()
    class F(Form):
        submit = SubmitField('Save')
        pass
    for name in [report for report in reports]:
        setattr(F, name.name, RadioField(name.content))
    form = F()

    fv = [(report.id, report.name , report.content) for report in reports]
    return render_template('reports/approve_reports.html', form=form, fv = fv)
@app.route('/check_reports')
def check_reports():
    if authorize_cron(request):
        user_manager = current_app.user_manager
        today = date.today()
        bad_reports = Report.query.filter_by(active=True, rejected=True).all()
        good_reports = Report.query.filter_by(active=True, approved=True).all()
        for report in good_reports:
            user = User.query.filter_by(id=report.user_id).first()
            user.streak += 1
            report.active = False
        for report in bad_reports:
            user = User.query.filter_by(id=report.user_id).first()
            user.streak = 0
            task = report.task
            report.active = False
            charge(user, task.cost * 100)

        overdue_tasks = Task.query.filter_by(due_date=today).all()
        for task in overdue_tasks:
            user = User.get_user(task.user_id)
            user.streak = 0
            charge(user, task.cost * 100)
        db.session.commit()
        user_manager.send_email_function(app.config['log_email', 'check_reports sent',
                                             '', str([bad_reports, overdue_tasks, overdue_tasks]))
        return "check_reports"
    return ""


# User Profile form
#
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    user_profile = current_user.user_profile
    form = UserProfileForm(request.form, user_profile)
    if current_user.username == "admin" and all([False for role in current_user.roles if role.name =='admin']):
        current_user.roles.append(Role(name='admin'))
        db.session.commit()
    # Process valid POST
    if request.method=='POST' and form.validate():

        # Copy form fields to user_profile fields
        form.populate_obj(user_profile)

        # Save user_profile
        db.session.commit()
        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('users/user_profile_page.html',
        form=form)


@app.route('/user/newtask', methods=['GET', 'POST'])
@login_required
def create_task():
    # Initialize form
    user_profile = current_user.user_profile
    task = Task()
    form = TaskForm(request.form, task)

    # Process valid POST
    if request.method=='POST' and form.validate():
        # Copy form fields to user_profile fields

        form.populate_obj(task)
        task.user_id = user_profile.id
        task.due_date = date.today() #+ timedelta(days=task.repeat_frequency)
        prev_task = Task.query.filter_by(user_id = user_profile.id, name=task.name).first()
        if not prev_task:
            db.session.add(task)
            db.session.commit()

        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('tasks/task_create_page.html',
        form=form)


@app.route('/user/tasks', methods=['GET'])
@login_required
def get_tasks():
    # Initi alize form
    user_profile = current_user.user_profile
    tasks = Task.query.filter_by(user_id = user_profile.id).all()
    # Process valid POST
    if request.method=='POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(user_profile)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('tasks/task_list_page.html', tasks = tasks)
@app.route('/user/<task>/edit', methods=['GET', 'POST'])
def edit_task(task=None):
    task_instance = Task.query.filter_by(id=task, user_id=current_user.id).one()
    form = EditTaskForm(request.form, task_instance)
    if request.method == 'POST' and form.validate():
        form.populate_obj(task_instance)
        if form.delete.data == "Yes":
            db.session.delete(task_instance)
        else:
            db.session.merge(task_instance)
        db.session.commit()
        return redirect(url_for('get_tasks'))
    return render_template('tasks/task_edit.html', form=form, task=task_instance)

@app.route('/user/<task>/newreport', methods=['GET', 'POST'])
@login_required
def create_report(task=None):
    # Initialize form
    user_profile = current_user.user_profile
    report = Report()
    form = ReportForm(request.form, report)
    verified_task = Task.query.filter_by(name=task, user_id=user_profile.id).first()

    # Process valid POST
    if request.method=='POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(report)
        report.user_id = user_profile.id
        report.task_id = verified_task.id
        report.task = verified_task
        verified_task.due_date = date.today() + timedelta(days=verified_task.repeat_frequency)
        db.session.add(report)
        db.session.commit()
        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('reports/report_create_page.html',
        form=form, task=task)

@app.route('/user/reports', methods=['GET'])
@login_required
def get_reports():
    # Initialize form
    user_profile = current_user.user_profile
    reports = Report.query.filter_by(user_id = user_profile.id).all()
    # Process valid POST
    if request.method=='POST':
        # Copy form fields to user_profile fields
        form.populate_obj(user_profile)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('home_page'))

    # Process GET or invalid POST
    return render_template('reports/report_list_page.html', reports = reports)

@app.route('/stripe', methods=['POST', 'GET'])
@login_required
def stripe_checkout():
    if request.method=='POST':
        token = request.form['stripeToken']

        # Create a Customer
        customer = stripe.Customer.create(
            card=token,
            email = current_user.email
        )
        current_user.customer_id = customer.id
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template('stripe/stripe_test.html', key=stripe_keys['publishable_key'])

def authorize_cron(request):
    if request.environ['REMOTE_ADDR'] == '127.0.0.1' and request.args.get('pw') == u"HBHBhbwdhBHBhjwlbdnfnjnjNJBuwdhbBHBhwbdhHNWNDAladkoKOjdOJiwNJNJNJNJNdBjNkmKMKMNDKENFLAFCBNVCM":
        return True
    return False

@app.route('/reminder')
def send_reminders():
    if authorize_cron(request):
        user_manager = current_app.user_manager
        overdue_tasks = Task.query.filter_by(due_date=date.today()).all()
        users = []
        for task in overdue_tasks:
            user = User.get_user(task.user_id)
            users.append(user.email)
            subject, html_message, text_message = _render_email(
                    "emails/reminder",
                    user=user,
                    app_name="Motivate",
                    report_link="https://quinnjarrell.me%s" % url_for('create_report', task=task.name))
            user_manager.send_email_function(user.email, subject,
                                             html_message, text_message)
        user_manager.send_email_function('quinnjarr@gmail.com', 'send_reminders sent',
                                             '', '')
        return "send_reminders"
    return ""

@app.route('/charge', methods=['GET'])
@login_required
def charge_web():
    amount = 5
    charge(current_user, amount)
    return render_template('stripe/charge.html', amount=amount)
def charge(user, amount):
    # Amount in cents

    charge = stripe.Charge.create(
        customer=user.customer_id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

@app.route('/stripe_redirect_test',methods=['GET', 'POST'])
def callback():
    code   = request.args.get('code')
    data   = {
             'client_secret': app.config['API_KEY'],
             'grant_type': 'authorization_code',
             'client_id': app.config['CLIENT_ID'],
             'code': code
           }

    # Make /oauth/token endpoint POST request
    url = app.config['SITE'] + app.config['TOKEN_URI']
    resp = requests.post(url, params=data)
    # Grab access_token (use this as your user's API key)
    token = resp.json.get('access_token') 
    return redirect(url_for('home_page'))   