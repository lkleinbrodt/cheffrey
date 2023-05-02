import streamlit as st

st.set_page_config(page_title="Cheffrey", page_icon=None, layout="wide")
import itertools
import logging
from datetime import datetime
from math import ceil, floor
from cheffrey import *
from recipe_scrapers import scrape_me as scrape_recipe
import spacy
from PIL import Image
import requests
from io import BytesIO

logging.basicConfig(
    level=logging.DEBUG,
    format=" %(asctime)s - $(levelname)s - $(message)s",
    filemode="w",
)
logger = logging.getLogger(__name__)
logger.info("Start of program")
stime = datetime.now()


def update_page(page_name):
    """
    Update the current page in the Streamlit application.

    Keyword arguments:
    page_name -- name of the page to switch to.

    Sets the value of 'page' key in the session_state dictionary to the provided page_name.
    """

    logger.info(f"Switching page to: {page_name}")
    st.session_state["page"] = page_name


def switch_to_recipe_info_page(i):
    """Switch to recipe info page for a specific recipe.

    Args:
    i (int): Index of the recipe to be displayed among session state stored recipe_list.

    Returns:
    None

    Side Effects:
    The active recipe for the session state is updated to the selected recipe and the logger records the recipe being displayed.
    The page is redirected to 'recipe_info'."""

    st.session_state["active_recipe"] = st.session_state["recipe_list"][i]
    logger.info(f"Getting more info on {st.session_state['active_recipe']['Title']}")
    update_page("recipe_info")


def add_tag():
    """
    Adds a new tag from st.session_state['new_tag'] to the list of current available tags in st.session_state['available_tags'].

    This function takes no arguments. It retrieves the value of the 'new_tag' key in the current session_state and appends it to the 'available_tags' list.
    """

    st.session_state["available_tags"] += [st.session_state["new_tag"]]


def submit_recipe(recipe):
    """Submit a recipe and store it in the session state.

    Args:
        recipe (dict): A dictionary containing the recipe information, including Ingredients.

    Returns:
        None"""

    logger.info("Submitting recipe")
    if len(recipe["Ingredients"]) == 0:
        st.warning("Make sure to enter ingredients")
        st.stop()
    st.session_state["submitted_recipe"] = recipe
    st.session_state["page"] = "edit recipe"


def store_recipe(recipe):
    """Store a recipe by adding it to the recipe file and updating the session state.

    Args:
        recipe (dict): A dictionary containing the details of the recipe, including its title and ingredients.

    Returns:
        None

    Raises:
        Nothing is raised from this function.

    Notes:
        The recipe will overwrite an existing recipe with the same title in the recipe file.
    """

    add_to_recipe_file(recipe, overwrite=True)
    st.session_state["master_recipes"][recipe["Title"]] = recipe
    st.session_state["page"] = "submit"


def download_recipe():
    """Downloads a recipe and submits it for storing or displays it to the user for confirmation if already exists. It logs the action of recipe download in the logger and retrieves the URL to download from the session state. If URL string is empty, an exception is raised. It scrapes recipe data from the given URL and parses the scraped recipe data. It then adds URL of the recipe to the dictionary of parsed recipe data. The function checks if the recipe's Title is already in the 'master_recipes' dictionary in the session state. If recipe already exists, it displays current saved information plus newly downloaded recipe to user for confirmation. It has 'Looks right to me' button and 'Wrong, replace this recipe' button for user to confirm. Submits the recipe data if user confirms that they are correct."""

    logger.info("Downloading recipe")
    url_to_download = st.session_state["url_to_download"]
    if url_to_download == "":
        st.stop("enter a valid url silly!")
    recipe = scrape_recipe(url_to_download)
    recipe = parse_scraped_recipe(recipe)
    recipe["URL"] = url_to_download
    if recipe["Title"] in st.session_state["master_recipes"].keys():
        existing_recipe = st.session_state["master_recipes"][recipe["Title"]]
        st.write("We already have that recipe loaded, does this look right?")
        st.write(recipe["Title"])
        st.write(existing_recipe["Ingredients"])
        st.write(existing_recipe["Instructions"])
        st.button("Looks right to me!", on_click=update_page, args=("submit",))
        st.button("Wrong, replace this recipe", on_click=submit_recipe, args=recipe)
    else:
        submit_recipe(recipe)


