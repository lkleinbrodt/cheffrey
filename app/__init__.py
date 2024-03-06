from flask import Flask, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_session import Session
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = (
    "login"  # name of endpoint for the login view in routes.py, same as url_for()
)
Session(app)
cache = Cache(app)
CORS(app)
jwt = JWTManager(app)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


admin = Admin(
    app, name="Admin Panel", template_mode="bootstrap3", index_view=MyAdminIndexView()
)

from app import routes, errors, models


class myModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == "admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


admin.add_view(myModelView(models.User, db.session))
admin.add_view(myModelView(models.Recipe, db.session))
admin.add_view(myModelView(models.Favorite, db.session))
admin.add_view(myModelView(models.RecipeList, db.session))

with app.app_context():
    db.create_all()
