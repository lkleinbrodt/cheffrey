from flask import flash, redirect, render_template, request, url_for, session, jsonify, Response
from flask_login import current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlalchemy as sa
from config import Config
from sqlalchemy.exc import IntegrityError
from app.src import recipes_to_shopping_list, create_meal_plan_html, HashableRecipe
from app import app, db, admin
import json

from urllib.parse import urlsplit

from app.models import User, Recipe, RecipeList, Favorite
from app.forms import LoginForm, RegistrationForm, SettingsForm
import datetime
from sqlalchemy.sql import func  # Import the func function

limiter = Limiter(app = app, key_func=get_remote_address)

@app.before_request
def before_request():
    pass
        
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    return render_template('index.html')

@app.route('/explore')
@login_required
def explore():
    return render_template('explore.html')

@app.route('/refresh-explore', methods=['GET'])
@login_required
def refresh_explore():
    session.pop('explore_recipes', None)
    return jsonify({'status': 'success'})

@app.route('/load-more-recipes/<int:page>')
@login_required
def load_more_recipes(page):
    per_page = 6  # Adjust as needed
    max_pages = 10
    
    if 'explore_recipes' not in session:
        recipes = Recipe.query.order_by(func.random()).limit(per_page*max_pages)
        session['explore_recipes'] = [recipe.to_dict() for recipe in recipes]
        # recipes = Recipe.query.paginate(page=page, per_page=per_page, error_out=False).items
    
    recipes = session['explore_recipes'][per_page * (page - 1):per_page * page]
    recipes = [Recipe.from_dict(recipe) for recipe in recipes]

    ##TODO: improve
    for recipe in recipes:
        #TODO: make a decision regarding eval here vs eval in to_dict and just using a dict here
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        favorite_item = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        
    #TODO: improve
    
    return render_template('recipe_partial.html', recipes=recipes)

