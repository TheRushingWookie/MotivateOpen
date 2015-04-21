# This file declares the Flask Singletons 'app' and 'db'
# 'app' and 'db' are defined in a separate file to avoid circular imports
# Usage: from app.app_and_db import app, db
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy# This is the WSGI compliant web application object

import threading
import atexit
from flask import Flask
from datetime import date
import stripe
#ess to variable

app = Flask(__name__)

# This is the SQLAlchemy ORM object
db = SQLAlchemy(app)



stripe_keys = {
	'secret_key': os.environ['SECRET_KEY'],
	'publishable_key': os.environ['PUBLISHABLE_KEY']
}
stripe.api_key = stripe_keys['secret_key']
   