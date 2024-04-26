import random
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
from app import app, db, admin, jwt
import json
from flask_cors import cross_origin
from itsdangerous import URLSafeTimedSerializer
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
    decode_token,
    current_user as jwt_current_user,
)
from urllib.parse import urlsplit
from werkzeug.security import check_password_hash
from app.models import User, Recipe, RecipeList, Favorite, CookBook
from app.forms import LoginForm, RegistrationForm, SettingsForm
import datetime
from sqlalchemy.sql import func
from app.MailBot import MailBot
from app.RecipeReader import RecipeReader
import os


limiter = Limiter(app=app, key_func=get_remote_address)
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


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
def refresh_explore_api():
    session.pop("explore_recipes", None)
    return jsonify({"status": "success"})


@app.route("/refresh-explore", methods=["GET"])
@login_required
def refresh_explore():
    session.pop("explore_recipes", None)
    return jsonify({"status": "success"})


@app.route("/load-more-recipes/<int:page>")
@login_required
def load_more_recipes(page):
    per_page = 12  # Adjust as needed
    max_pages = 10

    if "explore_recipes" not in session:
        recipes = (
            Recipe.query.filter(
                (Recipe.is_public == True) | (Recipe.user_id == current_user.id)
            )
            .order_by(func.random())
            .limit(per_page * max_pages)
        )
        session["explore_recipes"] = [recipe.to_dict() for recipe in recipes]
        # recipes = Recipe.query.paginate(page=page, per_page=per_page, error_out=False).items

    recipes = session["explore_recipes"][per_page * (page - 1) : per_page * page]

    for recipe in recipes:

        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe["id"]
        ).first()
        if recipe_list_item:
            recipe["in_recipe_list"] = True
        else:
            recipe["in_recipe_list"] = False
        favorite_item = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe["id"]
        ).first()
        if favorite_item:
            recipe["in_favorites"] = True
        else:
            recipe["in_favorites"] = False

    return render_template("recipe_partial.html", recipes=recipes)


@app.route("/api/load-more-recipes/", methods=["GET"])
@jwt_required()
def load_more_recipes_api():
    page = int(request.args.get("page", 1))
    per_page = 6  # Adjust as needed
    max_pages = 10

    if "explore_recipes" not in session:
        recipes = (
            Recipe.query.filter(
                (Recipe.is_public == True) | (Recipe.user_id == current_user.id)
            )
            .order_by(func.random())
            .limit(per_page * max_pages)
        )

        session["explore_recipes"] = recipes
        # recipes = Recipe.query.paginate(page=page, per_page=per_page, error_out=False).items

    recipes = session["explore_recipes"][per_page * (page - 1) : per_page * page]
    recipes = jwt_current_user.tag_recipes(recipes, as_json=True)

    return jsonify({"recipes": recipes})


@app.route("/login", methods=["POST", "GET"])
@limiter.limit("5 per 5 seconds")  # Adjust the limit as needed
def login():
    if current_user.is_authenticated:
        return redirect(url_for("explore"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        # if there is no next, no problem
        # if there is a next, make sure it's a relative path, otherwise redirect to index
        # this is to prevent a malicious user from inserting a URL to a malicious site
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")

        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per 5 seconds")  # Adjust the limit as needed
def login_api():

    # Assuming the incoming request is JSON
    data = request.json

    email = data.get("email").strip()
    password = data.get("password").strip()

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@jwt.additional_claims_loader
def add_claims_to_access_token(user):
    return {
        "role": user.role,
        "email": user.email,
        "id": user.id,
        "emailVerified": user.email_verified,
    }


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "message")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)

        if form.email.data in Config.ADMIN_EMAILS:
            user.role = "admin"
        else:
            user.role = "user"
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("explore"))
    return render_template("register.html", title="Register", form=form)