@app.route('/login', methods=['POST', 'GET'])
@limiter.limit("5 per 5 seconds")  # Adjust the limit as needed
def login():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember = form.remember_me.data)
        
        next_page = request.args.get('next')
        #if there is no next, no problem
        #if there is a next, make sure it's a relative path, otherwise redirect to index
            #this is to prevent a malicious user from inserting a URL to a malicious site
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'message')
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember = True)
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for('explore'))
    return render_template('register.html', title='Register', form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'GET':
        form = SettingsForm(
            phone_number = current_user.phone_number,
        )
    elif request.method == 'POST':
        form = SettingsForm(request.form)
        
    
    if request.method == 'POST' and form.validate_on_submit():
        # Update user settings in the database
        user = User.query.filter_by(id=current_user.id).first()

        user.phone_number = form.phone_number.data

        try:
            db.session.commit()
            flash('Settings successfully updated.', 'success')
            redirect(url_for('settings'))
        except IntegrityError:
            db.session.rollback()
            flash('Error saving settings. Please try again.', 'error')
            return redirect(url_for('settings'))

    return render_template('settings.html', settings_form=form)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

@app.route('/add-to-favorites/<int:recipe_id>')
@login_required
def add_to_favorites(recipe_id):
    favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    try:
        db.session.add(favorite)
        db.session.commit()
        # flash('Added to favorites!', 'success')
        return jsonify({'status': 'success'})
    except IntegrityError:
        db.session.rollback()
        # flash('Error adding to favorites. Please try again.', 'error')
        return jsonify({'status': 'error'})
    
@app.route('/remove-from-favorites/<int:recipe_id>')
@login_required
def remove_from_favorites(recipe_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    try:
        db.session.delete(favorite)
        db.session.commit()
        # flash('Removed from favorites.', 'success')
    except:
        db.session.rollback()
        # flash('Error removing from favorites. Please try again.', 'error')
    return jsonify({'status': 'success'})

@app.route('/add-to-recipe-list/<int:recipe_id>')
@login_required
def add_to_recipe_list(recipe_id):
    
    
    recipe_list_item = RecipeList(user_id=current_user.id, recipe_id=recipe_id)
    try:
        db.session.add(recipe_list_item)
        db.session.commit()
        # flash('Added to recipe list!', 'success')
        return jsonify({'status': 'success'})
    except IntegrityError:
        db.session.rollback()
        # flash('Error adding to recipe list. Please try again.', 'error')
        return jsonify({'status': 'error'})

@app.route('/remove-from-recipe-list/<int:recipe_id>')
@login_required
def remove_from_recipe_list(recipe_id):
    recipe_list_item = RecipeList.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    try:
        db.session.delete(recipe_list_item)
        db.session.commit()
        # flash('Removed from recipe list.', 'success')
    except:
        db.session.rollback()
        # flash('Error removing from recipe list. Please try again.', 'error')
    return jsonify({'status': 'success'})

@app.route('/clear-recipe-list')
@login_required
def clear_recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    for recipe_list_item in recipe_list:
        db.session.delete(recipe_list_item)
    db.session.commit()
    return redirect(url_for('recipe_list'))

@app.route('/toggle-recipe-in-list/<int:recipe_id>')
@login_required
def toggle_recipe_in_list(recipe_id):
    recipe_list_item = RecipeList.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if recipe_list_item:
        db.session.delete(recipe_list_item)
        # flash('Removed from recipe list.', 'success')
    else:
        recipe_list_item = RecipeList(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(recipe_list_item)
        # flash('Added to recipe list!', 'success')
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/toggle-favorite/<int:recipe_id>')
@login_required
def toggle_favorite(recipe_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if favorite:
        db.session.delete(favorite)
        # flash('Removed from favorites.', 'success')
    else:
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        # flash('Added to favorites!', 'success')
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/favorites')
@login_required
def favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    recipes = [favorite.recipe for favorite in favorites]
    for recipe in recipes:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        recipe.in_favorites = True
    return render_template('favorites.html', recipes=recipes)

@app.route('/recipe-list')
@login_required
def recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    recipes = []
    for recipe_list_item in recipe_list:
        
        recipe = recipe_list_item.recipe
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe.in_list = True
        favorite_item = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        recipes.append(recipe)
    return render_template('recipe_list.html', recipes=recipes)

@app.route('/load-meal-plan')
@login_required
def load_meal_plan():
    return render_template('meal_plan_loading.html')
    

@app.route('/generate-meal-plan', methods=['GET'])
@login_required
def generate_meal_plan():
    today = datetime.date.today()
    app.logger.info('Generating meal plan')
    filename = f"Cheffrey Meal Plan {today.strftime('%b %d')}"
    
    recipe_list_items = RecipeList.query.filter_by(user_id=current_user.id).all()
    
    recipe_list = [HashableRecipe(recipe_item.recipe) for recipe_item in recipe_list_items]
    
    for recipe in recipe_list:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)

    recipe_list = tuple(recipe_list)

    shopping_list = recipes_to_shopping_list(recipe_list)

    meal_plan_html = create_meal_plan_html(shopping_list, recipe_list)

    response = Response(meal_plan_html, content_type='text/html')
    
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.html"
    app.logger.info('Done generating meal plan')
    return response

@app.route('/shopping-list')
@login_required
def shopping_list():
    #TODO: ugly
    with open('data/ingredient2category.json', 'r') as f:
        ingredient2category = json.load(f)
        
    recipe_list_items = RecipeList.query.filter_by(user_id=current_user.id).all()
    
    recipe_list = [HashableRecipe(recipe_item.recipe) for recipe_item in recipe_list_items]
    
    ingredient_dict = {}
    
    n_ingredients = 0
    for recipe in recipe_list:
        for ingredient in eval(recipe.ingredients):
            category = ingredient2category.get(ingredient, 'Other')
            ingredient_dict[category] = ingredient_dict.get(category, []) + [ingredient]
            n_ingredients += 1
    
    # Sort ingredient_dict by category, with "Other" category last
    ingredient_dict = dict(sorted(ingredient_dict.items(), key=lambda x: (x[0] == 'Other', x[0])))
    
            
    
            
    dict_list = [{}, {}, {}]
    running_dict = {}
    limit = (n_ingredients / 3)
    ingredient_counter = 0
    dict_counter = 0
    for category, ingredients in ingredient_dict.items():
        running_dict[category] = ingredients
        ingredient_counter += len(ingredients)
        dict_list[dict_counter] = running_dict
        if (ingredient_counter > limit) & (dict_counter < 2):
            running_dict = {}
            ingredient_counter = 0
            dict_counter += 1
    print(ingredient_dict)
    return render_template('shopping_list.html', ingredient_dict1=dict_list[0], ingredient_dict2=dict_list[1], ingredient_dict3=dict_list[2])
    
@app.route('/test')
def test():
    return render_template('test.html')

@app.route("/favicon.ico")
def favicon():
    return url_for('static', filename='data:,')

@app.route('/get-recipe-list-count', methods=['GET'])
@login_required
def get_recipe_list_count():
    #TODO: which ones better?
    # count = len(current_user.recipe_list)
    count = len(RecipeList.query.filter_by(user_id=current_user.id).all())
    return jsonify({'count': count})

@app.route('/get-recipe-list', methods=['GET'])
@login_required
def get_recipe_list():
    recipe_list = RecipeList.query.filter_by(user_id=current_user.id).all()
    recipes = []
    for recipe_list_item in recipe_list:
        recipe = recipe_list_item.recipe
        favorite_item = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        recipe.in_list = True
        recipes.append(recipe)
    return jsonify({'recipes': recipes})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    recipes = Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()
    
    for recipe in recipes:
        recipe.ingredient_list = eval(recipe.ingredients)
        recipe.instruction_list = eval(recipe.instructions_list)
        recipe_list_item = RecipeList.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if recipe_list_item:
            recipe.in_list = True
        else:
            recipe.in_list = False
        favorite_item = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first()
        if favorite_item:
            recipe.in_favorites = True
        else:
            recipe.in_favorites = False
        
        
    return render_template('search.html', recipes=recipes, search_term=query)