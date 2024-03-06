from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
    jsonify,
    Response,
)
from flask_login import current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlalchemy as sa
from config import Config
from sqlalchemy.exc import IntegrityError
from app.src import recipes_to_shopping_list, create_meal_plan_html, HashableRecipe
from app import app, db, admin
import json
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from urllib.parse import urlsplit
from werkzeug.security import check_password_hash
from app.models import User, Recipe, RecipeList, Favorite
from app.forms import LoginForm, RegistrationForm, SettingsForm
import datetime
from sqlalchemy.sql import func  # Import the func function

limiter = Limiter(app=app, key_func=get_remote_address)


@app.before_request
def before_request():
    pass


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("explore"))
    return render_template("index.html")


@app.route("/explore")
@login_required
def explore():
    return render_template("explore.html")


@app.route("/api/refresh-explore", methods=["GET"])
@login_required
def refresh_explore():
    session.pop("explore_recipes", None)
    return jsonify({"status": "success"})


@app.route("/api/load-more-recipes/<int:page>")
@login_required
def load_more_recipes(page):
    per_page = 6  # Adjust as needed
    max_pages = 10

    if "explore_recipes" not in session:
        recipes = Recipe.query.order_by(func.random()).limit(per_page * max_pages)
        session["explore_recipes"] = [recipe.to_dict() for recipe in recipes]
        # recipes = Recipe.query.paginate(page=page, per_page=per_page, error_out=False).items

    recipes = session["explore_recipes"][per_page * (page - 1) : per_page * page]
    # recipes = [Recipe.from_dict(recipe) for recipe in recipes]

    ##TODO: improve
    # for recipe in recipes:
    #     # TODO: make a decision regarding eval here vs eval in to_dict and just using a dict here
    #     recipe.ingredient_list = eval(recipe.ingredients)
    #     recipe.instruction_list = eval(recipe.instructions_list)
    #     recipe_list_item = RecipeList.query.filter_by(
    #         user_id=current_user.id, recipe_id=recipe.id
    #     ).first()
    #     if recipe_list_item:
    #         recipe.in_list = True
    #     else:
    #         recipe.in_list = False
    #     favorite_item = Favorite.query.filter_by(
    #         user_id=current_user.id, recipe_id=recipe.id
    #     ).first()
    #     if favorite_item:
    #         recipe.in_favorites = True
    #     else:
    #         recipe.in_favorites = False

    # TODO: improve

    return jsonify({"recipes": recipes})


@app.route("/login", methods=["POST"])
@limiter.limit("5 per 5 seconds")  # Adjust the limit as needed
def login():

    # Assuming the incoming request is JSON
    data = request.get_json()

    # Extract username and password from the JSON data
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify(access_token=access_token), 200


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "message")
    return redirect(url_for("index"))


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)

        return jsonify(access_token=access_token), 200

    except:
        db.session.rollback()
        return jsonify({"message": "Error creating user"}), 500


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "GET":
        form = SettingsForm(
            phone_number=current_user.phone_number,
        )
    elif request.method == "POST":
        form = SettingsForm(request.form)

    if request.method == "POST" and form.validate_on_submit():
        # Update user settings in the database
        user = User.query.filter_by(id=current_user.id).first()

        user.phone_number = form.phone_number.data

        try:
            db.session.commit()
            flash("Settings successfully updated.", "success")
            redirect(url_for("settings"))
        except IntegrityError:
            db.session.rollback()
            flash("Error saving settings. Please try again.", "error")
            return redirect(url_for("settings"))

    return render_template("settings.html", settings_form=form)


@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template("recipe.html", recipe=recipe)


@app.route("/api/add-to-favorites/<int:recipe_id>")
@login_required
def add_to_favorites(recipe_id):
    favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    try:
        db.session.add(favorite)
        db.session.commit()
        # flash('Added to favorites!', 'success')
        return jsonify({"status": "success"})
    except IntegrityError:
        db.session.rollback()
        # flash('Error adding to favorites. Please try again.', 'error')
        return jsonify({"status": "error"})


