import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Tuple, Optional

from flask_login import UserMixin
from app import db, login, app

cooked_recipes_table = db.Table(
    "cooked_recipes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id")),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    verification_code = db.Column(db.String(6))
    verification_code_timestamp = db.Column(
        DateTime(timezone=True), server_default=func.now()
    )

    last_seen = sa.Column(DateTime, default=func.now())

    role = db.Column(db.String(80), default="user")

    favorites = so.relationship("Favorite", back_populates="user")
    recipe_list = so.relationship("RecipeList", back_populates="user")

    cooked_recipes = db.relationship(
        "Recipe",
        secondary=cooked_recipes_table,
        backref=db.backref("cooking_users", lazy="dynamic"),
    )

    def add_cooked_recipe(self, recipe):
        if recipe not in self.cooked_recipes:
            self.cooked_recipes.append(recipe)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255), index=True, unique=True)
    author = sa.Column(sa.String(64))
    canonical_url = sa.Column(sa.String(256))
    category = sa.Column(sa.String(256))
    image_url = sa.Column(sa.String(255))
    ingredients = sa.Column(sa.String(5000))
    description = sa.Column(sa.String(1024))
    instructions = sa.Column(sa.String(10000))
    instructions_list = sa.Column(sa.String(10000))
    total_time = sa.Column(sa.Integer)
    yields = sa.Column(sa.String(64))

    favorited_by = so.relationship("Favorite", back_populates="recipe")
    selected_by = so.relationship("RecipeList", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe {self.title}>"

    def to_dict(self, as_str=False):
        d = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "canonical_url": self.canonical_url,
            "category": self.category,
            "image_url": self.image_url,
            "ingredients": self.ingredients,
            "description": self.description,
            "instructions": self.instructions,
            "instructions_list": self.instructions_list,
            "total_time": self.total_time,
            "yields": self.yields,
        }
        if as_str:
            d = str(d)
        return d

    @classmethod
    def from_dict(cls, data):
        """
        Create a Recipe object from a dictionary.

        Parameters:
        - data (dict): Dictionary containing recipe data.

        Returns:
        - Recipe: A Recipe object.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            author=data["author"],
            canonical_url=data["canonical_url"],
            category=data["category"],
            image_url=data["image_url"],
            ingredients=data["ingredients"],
            description=data["description"],
            instructions=data["instructions"],
            instructions_list=data["instructions_list"],
            total_time=data["total_time"],
            yields=data["yields"],
        )


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), index=True, unique=True)
    category = sa.Column(sa.String(255))

    def __repr__(self):
        return f"<Ingredient {self.name}>"

    def to_dict(self, as_str=False):
        d = {"id": self.id, "name": self.name, "description": self.description}
        if as_str:
            d = str(d)
        return d

    @classmethod
    def from_dict(cls, data):
        """
        Create a Ingredient object from a dictionary.

        Parameters:
        - data (dict): Dictionary containing ingredient data.

        Returns:
        - Ingredient: A Ingredient object.
        """
        return cls(id=data["id"], name=data["name"], description=data["description"])

    def __repr__(self):
        return f"<Ingredient {self.name}>"


class Favorite(db.Model):
    __tablename__ = "favorites"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))

    user = so.relationship("User", back_populates="favorites")
    recipe = so.relationship("Recipe", back_populates="favorited_by")

    def __repr__(self):
        return f"<Favorite {self.id}>"


# Note: I'm NOT doing a shopping list as a class,
# because it doesnt really need to be tracked behind the scenes
# you just need to display it once.
# and so i'll just implement some basic caching using the ingredients table
# because the only "hard" thing to do is classify an ingredient, this way we only need to do that once.


class RecipeList(db.Model):
    __tablename__ = "recipe_lists"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))

    user = so.relationship("User", back_populates="recipe_list")
    recipe = so.relationship("Recipe", back_populates="selected_by")

    def __repr__(self):
        return f"<RecipeList {self.id}>"


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
