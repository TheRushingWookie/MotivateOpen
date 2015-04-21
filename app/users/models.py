# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from app.app_and_db import db

# Define the User model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_profile_id = db.Column(db.Integer(), db.ForeignKey('user_profile.id', ondelete='CASCADE'))

    # Flask-User fields
    active = db.Column(db.Boolean(), nullable=False, server_default='0', default = True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    customer_id = db.Column(db.String(100), nullable=False, server_default='')
    stripeToken = db.Column(db.String(100), nullable=False, server_default='')
    streak = db.Column(db.Integer(), default=0)
    # Relationships
    user_profile = db.relationship('UserProfile', uselist=False, backref="user")
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))
    @classmethod
    def get_user(cls, id):
        return User.query.filter_by(id=id).one()
# Define the UserProfile model
#   The User model contains login-related fields
#   The UserProfile model contains additional User fields
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, server_default='')
    last_name = db.Column(db.String(50), nullable=False, server_default='')

    @classmethod
    def get_tasks_ids(cls, user):
        return Tasks.query.filter_by(user = user).all()
    # def full_name(self):
    #     """ Return 'first_name last_name' """
    #     # Handle records with an empty first_name or an empty last_name
    #     name = self.first_name
    #     name += ' ' if self.first_name and self.last_name else ''
    #     name += self.last_name
    #     return name


# Define the Role model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


# Define the UserRoles association model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Task(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('user_profile.id', ondelete='CASCADE'))
    user_profile = db.relationship('UserProfile', uselist=False, backref="task", order_by=id)

    name = db.Column(db.String(50), nullable=False, server_default='')

    repeat_frequency = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False, server_default='')
    due_date = db.Column(db.Date)

    @classmethod
    def get_task(cls, task_name, user):
        return Task.query.filter_by(name = task_name, user_profile = user).first()

    def __str__(self):
        return "Task %s: is repeated every %s days. It costs $%s." % (self.name, self.repeat_frequency, self.cost)

class Report(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('user_profile.id', ondelete='CASCADE'))
    user_profile = db.relationship('UserProfile', uselist=False, backref="report", order_by=id)

    name = db.Column(db.String(50), nullable=False, server_default='')
    
    task_id = db.Column(db.Integer(), db.ForeignKey('task.id', ondelete='CASCADE'))
    task = db.relationship('Task', uselist=False, backref="report", order_by=id)

    content = db.Column(db.String(500), nullable=False, server_default='')
    active = db.Column(db.Boolean(), default=False)
    approved = db.Column(db.Boolean(), default=False)
    rejected = db.Column(db.Boolean(), default=False)
    def __str__(self):
        return "Report %s is related to task %s. It has content %s" % (self.name, self.task.name, self.content)

