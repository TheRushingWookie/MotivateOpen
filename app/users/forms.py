# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import StringField, SubmitField, validators, IntegerField, DecimalField, RadioField
from wtforms.validators import Required
from flask import current_app

# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])

# Define the User profile form
class UserProfileForm(Form):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')

class TaskForm(Form):
    name = StringField('Task name', validators=[
        validators.DataRequired('Task name is required')])
    description = StringField('Task description', validators=[
        validators.DataRequired('Task description is required')])
    repeat_frequency = IntegerField('Number of days between reports?', validators=[
        validators.DataRequired('Repeat frequency is required'),validators.NumberRange(max=99)])
    cost = IntegerField('How much are you willing to lose in dollars?', validators=[
        validators.DataRequired('Cost is required'), validators.NumberRange(max=99)])
    submit = SubmitField('Save')

class ReportForm(Form):
    content = StringField('What did you do today?', validators=[
        validators.DataRequired('Report description is required')])
    submit = SubmitField('Save')

class EditTaskForm(Form):
    delete = RadioField("Delete this task?", choices=[("Yes", "yes"), ("No", "no")], default="No")
    cost = IntegerField("Change the cost to ")
    repeat_frequency = IntegerField('Number of days between reports?')
    submit = SubmitField('Save')