@app.route("/api/register", methods=["POST"])
def register_api():

    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists with that email"}), 400

    try:
        user = User(email=email)
        user.set_password(password)
        access_token = create_access_token(identity=user)

        if email in Config.ADMIN_EMAILS:
            user.role = "admin"
        else:
            user.role = "user"

        send_verification_email(email)

        db.session.add(user)
        db.session.commit()
        return jsonify(access_token=access_token), 200

    except Exception as e:
        app.logger.exception(e)
        db.session.rollback()
        return jsonify({"message": "Error creating user"}), 500


@app.route("/api/change-password", methods=["POST"])
@jwt_required()
def change_password_api():
    user = jwt_current_user
    data = request.json
    old_password = data.get("currentPassword", "").strip()
    new_password = data.get("newPassword", "").strip()

    if not old_password or not new_password:
        return jsonify({"message": "Missing fields"}), 400

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({"message": "Incorrect password"}), 401

    try:
        user.set_password(new_password)
        db.session.commit()
    except Exception as e:
        app.logger.exception(e)
        db.session.rollback()
        return jsonify({"message": "Error changing password"}), 500
    return jsonify({"message": "Password changed successfully"}), 200


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


@app.route("/api/clear-recipe-list", methods=["POST"])
@jwt_required()
def clear_recipe_list_api():
    recipe_list = RecipeList.query.filter_by(user_id=get_jwt_identity()).all()
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


@app.route("/toggle-recipe-in-list/<int:recipe_id>")
@login_required
def toggle_recipe_in_recipe_list(recipe_id):
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


@app.route("/api/toggle-recipe-in-list/", methods=["POST"])
@jwt_required()
def toggle_recipe_in_recipe_list_api():
    user_id = get_jwt_identity()
    recipe_id = request.json["recipe_id"]
    recipe_list_item = RecipeList.query.filter_by(
        user_id=user_id, recipe_id=recipe_id
    ).first()
    if recipe_list_item:
        db.session.delete(recipe_list_item)
        # flash('Removed from recipe list.', 'success')
    else:
        print(f"Adding recipe {recipe_id} to list")
        recipe_list_item = RecipeList(user_id=user_id, recipe_id=recipe_id)
        db.session.add(recipe_list_item)
        # flash('Added to recipe list!', 'success')
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/toggle-favorite/<int:recipe_id>")
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


@app.route("/api/toggle-favorite/", methods=["POST"])
@jwt_required()
def toggle_favorite_api():
    user_id = get_jwt_identity()
    recipe_id = request.json["recipe_id"]

    favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if favorite:
        db.session.delete(favorite)
        # flash('Removed from favorites.', 'success')
    else:
        favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
        db.session.add(favorite)
        # flash('Added to favorites!', 'success')
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/api/get-favorites", methods=["GET"])
@jwt_required()
def get_favorites_api():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    recipes = []
    for favorite in favorites:
        recipe = favorite.recipe.to_dict()
        recipe["in_favorites"] = True
        recipes.append(recipe)
    return jsonify({"favorites": recipes})


@app.route("/api/get-cooked", methods=["GET"])
@jwt_required()
def get_cooked_api():
    user = jwt_current_user
    cooked = user.cooked_recipes

    # TODO: bad way to do this
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    favorites = [favorite.recipe for favorite in favorites]

    for recipe in cooked:
        recipe_list_item = RecipeList.query.filter_by(
            user_id=user.id, recipe_id=recipe.id
        ).first()

        if recipe_list_item:
            recipe.in_recipe_list = True
        else:
            recipe.in_recipe_list = False
        if recipe in favorites:
            recipe.in_favorites = True
        else:
            recipe.in_favorite = False

    return jsonify({"cooked": cooked})