def regen_recipe(i, cookbook, method):
    """
    Regenerates a given recipe based on the specified method.

        Args:
            i (int): Index representing which recipe needs to be regenerated.
            cookbook (Cookbook): Object representing the cookbook containing the recipes.
            method (str): Regeneration method to use, one of 'random', 'searched'.

        Returns:
            None: If the searched value is an empty space.
            Updated recipe list in session state with the new recipe.

        Raises:
            ValueError: If an unrecognized regeneration method is provided."""

    if method == "random":
        new_recipe = pick_recipes_randomly(cookbook, 1)[0]
    elif method == "searched":
        searched_value = st.session_state[f"search_{i}"]
        if searched_value == " ":
            return
        new_recipe = cookbook.recipes[searched_value]
    else:
        raise ValueError(f"Unrecognized method: {method}")
    st.session_state["recipe_list"][i] = new_recipe


def remove_recipe(i):
    """
    Remove recipe at index i from the recipe list stored in the `session_state` dictionary. This function updates the recipe list by removing the recipe at index i.

    Args:
        i (int): Integer value of the index of the recipe to be removed.

    Returns:
        None

    Side effects:
        This function updates the recipe list stored in the session_state dictionary of the application, by removing the recipe at index i.

    Constraints:
        - The stored recipe list must be non-empty, meaning removing a recipe will result in a non-empty list.
        - The index i must be between 0 and the length of recipe list, exclusive."""

    recipes = st.session_state["recipe_list"]
    if i == 0:
        st.session_state["recipe_list"] = recipes[1:]
    elif i == len(recipes):
        st.session_state["recipe_list"] = recipes[:i]
    else:
        st.session_state["recipe_list"] = recipes[:i] + recipes[i + 1 :]


def add_recipe(cookbook, method="random"):
    """Add a recipe to the cookbook according to a certain method.

    Keyword arguments:
    cookbook -- an instance of the Cookbook class representing the cookbook
    method -- either random or searched (default is random)

    If method is random, a recipe that hasn't been added to the recipe list is randomly picked from cookbook
    If method is searched, the recipe with the key 'searched_value' is added to the recipe list
    A ValueError is raised if the method is not recognized.
    """

    if method == "random":
        recipes = st.session_state["recipe_list"]
        picked_recipes = [r["Title"] for r in recipes]
        available_recipes = {
            i: v for (i, v) in cookbook.recipes.items() if i not in picked_recipes
        }
        if len(available_recipes) == 0:
            available_recipes = cookbook.recipes
        cookbook.recipes = available_recipes
        new_recipe = pick_recipes_randomly(cookbook, 1)[0]
    elif method == "searched":
        searched_value = st.session_state[f"searchbar"]
        if searched_value == " ":
            return
        new_recipe = cookbook.recipes[searched_value]
    else:
        raise ValueError(
            f"Unrecognized method: {method}. Must be either random or searched"
        )
    st.session_state["recipe_list"] += [new_recipe]


import re


def send_meal_plan(meal_plan):
    """Sends a meal plan to the user via text message.

    Keyword arguments:
    meal_plan -- a string containing the meal plan information to be sent

    Checks the validity of the phone number in the session state. Phone numbers should only contain digits and hyphens and must have 10 digits for sending SMS. The `meal_plan` is then sent to the user via the `text_meal_plan` function. If a problem occurs while sending the meal plan by text message, an error message is logged.

    Returns False if the phone number is invalid or incomplete."""

    num = st.session_state["phone_number"]
    if bool(re.search("[^0-9-]", num)):
        st.warning("Phone numbers should only contain numbers and hyphens")
        return False
    num = re.sub("[^0-9]+", "", num)
    if len(num) != 10:
        st.warning("Phone number must have 10 digits")
        return False
    try:
        text_meal_plan(phone_number=num, meal_plan=meal_plan)
    except Exception as e:
        logger.error(e)
        st.warning("Sorry. failed to text you")


def load_config():
    """
    Load configuration and master recipes from file and S3.

    Returns:
        tuple: Configuration and master recipes tuple. Configuration loaded from `config.yaml` and master recipes loaded from S3.

    Side Effects:
        Calls `logger` to log an information message: "Loading config and master recipes".

    Raises:
        None

    PEP 8:
        Function names should be lowercase, with words separated by underscores.
        `load_config()` is consistent with PEP 8 naming conventions."""

    logger.info("Loading config and master recipes")
    cfg = load_yaml("config")
    master_recipes = load_s3_recipes()
    return (cfg, master_recipes)


if "master_recipes" not in st.session_state.keys():
    (cfg, original_master_recipes) = load_config()
    st.session_state["master_recipes"] = original_master_recipes
if "page" not in st.session_state.keys():
    st.session_state["page"] = "main"
if "recipe_list" not in st.session_state.keys():
    st.session_state["recipe_list"] = []
if "meal_plan_html" not in st.session_state.keys():
    st.session_state["meal_plan_html"] = ""
if "nlp" not in st.session_state.keys():
    st.session_state["nlp"] = spacy.load("en_core_web_sm")
