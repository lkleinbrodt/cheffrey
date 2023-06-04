import requests
import streamlit as st
from PIL import Image
from io import BytesIO
import state


def recipe_image(recipe, shape=(300, 200)):
    r = requests.get(recipe["image"])
    image = Image.open(BytesIO(r.content))
    new_image = image.resize(shape)
    st.image(new_image, use_column_width="always")


def how_to():
    with st.expander(label="How to use Cheffrey", expanded=False):
        st.markdown(
            """
    <ul>
    <li>Browse Cheffrey's suggestions for what to eat this week.</li>
    <li>Explore more information about each dish or read the full recipe.</li>
    <li>You can replace any dish with a new suggestion or search for one yourself.</li>
    <li>When you're ready, download all the recipes as well as a shopping list with all the ingredients!</li>
    </ul>
    """,
            unsafe_allow_html=True,
        )


def search_results(recipe_list):
    n = 3
    title_cols = st.columns(n)
    title_placeholders = []
    for i, recipe in enumerate(recipe_list[:n]):
        title_placeholders += [title_cols[i].empty()]
        
    image_cols = st.columns(n)
    for i, recipe in enumerate(recipe_list[:n]):
        with image_cols[i]:
            recipe_image(recipe)
        title_placeholders[i].markdown(
            f"""<h4 style="text-align:center; position:aboslute; bottom:0px;">{recipe['title']}</h4>""", unsafe_allow_html=True
        )
    info_cols = st.columns(n)
    for i, recipe in enumerate(recipe_list[:n]):
        with info_cols[i]:
            # with st.expander(label='More info:', expanded=False):
            #         st.markdown(f"""
            #         <div class='row'>
            #             <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['ingredients']])}</ul></div>
            #             <div class='col'>Yield: {recipe.get('yields', None)}. Time: {recipe['total_time']}</div>
            #         </div>
            #         """, unsafe_allow_html=True)
            
            st.button(
                label = 'Add to meal plan',
                key = f'add_{i}',
                on_click = state.add_to_meal_plan, args = (recipe, i),
                type = 'primary'
            )

            st.button(
                label = 'See full recipe',
                key = f'recipe_info_{i}',
                on_click = state.switch_to_recipe_info_page, args = (recipe, ),
                type = 'secondary'
            )

            
def meal_plan():
    def list_item(i, recipe):
        # st.header(recipe['Title'])
        st.markdown(
                f"""<h4 style="text-align:center">{recipe['title']}</h4>""", unsafe_allow_html=True)
        cols = st.columns([3, 3, 1, 1])

        with cols[0]:
            recipe_image(recipe, shape = (300, 200))
        
        with cols[1]:
            # with st.expander(label='More info:', expanded=False):
            #         st.markdown(f"""
            #         <div class='row'>
            #             <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['ingredients']])}</ul></div>
            #             <div class='col'>Yield: {recipe.get('yields', None)}. Time: {recipe['total_time']}</div>
            #         </div>
            #         """, unsafe_allow_html=True)
            
            st.button(
                label = 'See full recipe',
                key = f'meal_plan_info_{i}',
                on_click = state.switch_to_recipe_info_page, args = (recipe, )
            )

        with cols[3]:
            st.button(
                label='Remove', key=f'delete_{i}',
                on_click=state.remove_recipe, args=(i,)
            )

        st.write('---')
    
    for i, recipe in enumerate(st.session_state['recipe_list']):
        list_item(i, recipe)





def list_presentation(recipe_list):
    # logger.info('creating recipe list')

    def list_item(i, recipe):
        # st.header(recipe['Title'])
        st.markdown(
                f"""<h4 style="text-align:center">{recipe['title']}</h4>""", unsafe_allow_html=True)
        cols = st.columns([3, 3, 1, 1])

        with cols[0]:
            recipe_image(recipe, shape = (300, 200))
        
        with cols[1]:
            with st.expander(label='More info:', expanded=False):
                    st.markdown(f"""
                    <div class='row'>
                        <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['ingredients']])}</ul></div>
                        <div class='col'>Yield: {recipe.get('yields', None)}. Time: {recipe['total_time']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.button(
                label = 'Full Recipe',
                key = f'recipe_info_{i}',
                on_click = state.switch_to_recipe_info_page, args = (i, )
            )
        
        with cols[2]:
            st.button(
                label='Refresh', key=f'regen_{i}',
                on_click=state.regen_recipe, args=(i, 'random')
            )
            

        with cols[3]:
            st.button(
                label='Remove', key=f'delete_{i}',
                on_click=state.remove_recipe, args=(i,)
            )

        st.write('---')

    for i, recipe in enumerate(recipe_list):
        list_item(i, recipe)

    st.button('+1 Recipe', on_click=state.add_recipe)

    search_options = [' '] + list(st.session_state['cookbook'].recipes.keys())

    # st.selectbox(
    #     label='Search for a recipe',
    #     key=f'searchbar',
    #     options=search_options,
    #     on_change=state.add_recipe,
    #     args=('searched',)
    # )

from math import ceil, floor

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

    # logger.info('making grid')
    recipe_grid = make_grid(n_cols, n_rows)
    # logger.info('done making grid')

    def grid_square(i, recipe):
        row_idx = floor(i / n_cols)
        col_idx = i % n_cols
        with recipe_grid[row_idx][col_idx]:
            st.markdown(
                f"""<h4 style="text-align:center">{recipe['title']}</h4>""", unsafe_allow_html=True)

            recipe_image(recipe)

            with st.expander(label='ingredients', expanded=False):
                st.markdown(f"""
                <div class='row'>
                    <div class='col'><ul>{''.join(['<li>'+r+'</li>' for r in recipe['ingredients']])}</ul></div>
                    <div class='col'>Yield: {recipe['yields']}. Time: {recipe['total_time']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.button(
                label='Pick Again', key=f'regen_{i}',
                on_click=state.regen_recipe, args=(i, 'random')
            )
            search_options = [' '] + list(st.session_state['cookbook'].recipes.keys())
            st.selectbox(
                label='Search',
                key=f'search_{i}',
                options=search_options,
                on_change=state.regen_recipe,
                args=(i, 'searched')
            )

            st.button(
                label='Remove', key=f'delete_{i}',
                on_click=state.remove_recipe, args=(i,)
            )

    # logger.info('Populating grid')
    for i, recipe in enumerate(recipe_list):
        grid_square(i, recipe)
    
    i += 1
    row_idx = floor(i / n_cols)
    col_idx = i % n_cols
    with recipe_grid[row_idx][col_idx]:
        for _ in range(10):
            st.text('')
        st.button('+1 Recipe', on_click=state.add_recipe)