import streamlit as st
from recipe_scrapers import scrape_me as scrape_recipe
import cheffrey
import itertools
from my_logger import create_logger
import gensim

logger = create_logger(__name__)

def initialize_state():
    if 'master_recipes' not in st.session_state.keys():
        original_master_recipes = cheffrey.load_local_recipes()
        st.session_state['master_recipes'] = original_master_recipes
        id_to_title = {
            recipe['uid']: recipe['title']
            for recipe in original_master_recipes.values()
        }
        st.session_state['recipe_id_to_title'] = id_to_title

        st.session_state['cookbook'] = cheffrey.Cookbook(
            'master',
            recipe_dict=st.session_state['master_recipes']
        )

    if 'page' not in st.session_state.keys():
        st.session_state['page'] = 'main'
    
    if 'recipe_list' not in st.session_state.keys():
        st.session_state['recipe_list'] = []
    
    if 'meal_plan_html' not in st.session_state.keys():
        st.session_state['meal_plan_html'] = ''

    if 'searched_recipes' not in st.session_state.keys():
        st.session_state['searched_recipes'] = []

    

    if 'available_tags' not in st.session_state.keys():
        base_tags = ['breakfast', 'lunch', 'dinner']
        try:
            existing_tags = list(itertools.chain.from_iterable(
                [st.session_state['master_recipes'][name]['tags'] for name in st.session_state['master_recipes'].keys()]))
            tags = list(set(base_tags + existing_tags))
        except KeyError:
            tags = base_tags

        st.session_state['available_tags'] = tags

    if 'embedding_model' not in st.session_state:
        st.session_state['embedding_model'] =  cheffrey.load_embedding_model()
    
    if 'selected_recipes' not in st.session_state:
        st.session_state['selected_recipes'] =  []

    if 'annoy_index' not in st.session_state.keys():
        st.session_state['annoy_index'] = cheffrey.load_annoy_index(st.session_state['embedding_model'].vector_size)

    if 'recommended_recipes' not in st.session_state:
        st.session_state['recommended_recipes'] = []
        
def add_to_meal_plan(recipe, i):
    #TODO: not great that terminology doesnt match
    #and that we need recipe and also index
    st.session_state['recipe_list'] += [recipe]
    regen_recipe(i)

def update_page(page_name):
    logger.info(f'Switching page to: {page_name}')
    st.session_state['page'] = page_name

def switch_to_recipe_info_page(recipe):
    st.session_state['active_recipe'] = recipe
    logger.info(f"Getting more info on {st.session_state['active_recipe']['title']}")
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
    cheffrey.add_to_recipe_file(recipe, overwrite=True)
    st.session_state['master_recipes'][recipe['Title']] = recipe
    st.session_state['page'] = 'submit'


def download_recipe():
    logger.info('Downloading recipe')
    url_to_download = st.session_state['url_to_download']
    if url_to_download == '':
        st.stop('enter a valid url silly!')
    recipe = scrape_recipe(url_to_download)
    recipe = cheffrey.parse_scraped_recipe(recipe)
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



def regen_recipe(i):
    source = st.session_state['recommendation_source']
    if source == 'random':
        new_recipe = cheffrey.pick_recipes_randomly(st.session_state['cookbook'], 1)[0]
    elif source == 'searched':
        new_recipe = st.session_state['searched_recipes'][st.session_state['searched_index']]
        st.session_state['searched_index'] += 1
    else:
        raise ValueError(f"Unrecognized source: {source}")
    st.session_state['recommended_recipes'][i] = new_recipe


def remove_recipe(i):
    recipes = st.session_state['recipe_list']
    if i == 0:
        st.session_state['recipe_list'] = recipes[1:]
    elif i == len(recipes):
        st.session_state['recipe_list'] = recipes[:i]
    else:
        st.session_state['recipe_list'] = recipes[:i] + recipes[i+1:]


def add_recipe(method = 'random'):
    cookbook = st.session_state['cookbook']
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
        new_recipe = cheffrey.pick_recipes_randomly(cookbook, 1)[0]
    elif method == 'searched':
        searched_value = st.session_state[f'searchbar']
        if searched_value == ' ':
            return
        new_recipe = cookbook.recipes[searched_value]
    else:
        raise ValueError(f"Unrecognized method: {method}. Must be either random or searched")

    st.session_state['recipe_list'] += [new_recipe]