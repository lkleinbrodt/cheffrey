import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import DateTime, and_
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


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255), index=True, unique=True)
    author = sa.Column(sa.String(64))
    canonical_url = sa.Column(sa.String(256))
    category = sa.Column(sa.String(256))
    image_url = sa.Column(sa.String(255))
    description = sa.Column(sa.String(1024))
    instructions = sa.Column(sa.String(10000))
    ingredients = sa.Column(
        sa.String(5000)
    )  # yes we could use a relationship here, but that would be overkill, just honestly dont need it. will implmement later if it's helpful
    total_time = sa.Column(sa.Integer)
    yields = sa.Column(sa.String(64))
    is_public = sa.Column(sa.Boolean, default=True)

    favorited_by = so.relationship("Favorite", back_populates="recipe")
    selected_by = so.relationship("RecipeList", back_populates="recipe")
    cookbooked_by = so.relationship("CookBook", back_populates="recipe")

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
            "description": self.description,
            "instructions": self.get_instructions(),
            "ingredients": self.get_ingredients(),
            "total_time": self.total_time,
            "yields": self.yields,
            "is_public": self.is_public,
        }
        if "in_cookbook" in self.__dict__:
            d["in_cookbook"] = self.in_cookbook
        if "in_recipe_list" in self.__dict__:
            d["in_recipe_list"] = self.in_recipe_list

        if as_str:
            d = str(d)
        return d

    @property
    def ingredient_list(self):
        return self.get_ingredients()

    def get_ingredients(self):
        return self.ingredients.split(",")

    def get_instructions(self):
        return self.instructions.split("\n")

    def update(self, data: dict):
        """
        Update the recipe with the data in the dictionary.

        Parameters:
        - data (dict): Dictionary containing the new recipe data.
        """
        self.title = data.get("title", self.title)
        self.category = data.get("category", self.category)
        self.image_url = data.get("image_url", self.image_url)
        self.description = data.get("description", self.description)
        self.instructions = data.get("instructions", self.instructions)
        self.ingredients = data.get("ingredients", self.ingredients)
        self.total_time = data.get("total_time", self.total_time)
        self.yields = data.get("yields", self.yields)
        self.is_public = data.get("is_public", self.is_public)

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
            description=data["description"],
            instructions=data["instructions"],
            total_time=data["total_time"],
            yields=data["yields"],
            is_public=data["is_public"],
        )


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(128), index=True, unique=True)
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
    cookbook = so.relationship("CookBook", back_populates="user")

    cooked_recipes = db.relationship(
        "Recipe",
        secondary=cooked_recipes_table,
        backref=db.backref("cooking_users", lazy="dynamic"),
    )

    email_verified = db.Column(db.Boolean, default=False)

    # TODO: I dont like this implementation, using deeplinking would be better
    # but that is more complex and requires more setup
    can_change_password = db.Column(db.Boolean, default=False)
    can_change_password_expiry = db.Column(
        db.DateTime, default=datetime.datetime.utcnow
    )
    change_password_code = db.Column(db.String(6), nullable=True)

    def add_cooked_recipe(self, recipe):
        if recipe not in self.cooked_recipes:
            self.cooked_recipes.append(recipe)

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def tag_recipes(self, recipes: list[Recipe], as_json=False) -> list[Recipe]:
        """
        Tags the recipes in the list with whether or not they are in the user's cookbook or recipe list.
        """
        output = []
        if isinstance(recipes[0], dict):
            cookbook_ids = [cb.recipe.id for cb in self.cookbook]
            recipe_ids = [rl.recipe.id for rl in self.recipe_list]
            for recipe in recipes:
                recipe["in_cookbook"] = recipe["id"] in cookbook_ids
                recipe["in_recipe_list"] = recipe["id"] in recipe_ids
                if not as_json:
                    recipe = Recipe.from_dict(recipe)
                output.append(recipe)
        else:
            for recipe in recipes:
                recipe.in_cookbook = recipe in self.cookbook
                recipe.in_recipe_list = recipe in self.recipe_list
                if as_json:
                    recipe = recipe.to_dict()
                output.append(recipe)
        return output

    def get_cookbook(self, as_json=False):

        joined_query = (
            db.session.query(CookBook, RecipeList)
            .outerjoin(
                RecipeList,
                and_(
                    CookBook.user_id == RecipeList.user_id,
                    CookBook.recipe_id == RecipeList.recipe_id,
                ),
            )
            .filter(CookBook.user_id == self.id)
        )

        output = []

        for cookbook, recipe_list in joined_query:
            cookbook.recipe.in_cookbook = True
            cookbook.recipe.in_recipe_list = recipe_list is not None
            if as_json:
                output.append(cookbook.recipe.to_dict())
            else:
                output.append(cookbook.recipe)

        # sort output by title
        # TODO: should this just be done in the query?
        if not as_json:
            output = sorted(output, key=lambda x: x.title)
        else:
            output = sorted(output, key=lambda x: x["title"])
        return output

    def get_recipe_list(self, as_json=False):

        joined_query = (
            db.session.query(RecipeList, CookBook)
            .outerjoin(
                CookBook,
                and_(
                    CookBook.user_id == RecipeList.user_id,
                    CookBook.recipe_id == RecipeList.recipe_id,
                ),
            )
            .filter(RecipeList.user_id == self.id)
        )

        output = []

        for recipe_list, cookbook in joined_query:
            recipe_list.recipe.in_cookbook = cookbook is not None
            recipe_list.recipe.in_recipe_list = True
            if as_json:
                output.append(recipe_list.recipe.to_dict())
            else:
                output.append(recipe_list.recipe)

        return output


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


class CookBook(db.Model):
    __tablename__ = "cookbooks"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))

    user = so.relationship("User", back_populates="cookbook")
    recipe = so.relationship("Recipe", back_populates="cookbooked_by")


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
