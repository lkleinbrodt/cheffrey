
import streamlit as st
from src.cheffrey import *
import pandas as pd
import yaml
import logging
import itertools
logging.basicConfig(level = logging.DEBUG, format = ' %(asctime)s - $(levelname)s - $(message)s', filemode = 'w')
logger = logging.getLogger(__name__)
logger.debug('Start of program')

def load_config():
    cfg = load_yaml('config')
    master_recipes = load_yaml('recipes')
    return cfg, master_recipes
cfg, original_master_recipes = load_config()

if 'master_recipes' not in st.session_state.keys():
    st.session_state['master_recipes'] = original_master_recipes
if 'page' not in st.session_state.keys():
    st.session_state['page'] = 'main'

logger.info(f"Showing: {st.session_state['page']}")

if 'available_tags' not in st.session_state.keys():
    base_tags = ['breakfast', 'lunch', 'dinner']
    try:
        existing_tags = list(itertools.chain.from_iterable([st.session_state['master_recipes'][name]['Tags'] for name in st.session_state['master_recipes'].keys()]))
        tags = list(set(base_tags + existing_tags))
    except TypeError:
        tags = base_tags

    st.session_state['available_tags'] = tags

def update_page(page_name):
    logger.info(f'Switching page to: {page_name}')
    st.session_state['page'] = page_name

if st.session_state['page'] == 'main':
    title_cols = st.columns([3,1])

    title_cols[0].title("Howdy! I'm Cheffrey")

    title_cols[1].button("Click here to submit a recipe", on_click=update_page, args=('submit',))

    # st.selectbox(
    #     "Who's recipes are we using today?",
    #     options = ['Erin', 'Landon', 'Both'],
    #     index = 2,
    #     key = 'user'
    # )

    #in future, we want to be able to request a certain amount of each type

    n_recipes = int(st.number_input(
        'How many recipes are we making?',
        min_value = 1, max_value = None,
    ))

    st.session_state['request'] = n_recipes

    ### Read in relevant cookbook
    #TODO: this should be read from the cookbook database

    cookbook = Cookbook('master', recipe_dict = st.session_state['master_recipes'])

    #TODO: Create Recipe List

    recipe_list = pick_recipes_randomly(cookbook, n_recipes)

    #TODO: Determine Shopping List

    shopping_list = create_shopping_list(recipe_list)

    #TODO: Create Meal Plan 

    meal_plan = {'Recipes': recipe_list, 'Shopping List': shopping_list}

    #TODO: Serve Meal plan

    st.header("Heres what you'll be cooking this week:")

    for recipe in meal_plan['Recipes']:
        st.subheader(recipe['Title'])
        st.write(f"Time: {recipe['Time']}")
        st.write(f"Tags: {recipe['Tags']}")
        st.image(recipe['Image'])

    st.header("And here's your shopping list:")

    st.write(shopping_list)

    #TODO: Allow for editing of plan

    #TODO: and Regenerating 

    #TODO: Export

def submit_recipe(recipe):
    logger.info('Submitting recipe')
    st.session_state['submitted_recipe'] = recipe
    st.session_state['page'] = 'edit recipe'

def store_recipe(recipe):
    add_to_recipe_file(recipe, overwrite = True) #we already checked if one exists
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
    #TODO: check to see if we already have that recipe
    if recipe['Title'] in st.session_state['master_recipes'].keys():
        existing_recipe = st.session_state['master_recipes'][recipe['Title']]
        st.write("We already have that recipe loaded, does this look right?")
        st.write(recipe['Title'])
        st.write(existing_recipe['Ingredients'])
        st.write(existing_recipe['Instructions'])

        st.button("Looks right to me!", on_click=update_page, args=('main',))
        st.button("Wrong, replace this recipe", on_click=submit_recipe, args = (recipe))
    else:
        submit_recipe(recipe)
    

if st.session_state['page'] == 'submit':
    t,b= st.columns([5,1])
    t.title('Submit a New Recipe')
    b.button('Back to main page', on_click=update_page, args=('main',))
    #TODO: how does a user submit a recipe?
    url_to_download = st.text_input("Enter the URL of the recipe:", on_change=download_recipe, key = 'url_to_download')

    st.button('Click here to enter one manually:', on_click=update_page, args=('manual_submit',))
        #TODO: if we do have that recipe:
            #
            #TODO: show the recipe
            #TODO: allow user to overwrite that recipe
        #TODO: if we don't ahve that recipe
            #TODO: download it using the scraper
            #TODO: show results to user for confirmation + tagging
            #TODO: if confirmed:
                #TODO: store the results in the database
            #TODO: else:
                #TODO: allow for editing

def add_tag():
    st.session_state['available_tags'] += [st.session_state['new_tag']]

if st.session_state['page'] == 'edit recipe':
    recipe = st.session_state['submitted_recipe']
    
    st.header("Here's your recipe:")
    st.title(recipe['Title'])
    st.image(recipe['Image'])
    st.header('Ingredients:')
    st.write('\n'.join([f for f in recipe['Ingredients']]))
    st.header('Instructions:')
    st.write(recipe['Instructions'])


    st.header('Add Tags')
    
    recipe_tags = st.multiselect(
        "Tags:",
        options=st.session_state['available_tags'],
        default = None
    )
    st.text_input('Create new tag:', on_change=add_tag, key='new_tag')

    recipe['Tags'] = recipe_tags

    st.button('Submit Recipe:', on_click=store_recipe, args=(recipe,))


if st.session_state['page'] == 'manually_submit':
    st.warning('Sorry, not implemented yet!')
    # with st.form(key = 'submit_recipe_form'):
    #         n_max_ingredients = 50
    #         ingredients = []
    #         amounts = []
    #         submit_cols = st.columns(3)
    #         name = submit_cols[0].text_input("What's the name of the dish?")
    #         instructions = submit_cols[0].text_input("Instructions:")
    #         tags = submit_cols[0].text_input("Tags:")
    #         #TODO: tags should be a list of existing tags, with the option of adding a new one

    #         for i in range(n_max_ingredients):
    #             submit_cols[0].text_input(f"Ingredient {i}", key = f"ingredient_{i}")
    #             ingredients.append()
    #             submit_cols[1].text_input(f"Amount:")
            
    #         submit = st.form_submit_button('Submit Recipe:')

    #         if submit:
    #             #TODO: parse and validate ingredients
    #             ingredients = [ing for ing in ingredients if ing != '']
    #             amounts = [amt for amt in amounts if amt != '']
                
    #             if len(ingredients) == 0:
    #                 st.warning('Make sure to enter ingredients')
    #                 st.stop()
    #             if len(ingredients) == 0:
    #                 st.warning('Make sure to enter amounts')
    #                 st.stop()
                

    #             #recipe_df = pd.DataFrame({"Ingredient" = ingredients})
    #             #TODO: parse name, instructions, tags
    #             #TODO: combine into one document
    #             #TODO: store