@app.route("/saved")
@login_required
def saved():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorites = [favorite.recipe for favorite in favorites]
    for recipe in favorites:
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if recipe_list_item:
            recipe.in_recipe_list = True
        else:
            recipe.in_recipe_list = False
        recipe.in_favorites = True

    cooked = current_user.cooked_recipes
    for recipe in cooked:
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()

        if recipe_list_item:
            recipe.in_recipe_list = True
        else:
            recipe.in_recipe_list = False
        if recipe in favorites:
            recipe.in_favorites = True
        else:
            recipe.in_favorite = False

    return render_template("saved.html", favorites=favorites, cooked=cooked)


@app.route("/recipe-list")
@login_required
def recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    recipes = []
    for recipe_list_item in recipe_list:

        recipe = recipe_list_item.recipe
        recipe.in_recipe_list = True
        favorite_item = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        recipes.append(recipe.to_dict())
    return render_template("recipe_list.html", recipes=recipes)


@app.route("/api/recipe-list")
@jwt_required()
def recipe_list_api():

    recipes = jwt_current_user.get_recipe_list(as_json=True)

    return jsonify({"recipes": recipes}), 200


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


# @app.route("/generate-meal-plan", methods=["GET"])
# @login_required
# def generate_meal_plan():
# raise NotImplementedError("deprecated")
# today = datetime.date.today()
# app.logger.info("Generating meal plan")
# filename = f"Cheffrey Meal Plan {today.strftime('%b %d')}"

# recipe_list_items = RecipeList.query.filter_by(user_id=current_user.id).all()

# recipe_list = [
#     HashableRecipe(recipe_item.recipe) for recipe_item in recipe_list_items
# ]

# recipe_list = tuple(recipe_list)

# shopping_list = recipes_to_shopping_list(recipe_list)

# meal_plan_html = create_meal_plan_html(shopping_list, recipe_list)

# response = Response(meal_plan_html, content_type="text/html")

# response.headers["Content-Disposition"] = f"attachment; filename={filename}.html"
# app.logger.info("Done generating meal plan")
# return response


@app.route("/api/get-shopping-list", methods=["GET"])
@jwt_required()
def shopping_list_api():
    # TODO: ugly
    with open("data/ingredient2category.json", "r") as f:
        ingredient2category = json.load(f)

    recipes = jwt_current_user.get_recipe_list(as_json=True)

    ingredient_dict = {}

    n_ingredients = 0
    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            category = ingredient2category.get(ingredient, "Other")
            ingredient_dict[category] = ingredient_dict.get(category, []) + [ingredient]
            n_ingredients += 1

    # Sort ingredient_dict by category, with "Other" category last
    ingredient_dict = dict(
        sorted(ingredient_dict.items(), key=lambda x: (x[0] == "Other", x[0]))
    )

    return jsonify(ingredient_dict)


@app.route("/shopping-list")
@login_required
def shopping_list():
    # TODO: ugly
    with open("data/ingredient2category.json", "r") as f:
        ingredient2category = json.load(f)

    recipes = current_user.get_recipe_list(as_json=True)

    ingredient_dict = {}

    n_ingredients = 0
    for recipe in recipes:
        for ingredient in recipe.ingredients:
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


@app.route("/api/search-recipes/", methods=["POST"])
@jwt_required(optional=True)
def search_api():

    per_page = 6  # Adjust as needed

    query = request.json["query"]
    page = request.json.get("page", None)

    if ("search_recipes" not in session) or (query != session["search_query"]):
        recipes = Recipe.query.filter(
            ((Recipe.is_public == True) | (Recipe.user_id == jwt_current_user.id))
            & (Recipe.title.ilike(f"%{query}%"))
        ).all()
        session["search_query"] = query

    recipes = session["search_recipes"]
    if page is not None:
        start_idx = per_page * (page - 1)
        if start_idx > len(recipes):
            return jsonify({"recipes": []})
        recipes = recipes[start_idx : per_page * page]

    recipes = jwt_current_user.tag_recipes(recipes, as_json=True)

    return jsonify({"recipes": recipes})


