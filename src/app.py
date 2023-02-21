import streamlit as st
st.set_page_config(
    page_title='Cheffrey',
    page_icon=None,
    layout="wide",
)

import itertools
import logging
from datetime import datetime
from math import ceil, floor
from cheffrey import *
import spacy

from PIL import Image
import requests
from io import BytesIO

logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - $(levelname)s - $(message)s', filemode='w')
logger = logging.getLogger(__name__)
logger.info('Start of program')
stime = datetime.now()
# Callbacks and Session State Functions

def update_page(page_name):
    logger.info(f'Switching page to: {page_name}')
    st.session_state['page'] = page_name

def switch_to_recipe_info_page(i):
    st.session_state['active_recipe'] = st.session_state['recipe_list'][i]
    logger.info(f"Getting more info on {st.session_state['active_recipe']['Title']}")
    update_page('recipe_info')

def add_tag():
    st.session_state['available_tags'] += [st.session_state['new_tag']]


def submit_recipe(recipe):
    logger.info('Submitting recipe')

    if len(recipe['Ingredients']) == 0:
        st.warning('Make sure to enter ingredients')
        st.stop()

    st.session_state['submitted_recipe'] = recipe
    st.session_state['page'] = 'edit recipe'


def store_recipe(recipe):
    # we already checked if one exists
    add_to_recipe_file(recipe, overwrite=True)
    st.session_state['master_recipes'][recipe['Title']] = recipe
    st.session_state['page'] = 'submit'


def download_recipe():
    logger.info('Downloading recipe')
    url_to_download = st.session_state['url_to_download']
    if url_to_download == '':
        st.stop('enter a valid url silly!')
    recipe = scrape_recipe(url_to_download)
    recipe = parse_scraped_recipe(recipe)
    recipe['URL'] = url_to_download

    if recipe['Title'] in st.session_state['master_recipes'].keys():
        existing_recipe = st.session_state['master_recipes'][recipe['Title']]
        st.write("We already have that recipe loaded, does this look right?")
        st.write(recipe['Title'])
        st.write(existing_recipe['Ingredients'])
        st.write(existing_recipe['Instructions'])

        st.button("Looks right to me!", on_click=update_page, args=('submit',))
        st.button("Wrong, replace this recipe",
                  on_click=submit_recipe, args=(recipe))
    else:
        submit_recipe(recipe)


def regen_recipe(i, cookbook, method):
    if method == 'random':
        new_recipe = pick_recipes_randomly(cookbook, 1)[0]
    elif method == 'searched':
        searched_value = st.session_state[f'search_{i}']
        if searched_value == ' ':
            return
        new_recipe = cookbook.recipes[searched_value]
    else:
        raise ValueError(f"Unrecognized method: {method}")
    st.session_state['recipe_list'][i] = new_recipe


def remove_recipe(i):
    recipes = st.session_state['recipe_list']
    if i == 0:
        st.session_state['recipe_list'] = recipes[1:]
    elif i == len(recipes):
        st.session_state['recipe_list'] = recipes[:i]
    else:
        st.session_state['recipe_list'] = recipes[:i] + recipes[i+1:]


def add_recipe(cookbook, method = 'random'):
    if method == 'random':
        recipes = st.session_state['recipe_list']
        picked_recipes = [r['Title'] for r in recipes]
        available_recipes = {
            i: v
            for i, v in cookbook.recipes.items()
            if i not in picked_recipes
        }
        if len(available_recipes) == 0:
            available_recipes = cookbook.recipes
        cookbook.recipes = available_recipes
        new_recipe = pick_recipes_randomly(cookbook, 1)[0]
    elif method == 'searched':
        searched_value = st.session_state[f'searchbar']
        if searched_value == ' ':
            return
        new_recipe = cookbook.recipes[searched_value]
    else:
        raise ValueError(f"Unrecognized method: {method}. Must be either random or searched")

    st.session_state['recipe_list'] += [new_recipe]

import re

