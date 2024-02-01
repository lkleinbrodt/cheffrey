from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_session import Session
from flask_caching import Cache


app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login' #name of endpoint for the login view in routes.py, same as url_for()
Session(app)
cache = Cache(app)


admin = Admin(app, name = 'Admin Panel', template_mode='bootstrap3')

from app import routes, errors, models

admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Recipe, db.session))
# admin.add_view(ModelView(models.RecurringDate, db.session))

with app.app_context():
    db.create_all()