if "available_tags" not in st.session_state.keys():
    base_tags = ["breakfast", "lunch", "dinner"]
    try:
        existing_tags = list(
            itertools.chain.from_iterable(
                [
                    st.session_state["master_recipes"][name]["Tags"]
                    for name in st.session_state["master_recipes"].keys()
                ]
            )
        )
        tags = list(set(base_tags + existing_tags))
    except TypeError:
        tags = base_tags
    st.session_state["available_tags"] = tags
nlp = st.session_state["nlp"]
logger.info(f"Showing: {st.session_state['page']}")
if st.session_state["page"] == "main":
    title_cols = st.columns([3, 1.5, 1.5])
    title_cols[0].subheader("Let's get cooking")
    title_cols[1].button("Submit a recipe", on_click=update_page, args=("submit",))
    with st.expander(label="How to use Cheffrey", expanded=False):
        st.markdown(
            "\n        <ul>\n        <li>Browse Cheffrey's suggestions for what to eat this week.</li>\n        <li>Explore more information about each dish or read the full recipe.</li>\n        <li>You can replace any dish with a new suggestion or search for one yourself.</li>\n        <li>When you're ready, download all the recipes as well as a shopping list with all the ingredients!</li>\n        </ul>\n        ",
            unsafe_allow_html=True,
        )
    st.write("---")
    cookbook = Cookbook("master", recipe_dict=st.session_state["master_recipes"])
    if len(st.session_state["recipe_list"]) == 0:
        logger.info("Initializing Recipes")
        recipe_list = pick_recipes_randomly(cookbook, 4)
        st.session_state["recipe_list"] = recipe_list
    else:
        recipe_list = st.session_state["recipe_list"]

    def display_recipe_image(recipe, shape=(300, 200)):
        r = requests.get(recipe["Image"])
        image = Image.open(BytesIO(r.content))
        new_image = image.resize(shape)
        st.image(new_image, use_column_width="always")

    def list_presentation(recipe_list):
        logger.info("creating recipe list")

        def list_item(i, recipe):
            st.markdown(
                f"""<h4 style="text-align:center">{recipe['Title']}</h4>""",
                unsafe_allow_html=True,
            )
            cols = st.columns([3, 2.5, 1.25, 1])
            with cols[0]:
                display_recipe_image(recipe, shape=(300, 200))
            with cols[1]:
                with st.expander(label="More info:", expanded=False):
                    st.markdown(
                        f"\n                        <div class='row'>\n                            <div class='col'><ul>{''.join(['<li>' + r + '</li>' for r in recipe['Ingredients']])}</ul></div>\n                            <div class='col'>Yield: {recipe['Yield']}. Time: {recipe['Time']}</div>\n                        </div>\n                        ",
                        unsafe_allow_html=True,
                    )
                st.button(
                    label="Full Recipe",
                    key=f"recipe_info_{i}",
                    on_click=switch_to_recipe_info_page,
                    args=(i,),
                )
            with cols[2]:
                st.button(
                    label="Pick again",
                    key=f"regen_{i}",
                    on_click=regen_recipe,
                    args=(i, cookbook, "random"),
                )
            with cols[3]:
                st.button(
                    label="Remove", key=f"delete_{i}", on_click=remove_recipe, args=(i,)
                )
            st.write("---")

        for i, recipe in enumerate(recipe_list):
            list_item(i, recipe)
        st.button("+1 Recipe", on_click=add_recipe, args=(cookbook,))
        search_options = [" "] + list(cookbook.recipes.keys())
        st.selectbox(
            label="Search for a recipe",
            key=f"searchbar",
            options=search_options,
            on_change=add_recipe,
            args=(cookbook, "searched"),
        )

    list_presentation(recipe_list)

    def grid_presentation(recipe_list):
        n_cols = min([len(recipe_list), 3])
        n_rows = ceil(len(recipe_list) / n_cols)
        if n_cols * n_rows == len(recipe_list):
            n_rows += 1

        def make_grid(n_cols, n_rows):
            grid = [0] * n_rows
            for i in range(n_rows):
                with st.container():
                    grid[i] = st.columns(n_cols)
            return grid

        logger.info("making grid")
        recipe_grid = make_grid(n_cols, n_rows)
        logger.info("done making grid")

        def grid_square(i, recipe):
            row_idx = floor(i / n_cols)
            col_idx = i % n_cols
            with recipe_grid[row_idx][col_idx]:
                st.markdown(
                    f"""<h4 style="text-align:center">{recipe['Title']}</h4>""",
                    unsafe_allow_html=True,
                )
                display_recipe_image(recipe)
                with st.expander(label="ingredients", expanded=False):
                    st.markdown(
                        f"\n                    <div class='row'>\n                        <div class='col'><ul>{''.join(['<li>' + r + '</li>' for r in recipe['Ingredients']])}</ul></div>\n                        <div class='col'>Yield: {recipe['Yield']}. Time: {recipe['Time']}</div>\n                    </div>\n                    ",
                        unsafe_allow_html=True,
                    )
                st.button(
                    label="Pick Again",
                    key=f"regen_{i}",
                    on_click=regen_recipe,
                    args=(i, cookbook, "random"),
                )
                search_options = [" "] + list(cookbook.recipes.keys())
                st.selectbox(
                    label="Search",
                    key=f"search_{i}",
                    options=search_options,
                    on_change=regen_recipe,
                    args=(i, cookbook, "searched"),
                )
                st.button(
                    label="Remove", key=f"delete_{i}", on_click=remove_recipe, args=(i,)
                )

        logger.info("Populating grid")
        for i, recipe in enumerate(recipe_list):
            grid_square(i, recipe)
        i += 1
        row_idx = floor(i / n_cols)
        col_idx = i % n_cols
        with recipe_grid[row_idx][col_idx]:
            for _ in range(10):
                st.text("")
            st.button("+1 Recipe", on_click=add_recipe, args=(cookbook,))

    logger.info("Done populating grid")

    def create_meal_plan(recipe_list):
        shopping_list = create_shopping_list(recipe_list, nlp)
        meal_plan = {"Recipes": recipe_list, "Shopping List": shopping_list}
        html = create_meal_plan_html(meal_plan)
        return html

    meal_plan_html = create_meal_plan(recipe_list)
    with title_cols[2]:
        st.download_button(
            label="Download Meal Plan",
            data=meal_plan_html,
            file_name="meal_plan.html",
            mime="text/html",
        )
    st.download_button(
        label="Download Meal Plan",
        key="download_meal_plan_2",
        data=meal_plan_html,
        file_name="meal_plan.html",
        mime="text/html",
    )