@app.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("q")

    recipes = Recipe.query.filter(
        ((Recipe.is_public == True) | (Recipe.user_id == current_user.id))
        & (Recipe.title.ilike(f"%{query}%"))
    ).all()

    for recipe in recipes:
        recipe_list_item = RecipeList.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if recipe_list_item:
            recipe.in_recipe_list = True
        else:
            recipe.in_recipe_list = False
        favorite_item = Favorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe.id
        ).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False

    return render_template("search.html", recipes=recipes, search_term=query)


def generate_email_verification_token(email):
    token = serializer.dumps(email, salt="email-verification")
    return token


def send_verification_email(email):

    token = generate_email_verification_token(email)
    mailer = MailBot()

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "Email not found"}), 404

    subject = "Cheffrey: Verify Your Email"
    url = url_for("app.verify_email", token=token, _external=True)
    body = f"Click the following link to verify your email: {url}"

    mailer.send_email(subject, body, email)

    return True


@app.route("/api/send-verification-email", methods=["GET"])
@jwt_required()
def send_verification_email_route():
    # check if email is already verified
    if current_user.email_verified:
        return jsonify({"message": "Email already verified"}), 200

    email = current_user.email
    try:
        send_verification_email(email)
    except Exception as e:
        # logger.error(f"Error sending verification email: {e}")
        return jsonify({"error": "Error sending verification email"}), 500

    return jsonify({"message": "Verification email sent"}), 200


@app.route("/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    try:
        email = serializer.loads(token, salt="email-verification", max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"error": "Email not found"}), 404
        if user.email_verified:
            return jsonify({"message": "Email already verified"}), 200
        user.email_verified = True
        db.session.commit()
        return jsonify({"message": "Email verified"}), 200
    except Exception as e:
        # logger.exception("Unable to verify email")

        return jsonify({"error": "Unable to verify email"}), 400


@app.route("/api/forgot-password", methods=["POST"])
def send_forget_password_email():
    data = request.json
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not found"}), 404

    current_expiration = user.can_change_password_expiry
    if current_expiration is not None:
        if current_expiration > datetime.datetime.utcnow():
            return (
                jsonify(
                    {
                        "error": "There is already an active verification code. Please use that code or wait to generate a new one."
                    }
                ),
                400,
            )

    token = str(random.randint(100000, 999999))
    mailer = MailBot()
    subject = "Cheffrey: Reset Your Password"
    body = f"Use the following code to reset your password: {token}"
    try:
        mailer.send_email(subject, body, email)
    except Exception as e:
        app.logger.error(f"Error sending forget password email: {e}")
        return jsonify({"error": "Error sending forget password email"}), 500

    try:
        user.can_change_password = True
        user.can_change_password_expiry = (
            datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        )
        user.change_password_code = token
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating user: {e}")
        return jsonify({"error": "Error updating user"}), 500

    return jsonify({"message": "Forget password email sent"}), 200


@app.route("/api/change-forgot-password", methods=["POST"])
def change_forgot_password():
    data = request.json
    code = data.get("verificationCode", "").strip()
    new_password = data.get("newPassword", "").strip()
    email = data.get("email", "").strip()

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.can_change_password:
        return jsonify({"error": "Change password code expired"}), 400

    if user.can_change_password_expiry < datetime.datetime.utcnow():
        return jsonify({"error": "Change password code expired"}), 400

    if user.change_password_code != code:
        app.logger.debug(code)
        app.logger.debug(user.change_password_code)
        return jsonify({"error": "Invalid code"}), 400

    try:
        user.set_password(new_password)
        user.can_change_password = False
        user.can_change_password_expiry = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error changing password"}), 500


@app.route("/api/cookbook", methods=["GET"])
@jwt_required()
def cookbook():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    recipes = user.get_cookbook(as_json=True)

    return jsonify({"recipes": recipes}), 200