@app.route("/api/remove-from-favorites/<int:recipe_id>")
@login_required
def remove_from_favorites(recipe_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    try:
        db.session.delete(favorite)
        db.session.commit()
        # flash('Removed from favorites.', 'success')
    except:
        db.session.rollback()
        # flash('Error removing from favorites. Please try again.', 'error')
    return jsonify({"status": "success"})


@app.route("/api/add-to-recipe-list/<int:recipe_id>")
@login_required
def add_to_recipe_list(recipe_id):

    recipe_list_item = RecipeList(user_id=current_user.id, recipe_id=recipe_id)
    try:
        db.session.add(recipe_list_item)
        db.session.commit()
        # flash('Added to recipe list!', 'success')
        return jsonify({"status": "success"})
    except IntegrityError:
        db.session.rollback()
        # flash('Error adding to recipe list. Please try again.', 'error')
        return jsonify({"status": "error"})


@app.route("/api/remove-from-recipe-list/<int:recipe_id>")
@login_required
def remove_from_recipe_list(recipe_id):
    recipe_list_item = RecipeList.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    try:
        db.session.delete(recipe_list_item)
        db.session.commit()
        # flash('Removed from recipe list.', 'success')
    except:
        db.session.rollback()
        # flash('Error removing from recipe list. Please try again.', 'error')
    return jsonify({"status": "success"})


@app.route("/clear-recipe-list")
@login_required
def clear_recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    for recipe_list_item in recipe_list:
        db.session.delete(recipe_list_item)
    db.session.commit()
    return redirect(url_for("recipe_list"))


@app.route("/api/clear-recipe-list")
@login_required
def clear_recipe_list_api():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    for recipe_list_item in recipe_list:
        db.session.delete(recipe_list_item)
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/api/submit-cooked-recipes", methods=["POST"])
@login_required
def submit_cooked_recipes():
    recipe_ids = request.json["recipe_ids"]
    user = User.query.get(current_user.id)
    for id in recipe_ids:
        try:
            recipe = Recipe.query.get(id)
            user.add_cooked_recipe(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"status": "error"})
    return jsonify({"status": "success"})