if st.session_state["page"] == "recipe_info":
    recipe = st.session_state["active_recipe"]
    st.button("Back", key="back_1", on_click=update_page, args=("main",))
    st.markdown(create_recipe_html(recipe, standalone=True), True)
    st.button("Back", key="back_2", on_click=update_page, args=("main",))
if st.session_state["page"] == "submit":
    (t, b) = st.columns([5, 1])
    t.title("Submit a New Recipe")
    b.button("Back to main page", on_click=update_page, args=("main",))
    url_to_download = st.text_input(
        "Enter the URL of the recipe:", on_change=download_recipe, key="url_to_download"
    )
    st.button(
        "Click here to enter one manually:",
        on_click=update_page,
        args=("manual_submit",),
    )
if st.session_state["page"] == "edit recipe":
    recipe = st.session_state["submitted_recipe"]
    st.header("Here's your recipe:")
    st.title(recipe["Title"])
    if recipe["Image"]:
        st.image(recipe["Image"])
    st.header("Ingredients:")
    st.write("\n".join([f for f in recipe["Ingredients"]]))
    st.header("Instructions:")
    st.write(recipe["Instructions"])
    st.header("Add Tags")
    recipe_tags = st.multiselect(
        "Tags:", options=st.session_state["available_tags"], default=None
    )
    st.text_input("Create new tag:", on_change=add_tag, key="new_tag")
    recipe["Tags"] = recipe_tags
    st.button("Submit Recipe:", on_click=store_recipe, args=(recipe,))
if st.session_state["page"] == "manual_submit":
    st.title("Submitting recipe")
    submit_cols = st.columns(2)
    name = submit_cols[0].text_input("What's the name of the dish?")
    instructions = submit_cols[1].text_input("Instructions:")
    n_ingredients = int(
        st.number_input("How many ingredients?", min_value=1, step=1, value=5)
    )
    ingredients = []
    for i in range(n_ingredients):
        ingredients.append(
            st.text_input(f"Ingredient {i + 1}", key=f"ingredient_{i + 1}")
        )
    ingredients = [ing for ing in ingredients if ing != ""]
    recipe = {
        "Title": name,
        "Time": None,
        "Yield": None,
        "Ingredients": ingredients,
        "Instructions": instructions,
        "Image": None,
        "URL": None,
        "Tags": None,
    }
    if recipe["Title"] in st.session_state["master_recipes"].keys():
        existing_recipe = st.session_state["master_recipes"][recipe["Title"]]
        st.write("We already have that recipe loaded, does this look right?")
        st.write(recipe["Title"])
        st.write(existing_recipe["Ingredients"])
        st.write(existing_recipe["Instructions"])
        st.button("Looks right to me!", on_click=update_page, args=("submit",))
    st.button("Submit and Review", on_click=submit_recipe, args=(recipe,))
etime = datetime.now()
elapsed = etime - stime
logger.info(f"Fully Refreshed in: {elapsed}")