@app.route("/api/add-to-cookbook/", methods=["POST"])
@jwt_required()
def add_to_cookbook():
    user_id = get_jwt_identity()
    recipe_id = request.json.get("recipe_id")

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    cookbook_item = CookBook(user_id=user_id, recipe_id=recipe_id)
    db.session.add(cookbook_item)
    db.session.commit()

    return jsonify({"message": "Recipe added to cookbook"}), 200


@app.route("/api/remove-from-cookbook/", methods=["POST"])
@jwt_required()
def remove_from_cookbook():
    user_id = get_jwt_identity()
    recipe_id = request.json.get("recipe_id")

    cookbook_item = CookBook.query.filter_by(
        user_id=user_id, recipe_id=recipe_id
    ).first()
    if not cookbook_item:
        return jsonify({"error": "Recipe not found in cookbook"}), 404

    db.session.delete(cookbook_item)
    db.session.commit()

    return jsonify({"message": "Recipe removed from cookbook"}), 200


@app.route("/api/toggle-in-cookbook/", methods=["POST"])
@jwt_required()
def toggle_in_cookbook():
    user_id = get_jwt_identity()
    recipe_id = request.json.get("recipe_id")

    cookbook_item = CookBook.query.filter_by(
        user_id=user_id, recipe_id=recipe_id
    ).first()
    if cookbook_item:
        db.session.delete(cookbook_item)
        db.session.commit()
        return jsonify({"message": "Recipe removed from cookbook"}), 200
    else:
        cookbook_item = CookBook(user_id=user_id, recipe_id=recipe_id)
        db.session.add(cookbook_item)
        db.session.commit()
        return jsonify({"message": "Recipe added to cookbook"}), 200


@app.route("/api/create-recipe", methods=["POST"])
@jwt_required()
def create_recipe():
    user_id = get_jwt_identity()
    data = request.json

    data["author"] = user_id

    recipe_id = data.get("id")
    if recipe_id:
        recipe = Recipe.query.get(recipe_id)
        if recipe:
            return jsonify({"error": "Recipe already exists"}), 400

    if Recipe.query.filter_by(title=data["title"]).first():
        return jsonify({"error": "Recipe with that title already exists"}), 400
    try:
        recipe = Recipe(**data)
    except Exception as e:
        app.logger.exception(f"Error creating recipe: {e}")
        return jsonify({"error": "Error creating recipe"}), 500
    try:
        db.session.add(recipe)
        db.session.commit()
    except Exception as e:
        app.logger.exception(f"Error adding recipe to database: {e}")
        db.session.rollback()
        return jsonify({"error": "Error adding recipe to database"}), 500

    return jsonify({"message": "Recipe added successfully", "id": recipe.id}), 200


@app.route("/api/update-recipe", methods=["POST"])
@jwt_required()
def update_recipe():
    user_id = get_jwt_identity()
    data = request.json

    recipe_id = data.get("id")
    if not recipe_id:
        return jsonify({"error": "Recipe ID not provided"}), 400

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    if recipe.author != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        recipe.update(data)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error updating recipe: {e}")
        db.session.rollback()
        return jsonify({"error": "Error updating recipe"}), 500

    return jsonify({"message": "Recipe updated successfully"}), 200


@app.route("/api/extract-recipe-info/", methods=["POST"])
@jwt_required()
def extract_recipe():

    image_encodings = request.json.get("image_encodings")

    if not image_encodings:
        return jsonify({"error": "No image provided"}), 400

    recipe_reader = RecipeReader(image_encodings=image_encodings)
    recipe_info = recipe_reader.extract_info()

    recipe_info = recipe_info[recipe_info.find("{") : recipe_info.rfind("}") + 1]

    try:
        recipe_info = json.loads(recipe_info)
    except Exception as e:
        app.logger.exception(f"Error parsing recipe info: {e}")
        return jsonify({"error": "Error parsing recipe info"}), 500

    return jsonify(recipe_info), 200