@app.route("/api/toggle-recipe-in-list/<int:recipe_id>")
@login_required
def toggle_recipe_in_list(recipe_id):
    recipe_list_item = RecipeList.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    if recipe_list_item:
        db.session.delete(recipe_list_item)
        # flash('Removed from recipe list.', 'success')
    else:
        recipe_list_item = RecipeList(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(recipe_list_item)
        # flash('Added to recipe list!', 'success')
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/api/toggle-favorite/<int:recipe_id>")
@login_required
def toggle_favorite(recipe_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    if favorite:
        db.session.delete(favorite)
        # flash('Removed from favorites.', 'success')
    else:
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        # flash('Added to favorites!', 'success')
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/saved")
@login_required
def saved():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorites = [favorite.recipe for favorite in favorites]
    for recipe in favorites:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        recipe.in_favorites = True

    cooked = current_user.cooked_recipes
    for recipe in cooked:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()

        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        if recipe in favorites:
            recipe.in_favorites = True
        else:
            recipe.in_favorite = False

    return render_template("saved.html", favorites=favorites, cooked=cooked)


@app.route("/recipe-list")
@jwt_required()
def recipe_list():
    print("WOAH")
    recipe_list = RecipeList.query.filter_by(user_id=get_jwt_identity()).all()
    recipes = [r.to_dict() for r in recipe_list]
    # TODO: re do this
    # for recipe_list_item in recipe_list:

    #     recipe = recipe_list_item.recipe
    #     recipe.ingredient_list = eval(recipe.ingredients)
    #     recipe.instruction_list = eval(recipe.instructions_list)
    #     recipe.in_list = True
    #     favorite_item = Favorite.query.filter_by(
    #         user_id=current_user.id, recipe_id=recipe.id
    #     ).first()
    #     if favorite_item:
    #         recipe.in_favorites = True
    #     else:
    #         recipe.in_favorites = False
    #     recipes.append(recipe)

    return jsonify({"recipes": recipes})


@app.route("/cooked-recipes")
@login_required
def cooked_recipes():
    user = User.query.get(current_user.id)
    recipes = user.cooked_recipes
    # TODO: should have its own template but it will end up being the same so why bother?
    return render_template("recipe_list.html", recipes=recipes, hideClear=True)


@app.route("/load-meal-plan")
@login_required
def load_meal_plan():
    return render_template("meal_plan_loading.html")


@app.route("/generate-meal-plan", methods=["GET"])
@login_required
def generate_meal_plan():
    today = datetime.date.today()
    app.logger.info("Generating meal plan")
    filename = f"Cheffrey Meal Plan {today.strftime('%b %d')}"

    recipe_list_items = RecipeList.query.filter_by(user_id=current_user.id).all()

    recipe_list = [
        HashableRecipe(recipe_item.recipe) for recipe_item in recipe_list_items
    ]

    for recipe in recipe_list:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)

    recipe_list = tuple(recipe_list)

    shopping_list = recipes_to_shopping_list(recipe_list)

    meal_plan_html = create_meal_plan_html(shopping_list, recipe_list)

    response = Response(meal_plan_html, content_type="text/html")

    response.headers["Content-Disposition"] = f"attachment; filename={filename}.html"
    app.logger.info("Done generating meal plan")
    return response


@app.route("/shopping-list")
@login_required
def shopping_list():
    # TODO: ugly
    with open("data/ingredient2category.json", "r") as f:
        ingredient2category = json.load(f)

    recipe_list_items = RecipeList.query.filter_by(user_id=current_user.id).all()

    recipe_list = [
        HashableRecipe(recipe_item.recipe) for recipe_item in recipe_list_items
    ]

    ingredient_dict = {}

    n_ingredients = 0
    for recipe in recipe_list:
        for ingredient in eval(recipe.ingredients):
            category = ingredient2category.get(ingredient, "Other")
            ingredient_dict[category] = ingredient_dict.get(category, []) + [ingredient]
            n_ingredients += 1

    # Sort ingredient_dict by category, with "Other" category last
    ingredient_dict = dict(
        sorted(ingredient_dict.items(), key=lambda x: (x[0] == "Other", x[0]))
    )

    # dict_list = [{}, {}, {}]
    # running_dict = {}
    # limit = n_ingredients / 3
    # ingredient_counter = 0
    # dict_counter = 0
    # for category, ingredients in ingredient_dict.items():
    #     running_dict[category] = ingredients
    #     ingredient_counter += len(ingredients)
    #     dict_list[dict_counter] = running_dict
    #     if (ingredient_counter > limit) & (dict_counter < 2):
    #         running_dict = {}
    #         ingredient_counter = 0
    #         dict_counter += 1
    dict_list = [{}, {}, {}]
    counter = 0
    for category, ingredients in ingredient_dict.items():
        dict_list[counter][category] = ingredients
        counter += 1
        if counter == 3:
            counter = 0
    return render_template(
        "shopping_list.html",
        ingredient_dict=ingredient_dict,
        ingredient_dict1=dict_list[0],
        ingredient_dict2=dict_list[1],
        ingredient_dict3=dict_list[2],
    )


@app.route("/favicon.ico")
def favicon():
    return url_for("static", filename="data:,")


@app.route("/api/get-recipe-list-count", methods=["GET"])
@login_required
def get_recipe_list_count():
    # TODO: which ones better?
    # count = len(current_user.recipe_list)
    count = len(RecipeList.query.filter_by(user_id=current_user.id).all())
    return jsonify({"count": count})


@app.route("/api/get-recipe-list", methods=["GET"])
@login_required
def get_recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    recipes = []
    for recipe_list_item in recipe_list:
        recipe = recipe_list_item.recipe
        favorite_item = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        recipe.in_list = True
        recipes.append(recipe)
    return jsonify({"recipes": recipes})


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    recipes = Recipe.query.filter(Recipe.title.ilike(f"%{query}%")).all()

    for recipe in recipes:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        favorite_item = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False

    return render_template("search.html", recipes=recipes, search_term=query)
