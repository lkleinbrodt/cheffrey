import streamlit as st
st.set_page_config(
    page_title='Cheffrey',
    page_icon=None,
    layout="wide",
)


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css(ROOT_DIR/"style.css")
import datetime
today = datetime.date.today
from datetime import datetime
from cheffrey import *

stime = datetime.now()

import state
import display

from my_logger import create_logger
logger = create_logger('app')


##################
# App
##################

# Initialize Session
state.initialize_state()

###
# Display:

logger.info(f"Showing: {st.session_state['page']}")

meal_plan_title = 'Meal Plan'
if len(st.session_state['recipe_list']) == 0:
    meal_plan_title += ' (Empty)'
elif len(st.session_state['recipe_list']) == 1:
    meal_plan_title += f" (1 Recipe)"
else:
    meal_plan_title += f" ({len(st.session_state['recipe_list'])} Recipes)"
    


def search_for_recipes():
    st.session_state['recommendation_source'] = 'searched'
    n = 3
    recipes = search_recipes(
        query = st.session_state['searchbar'],
        annoy_index = st.session_state['annoy_index'],
        embedding_model = st.session_state['embedding_model'],
        recipe_id_to_title=st.session_state['recipe_id_to_title'],
        n = 50
    )

    st.session_state['searched_recipes'] = [
        st.session_state['master_recipes'][recipe]
        for recipe in recipes
    ]


    st.session_state['recommended_recipes'] = st.session_state['searched_recipes'][:n]
    st.session_state['searched_index'] = n

def refresh_search():
    st.session_state['recommendation_source'] = 'searched'
    n = len(st.session_state['recommended_recipes'])

    new_index = st.session_state['searched_index'] + n
    new_recipes = st.session_state['searched_recipes'][st.session_state['searched_index']: new_index]
    st.session_state['searched_index'] = new_index
    st.session_state['recommended_recipes'] = new_recipes

def recommend_random():
    st.session_state['recommendation_source'] = 'random'
    st.session_state['recommended_recipes'] = pick_recipes_randomly(st.session_state['cookbook'], 3)


if st.session_state['page'] == 'main':
    build_tab, meal_plan_tab = st.tabs(['Add Recipes', meal_plan_title])

    with build_tab:
        title_cols = st.columns([3, 1.5, 1.5])

        title_cols[0].subheader("What do you feel like cooking?")
        # title_cols[1].button("Submit a recipe",on_click=state.update_page, args=('submit',))

        search_cols = st.columns([4, 2, 2])
        search = search_cols[0].text_input(
            label = 'Search',
            placeholder = "Search (Ex. Easy weeknight dinners with mushrooms...)",
            help = "Enter a search query and we'll find recipes that match. You can search by name, type, vibe, etc. Treat this like google!",
            key = 'searchbar',
            on_change=search_for_recipes,
            label_visibility='collapsed'
        )

        if len(st.session_state['searched_recipes']) > 0:
            search_cols[1].button(
                label = ':arrows_counterclockwise:',
                on_click=refresh_search,
                help='Get 3 new recipes based on your search'
            )

        feeling_lucky = search_cols[2].button(
            label = 'Surprise me!',
            on_click=recommend_random,
            help = 'Have cheffrey recommend 3 random recipes'
        )

        if len(st.session_state['recommended_recipes']) == 0:
            pass
            # st.info('Search for recipes or ask Cheffrey to surprise you.')
        else:
            display.search_results(st.session_state['recommended_recipes'])

        
        logger.info('Done populating grid')

        def create_meal_plan(recipe_list):

            def sort_by_first(x):
                s = x.split(' ')
                if len(s) > 1:
                    return s[1][0]
                else:
                    return x[0]

            all_ingredients = sorted([item for recipe in recipe_list for item in recipe['ingredients']], key = sort_by_first)
            shopping_list = all_ingredients

            meal_plan = {'Recipes': recipe_list, 'Shopping List': shopping_list}

            html = create_meal_plan_html(meal_plan)
            # with open('./meal_plan.html', 'w') as f:
            #     f.write(html)

            return html
        



    with meal_plan_tab:
        header_cols = st.columns([4, 3, 4])
        if len(st.session_state['recipe_list']) > 0:
            meal_plan_html = create_meal_plan(st.session_state['recipe_list'])
            with header_cols[1]:
                st.download_button(
                    label='Download Meal Plan',
                    data=meal_plan_html, 
                    file_name=f'Cheffrey Meal Plan {today().strftime("%B %d")}.html', mime='text/html',
                )
        display.meal_plan()

if st.session_state['page'] == 'recipe_info':
    recipe = st.session_state['active_recipe']

    st.button('Back', key = 'back_1', on_click = state.update_page, args=('main', ))
    
    st.markdown(
        create_recipe_html(recipe, standalone=True),
        True
    )

    st.button('Back', key = 'back_2', on_click = state.update_page, args=('main', ))



if st.session_state['page'] == 'submit':
    t, b = st.columns([5, 1])
    t.title('Submit a New Recipe')
    b.button('Back to main page', on_click=state.update_page, args=('main',))
    # TODO: how does a user submit a recipe?
    url_to_download = st.text_input(
        "Enter the URL of the recipe:", on_change=state.download_recipe, key='url_to_download')

    st.button('Click here to enter one manually:',
              on_click=state.update_page, args=('manual_submit',))

if st.session_state['page'] == 'edit recipe':
    recipe = st.session_state['submitted_recipe']

    st.header("Here's your recipe:")
    st.title(recipe['Title'])
    if recipe['Image']:
        st.image(recipe['Image'])
    st.header('Ingredients:')
    st.write('\n'.join([f for f in recipe['ingredients']]))
    st.header('Instructions:')
    st.write(recipe['Instructions'])

    st.header('Add Tags')

    recipe_tags = st.multiselect(
        "Tags:",
        options=st.session_state['available_tags'],
        default=None
    )
    st.text_input('Create new tag:', on_change=state.add_tag, key='new_tag')

    recipe['Tags'] = recipe_tags

    st.button('Submit Recipe:', on_click=state.store_recipe, args=(recipe,))


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

        st.button("Looks right to me!", on_click=state.update_page, args=('submit',))

    st.button('Submit and Review', on_click=state.submit_recipe, args=(recipe,))

etime = datetime.now()
elapsed = etime - stime
logger.info(f'Fully Refreshed in: {elapsed}')
