from config import Config
from urllib import request as ulreq
from PIL import ImageFile
from openai import OpenAI
from app.models import Recipe
from functools import lru_cache


def css_style():
    with open(Config.ROOT_DIR + "/app/static/meal_plan_style.css", "r") as f:
        x = f.read()
    return x


def char_to_price(n_chars):
    """estimates the price to embed this many chars using openai"""
    chars_per_token = 3.7
    n_tokens = n_chars / chars_per_token
    price_per_token = 0.001 / 1000
    price = price_per_token * n_tokens
    return price


# TODO: is this a bad hack or a good hack?
class HashableRecipe:
    def __init__(self, recipe: Recipe):
        self.id = recipe.id
        self.title = recipe.title
        self.author = recipe.author
        self.canonical_url = recipe.canonical_url
        self.category = recipe.category
        self.image_url = recipe.image_url
        self.ingredients = recipe.ingredients
        self.description = recipe.description
        self.instructions = recipe.instructions
        self.total_time = recipe.total_time
        self.yields = recipe.yields

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


def recipes_to_shopping_list(recipes: tuple[HashableRecipe]):
    shopping_list = []
    for recipe in recipes:
        shopping_list += recipe.ingredient_list

    return shopping_list


# @lru_cache(maxsize=32)
# def recipes_to_shopping_list(recipes: tuple[HashableRecipe]):
#     client = OpenAI()
#     ingredient_str = ''
#     for recipe in recipes:
#         ingredient_str += recipe.ingredients + '\n'

#     print('estimated price to create shopping list:', char_to_price(len(ingredient_str)))

#     completion = client.chat.completions.create(
#         model = 'gpt-3.5-turbo',
#         messages = [
#             {'role':'user',  'content': """
#              Condense the following list of ingredients into a shopping list.
#              Add the ingredients together and sum them correctly (for example if you see "1 cup of flour" and "2 cups of flour" you should sum them to "3 cups of flour").
#              Group similar ingredients together (for example, vegetables go together, spices go together, etc.)
#              Separate each line with a "\n".
#              Make sure not to leave out any ingredients and ensure to add them together properly to sum correctly.
#              Ingredients:
#             \n\n
#              """ + ingredient_str}
#         ]
#     )

#     shopping_list = completion.choices[0].message.content.split('\n')
#     return shopping_list


def create_meal_plan_html(shopping_list: list, recipes: tuple[HashableRecipe]):

    # <link rel="stylesheet" type="text/css" href="example.css" media=”screen” />
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style type="text/css" media="screen">
    {css_style()}
    </style>
    </head>
    <body>
    """

    html += """<h1 style='text-align:center'>Shopping List</h1>"""

    n_items = len(shopping_list)

    shop1 = shopping_list[: int(n_items / 2)]
    shop2 = shopping_list[int(n_items / 2) :]

    shop1_html = "".join(["<li>" + item + "</li>" for item in shop1])
    shop2_html = "".join(["<li>" + item + "</li>" for item in shop2])
    html += f"""
        <div class="row";>
            <div class="col"><ul>{shop1_html}</ul></div>
            <div class="col"><ul>{shop2_html}</ul></div>
        </div>
        """

    html += "<hr>"

    for recipe in recipes:
        html += create_recipe_html(recipe)

    html += """
    </body>
    </html>
    """
    return html


def getsizes(uri):
    # get image size (None if not known)
    with ulreq.urlopen(uri) as file:
        p = ImageFile.Parser()
        while 1:
            data = file.read(1024)
            if not data:
                break
            p.feed(data)
            if p.image:
                return p.image.size


def create_recipe_html(recipe, standalone=False):
    if standalone:
        html = ""
    else:
        html = "<div style='break-before:all'>"
        html += "<hr><hr>"
    html += f"""<h1 style='text-align:center'> {recipe.title}</h1>"""
    html += "<br>"

    image_size = getsizes(recipe.image_url)
    if image_size:
        image_width, image_height = image_size
        image_height /= image_width / 350
        image_width = 350

    html += f"""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <img 
            src='{recipe.image_url}'; 
            alt='{recipe.title}'; 
            width='{image_width}';
            height='{image_height}';
            class='center';
        >
    </div>
    """

    html += "</div>"

    ingredient_html = "<h2 style='text-align:center'> Ingredients: </h2>"
    ingredient_html += f"<p> Yields: {recipe.yields}</p>"
    ingredient_html += "<ul>"
    for ingredient in recipe.ingredient_list:
        ingredient_html += "<li>" + ingredient + "</li>"
    ingredient_html += "</ul>"

    instructions_html = "<h2 style='text-align:center'> Instructions: </h2>"
    instructions_html += "<ol>"
    instructions = recipe.instruction_list
    for instruction in instructions:
        instructions_html += "<li>" + instruction + "</li>"
    instructions_html += "</ol>"

    html += f"""
    <div class="row";>
        <div class="col left">{ingredient_html}</div>
        <div class="col right">{instructions_html}</div>
    </div>
    """

    return html
