
import streamlit as st
from src.cheffrey import *
import pandas as pd

import logging
logging.basicConfig(level = logging.DEBUG, format = ' %(asctime)s - $(levelname)s - $(message)s', filemode = 'w')
logging.debug('Start of program')

if 'page' not in st.session_state.keys():
    st.session_state['page'] = 'main'

if st.session_state['page'] == 'main':
    title_cols = st.beta_columns([3,1])

    title_cols[0].title("Howdy! I'm Cheffrey")

    if title_cols[1].button("Click here to submit a recipe"):
        st.session_state['page'] = 'submit recipe'

st.selectbox(
    "Who's recipes are we using today?",
    options = ['Erin', 'Landon', 'Both'],
    index = 2,
    key = 'user'
)

#in future, we want to be able to request a certain amount of each type

n_recipes = int(st.number_input(
    'How many recipes are we making?',
    min_value = 1, max_value = None,
))

st.session_state['request'] = n_recipes

### Read in relevant cookbook
#TODO: this should be read from the cookbook database

cookbook = random_cookbook()

#TODO: Create Recipe List

recipe_list = pick_recipes_randomly(cookbook, n_recipes)

#TODO: Determine Shopping List

shopping_list = create_shopping_list(recipe_list)

#TODO: Create Meal Plan 

meal_plan = {'Recipes': recipe_list, 'Shopping List': shopping_list}

#TODO: Serve Meal plan

st.header("Heres what you'll be cooking this week:")
st.write([str(recipe) for recipe in meal_plan['Recipes']])

st.header("And here's your shopping list:")

shopping_df = pd.DataFrame([{'Ingredient': ingredient.element.name, 'Amount': ingredient.amount.value, 'Unit': str(ingredient.amount.unit)} for ingredient in meal_plan['Shopping List'].values()])
print(shopping_df)
st.write(shopping_df)
#TODO: Allow for editing of plan

#TODO: and Regenerating 

#TODO: Export

if st.session_state['page'] == 'submit':
    #TODO: how does a user submit a recipe?
    pass

#TODO: there should be recipes, and meals, whch are collections of recipes