import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Tuple, Optional

from flask_login import UserMixin
from app import db, login, app


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    verification_code = db.Column(db.String(6))
    verification_code_timestamp = db.Column(DateTime(timezone=True), server_default=func.now())
    
    last_seen = sa.Column(DateTime, default=func.now())
    
    role = db.Column(db.String(80), default='user')
    
    favorites = so.relationship('Favorite', back_populates='user')
    recipe_list = so.relationship('RecipeList', back_populates='user')
    

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(64), index=True, unique=True)
    author = sa.Column(sa.String(64))
    canonical_url = sa.Column(sa.String(255))
    category = sa.Column(sa.String(128))
    image_url = sa.Column(sa.String(255))
    ingredients = sa.Column(sa.String(5000))
    description = sa.Column(sa.String(1024))
    instructions = sa.Column(sa.String(10000))
    instructions_list = sa.Column(sa.String(10000))
    total_time = sa.Column(sa.Integer)
    yields = sa.Column(sa.String(64))
    
    favorited_by = so.relationship('Favorite', back_populates='recipe')
    selected_by = so.relationship('RecipeList', back_populates='recipe')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
    
    def to_dict(self, as_str = False):
        d = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'canonical_url': self.canonical_url,
            'category': self.category,
            'image_url': self.image_url,
            'ingredients': self.ingredients,
            'description': self.description,
            'instructions': self.instructions,
            'instructions_list': self.instructions_list,
            'total_time': self.total_time,
            'yields': self.yields
        }
        if as_str:
            d = str(d)
        return d
    
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'))
    
    user = so.relationship('User', back_populates='favorites')
    recipe = so.relationship('Recipe', back_populates='favorited_by')
    
    def __repr__(self):
        return f'<Favorite {self.id}>'
    
class RecipeList(db.Model):
    __tablename__ = 'recipe_lists'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'))
    
    user = so.relationship('User', back_populates='recipe_list')
    recipe = so.relationship('Recipe', back_populates='selected_by')
    
    def __repr__(self):
        return f'<RecipeList {self.id}>'
    
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


