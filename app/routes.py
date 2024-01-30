from flask import flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlalchemy as sa
from config import Config
from sqlalchemy.exc import IntegrityError

from app import app, db

from datetime import datetime, timezone, timedelta
from random import randint
from urllib.parse import urlsplit

from app.models import User, Recipe, RecipeList, Favorite
from app.forms import LoginForm, RegistrationForm, SettingsForm
from sqlalchemy.sql import func  # Import the func function

import random



limiter = Limiter(app = app, key_func=get_remote_address)

@app.before_request
def before_request():
    pass
        
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    random_recipes = Recipe.query.filter(Recipe.description != None).order_by(func.random()).limit(5).all()
    print(random_recipes)
    return render_template('home.html', recipes = random_recipes)



@app.route('/login', methods=['POST', 'GET'])
@limiter.limit("5 per 5 seconds")  # Adjust the limit as needed
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
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
        return redirect(url_for('home'))
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