def send_meal_plan(meal_plan):
    num = st.session_state['phone_number']
    if bool(re.search(r'[^0-9-]', num)):
        st.warning('Phone numbers should only contain numbers and hyphens')
        return False
    # Replace all non-numeric characters with an empty string
    num = re.sub(r'[^0-9]+', '', num)
    if len(num) != 10:
        st.warning('Phone number must have 10 digits')
        return False
    
    try:
        text_meal_plan(phone_number=num, meal_plan = meal_plan)
    except Exception as e:
        logger.error(e)
        st.warning('Sorry. failed to text you')
    

def load_config():
    logger.info('Loading config and master recipes')
    cfg = load_yaml('config')
    master_recipes = load_s3_recipes()
    return cfg, master_recipes


##################
# App
##################

# Initialize Session


if 'master_recipes' not in st.session_state.keys():
    cfg, original_master_recipes = load_config()
    st.session_state['master_recipes'] = original_master_recipes

if 'page' not in st.session_state.keys():
    st.session_state['page'] = 'main'
if 'recipe_list' not in st.session_state.keys():
    st.session_state['recipe_list'] = []
if 'meal_plan_html' not in st.session_state.keys():
    st.session_state['meal_plan_html'] = ''
if 'nlp' not in st.session_state.keys():
    st.session_state['nlp'] = spacy.load("en_core_web_sm")

if 'available_tags' not in st.session_state.keys():
    base_tags = ['breakfast', 'lunch', 'dinner']
    try:
        existing_tags = list(itertools.chain.from_iterable(
            [st.session_state['master_recipes'][name]['Tags'] for name in st.session_state['master_recipes'].keys()]))
        tags = list(set(base_tags + existing_tags))
    except TypeError:
        tags = base_tags

    st.session_state['available_tags'] = tags

nlp = st.session_state['nlp']
###
# Display:

logger.info(f"Showing: {st.session_state['page']}")

