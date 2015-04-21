#!/Users/lingthio/envs/glamdring/bin/python

# The 'runserver.py' file is used to run a Flask application
# using the development WSGI web server provided by Flask.
# Run 'python runserver.py' and point your web browser to http://localhost:5000/


from app.app_and_db import app, db
from app.startup.init_app import init_app
import os
from flask_sslify import SSLify
from OpenSSL import SSL
from flask_user import UserManager, SQLAlchemyAdapter
from app.users.models import User

init_app(app, db)
#sslify = SSLify(app)
from werkzeug.contrib.fixers import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == 'main' or __name__ == "__main__":
	app.run(debug=True, port=4000)