if st.session_state['page'] == 'main':
    title_cols = st.columns([3, 1.5, 1.5])

    # title_cols[0].header("Heres what you'll be cooking this week:")
    title_cols[0].subheader("Let's get cooking")
    title_cols[1].button("Submit a recipe",
                         on_click=update_page, args=('submit',))
    with st.expander(label = 'How to use Cheffrey', expanded = False):
        st.markdown("""
        <ul>
        <li>Browse Cheffrey's suggestions for what to eat this week.</li>
        <li>Explore more information about each dish or read the full recipe.</li>
        <li>You can replace any dish with a new suggestion, or search for one yourself.</li>
        <li>When ready, download all the recipes, as well as a shopping list of all the ingredients!</li>
        </ul>
        """, unsafe_allow_html = True)

    st.write('---')

    # st.selectbox(
    #     "Who's recipes are we using today?",
    #     options = ['Erin', 'Landon', 'Both'],
    #     index = 2,
    #     key = 'user'
    # )

    # in future, we want to be able to request a certain amount of each type

    # n_recipes = int(st.number_input(
    #     'How many recipes are we making?',
    #     min_value=1,
    #     max_value=None,
    #     value=4
    # ))

    # Read in relevant cookbook
    # TODO: this should be read from the cookbook database

    cookbook = Cookbook(
        'master',
        recipe_dict=st.session_state['master_recipes']
    )

    # TODO: Create Recipe List

    # def pick_recipes(cookbook, n_recipes):

    #     if st.session_state['recipe_list'] == []:
    #         recipe_list = pick_recipes_randomly(
    #             cookbook, n_recipes)
    #     elif len(st.session_state['recipe_list']) < n_recipes:
    #         available_recipes = cookbook.recipes
    #         picked_recipes = [r['Title']
    #                           for r in st.session_state['recipe_list']]
    #         available_recipes = {
    #             i: v for i, v in available_recipes.items() if i not in picked_recipes}
    #         n_needed = n_recipes - len(picked_recipes)
    #         if len(available_recipes) < n_needed:
    #             pass
    #         else:
    #             cookbook.recipes = available_recipes
    #         new_recipes = pick_recipes_randomly(
    #             cookbook, n_needed)
    #         recipe_list = st.session_state['recipe_list'] + new_recipes
    #     elif len(st.session_state['recipe_list']) > n_recipes:
    #         recipe_list = st.session_state['recipe_list'][:n_recipes]
    #     else:
    #         # list is same length as N, meaning we have just swapped one of the items,
    #         # no need to re-run
    #         recipe_list = st.session_state['recipe_list']

    #     st.session_state['recipe_list'] = recipe_list
    #     return recipe_list

    if len(st.session_state['recipe_list']) == 0:
        logger.info('Initializing Recipes')
        recipe_list = pick_recipes_randomly(cookbook, 4)
        st.session_state['recipe_list'] = recipe_list
    else:
        recipe_list = st.session_state['recipe_list']

    # TODO: Determine Shopping List
    
    # TODO: Create Meal Plan

    # TODO: Serve Meal plan

    def display_recipe_image(recipe, shape = (300, 200)):
        r = requests.get(recipe['Image'])
        image = Image.open(BytesIO(r.content))
        new_image = image.resize(shape)
        st.image(new_image, use_column_width='always')

    def list_presentation(recipe_list):
        logger.info('creating recipe list')

        def list_item(i, recipe):
            # st.header(recipe['Title'])
            st.markdown(
                    f"""<h4 style="text-align:center">{recipe['Title']}</h4>""", unsafe_allow_html=True)
            cols = st.columns([3, 3, 1, 1])

            with cols[0]:
                display_recipe_image(recipe, shape = (300, 200))
            
            with cols[1]:
                with st.expander(label='More info:', expanded=False):
                        st.markdown(f"""
                        <div class='row'>
                            <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['Ingredients']])}</ul></div>
                            <div class='col'>Yield: {recipe['Yield']}. Time: {recipe['Time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.button(
                    label = 'Full Recipe',
                    key = f'recipe_info_{i}',
                    on_click = switch_to_recipe_info_page, args = (i, )
                )
            
            with cols[2]:
                st.button(
                    label='Refresh', key=f'regen_{i}',
                    on_click=regen_recipe, args=(i, cookbook, 'random')
                )
                

            with cols[3]:
                st.button(
                    label='Remove', key=f'delete_{i}',
                    on_click=remove_recipe, args=(i,)
                )

            st.write('---')

        for i, recipe in enumerate(recipe_list):
            list_item(i, recipe)

        st.button('+1 Recipe', on_click=add_recipe, args=(cookbook,))

        search_options = [' '] + list(cookbook.recipes.keys())

        st.selectbox(
            label='Search for a recipe',
            key=f'searchbar',
            options=search_options,
            on_change=add_recipe,
            args=(i, cookbook, 'searched')
        )

    
    list_presentation(recipe_list)

    



    def grid_presentation(recipe_list):

        n_cols = min([len(recipe_list), 3])
        n_rows = ceil(len(recipe_list) / n_cols)

        if (n_cols * n_rows) == len(recipe_list):
            n_rows += 1

        def make_grid(n_cols, n_rows):
            grid = [0]*n_rows
            for i in range(n_rows):
                with st.container():
                    grid[i] = st.columns(n_cols)
            return grid

        logger.info('making grid')
        recipe_grid = make_grid(n_cols, n_rows)
        logger.info('done making grid')

        def grid_square(i, recipe):
            row_idx = floor(i / n_cols)
            col_idx = i % n_cols
            with recipe_grid[row_idx][col_idx]:
                st.markdown(
                    f"""<h4 style="text-align:center">{recipe['Title']}</h4>""", unsafe_allow_html=True)

                display_recipe_image(recipe)

                with st.expander(label='ingredients', expanded=False):
                    st.markdown(f"""
                    <div class='row'>
                        <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['Ingredients']])}</ul></div>
                        <div class='col'>Yield: {recipe['Yield']}. Time: {recipe['Time']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.button(
                    label='Pick Again', key=f'regen_{i}',
                    on_click=regen_recipe, args=(i, cookbook, 'random')
                )
                search_options = [' '] + list(cookbook.recipes.keys())
                st.selectbox(
                    label='Search',
                    key=f'search_{i}',
                    options=search_options,
                    on_change=regen_recipe,
                    args=(i, cookbook, 'searched')
                )

                st.button(
                    label='Remove', key=f'delete_{i}',
                    on_click=remove_recipe, args=(i,)
                )

        logger.info('Populating grid')
        for i, recipe in enumerate(recipe_list):
            grid_square(i, recipe)
        
        i += 1
        row_idx = floor(i / n_cols)
        col_idx = i % n_cols
        with recipe_grid[row_idx][col_idx]:
            for _ in range(10):
                st.text('')
            st.button('+1 Recipe', on_click=add_recipe, args=(cookbook,))

    logger.info('Done populating grid')
    # TODO: Allow for editing of plan

    # TODO: and Regenerating

    # TODO: Export

    def create_meal_plan(recipe_list):

        shopping_list = create_shopping_list(recipe_list, nlp)

        meal_plan = {'Recipes': recipe_list, 'Shopping List': shopping_list}

        html = create_meal_plan_html(meal_plan)
        # with open('./meal_plan.html', 'w') as f:
        #     f.write(html)

        return html
    
    meal_plan_html = create_meal_plan(recipe_list)

    with title_cols[2]:
        st.download_button(
            label='Download Meal Plan',
            data=meal_plan_html, 
            file_name='meal_plan.html', mime='text/html',
        )
        # st.text_input(
        #     label = 'Text me the meal plan', 
        #     key = 'phone_number',
        #     placeholder = 'Your phone #...', 
        #     on_change = send_meal_plan, args=(meal_plan_html, )
        # )

if st.session_state['page'] == 'recipe_info':
    recipe = st.session_state['active_recipe']

    st.button('Back', key = 'back_1', on_click = update_page, args=('main', ))
    
    st.markdown(
        create_recipe_html(recipe, standalone=True),
        True
    )

    st.button('Back', key = 'back_2', on_click = update_page, args=('main', ))



if st.session_state['page'] == 'submit':
    t, b = st.columns([5, 1])
    t.title('Submit a New Recipe')
    b.button('Back to main page', on_click=update_page, args=('main',))
    # TODO: how does a user submit a recipe?
    url_to_download = st.text_input(
        "Enter the URL of the recipe:", on_change=download_recipe, key='url_to_download')

    st.button('Click here to enter one manually:',
              on_click=update_page, args=('manual_submit',))

if st.session_state['page'] == 'edit recipe':
    recipe = st.session_state['submitted_recipe']

    st.header("Here's your recipe:")
    st.title(recipe['Title'])
    if recipe['Image']:
        st.image(recipe['Image'])
    st.header('Ingredients:')
    st.write('\n'.join([f for f in recipe['Ingredients']]))
    st.header('Instructions:')
    st.write(recipe['Instructions'])

    st.header('Add Tags')

    recipe_tags = st.multiselect(
        "Tags:",
        options=st.session_state['available_tags'],
        default=None
    )
    st.text_input('Create new tag:', on_change=add_tag, key='new_tag')

    recipe['Tags'] = recipe_tags

    st.button('Submit Recipe:', on_click=store_recipe, args=(recipe,))


if st.session_state['page'] == 'manual_submit':
    st.title('Submitting recipe')
    submit_cols = st.columns(2)
    name = submit_cols[0].text_input("What's the name of the dish?")
    instructions = submit_cols[1].text_input("Instructions:")

    n_ingredients = int(st.number_input(
        'How many ingredients?', min_value=1, step=1, value=5))

    ingredients = []

    for i in range(n_ingredients):
        ingredients.append(st.text_input(
            f"Ingredient {i+1}", key=f"ingredient_{i+1}"))

    ingredients = [ing for ing in ingredients if ing != '']

    recipe = {
        'Title': name,
        'Time': None,
        'Yield': None,
        'Ingredients': ingredients,
        'Instructions': instructions,
        'Image': None,
        'URL': None,
        'Tags': None
    }

    if recipe['Title'] in st.session_state['master_recipes'].keys():
        existing_recipe = st.session_state['master_recipes'][recipe['Title']]
        st.write("We already have that recipe loaded, does this look right?")
        st.write(recipe['Title'])
        st.write(existing_recipe['Ingredients'])
        st.write(existing_recipe['Instructions'])

        st.button("Looks right to me!", on_click=update_page, args=('submit',))

    st.button('Submit and Review', on_click=submit_recipe, args=(recipe,))

etime = datetime.now()
elapsed = etime - stime
logger.info(f'Fully Refreshed in: {elapsed}')
