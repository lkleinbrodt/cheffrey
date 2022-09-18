

"""
Storage system for recipes:
    Must have: 
        Holding recipes
        Adding recipes
        Retrieving recipes
        
Adding a recipe
    Parsing, 
    validation

Generate the menu
    ...
    features:
        
"""

from random import sample, randint, choice
from bisect import bisect
from fractions import Fraction
import itertools

from xhtml2pdf import pisa
from streamlit.state.session_state import Value
import src.sugarcube as sc
import logging
from recipe_scrapers import scrape_me as scrape_recipe
import yaml
import streamlit as st
logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - $(levelname)s - $(message)s', filemode='w')
logger = logging.getLogger(__name__)
logger.debug('Start of program')


def load_yaml(name):
    valid_names = ['config', 'recipes']
    if name in valid_names:
        with open(f"data/{name}.yaml", 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(
            f"Unrecognized name: {name}. Valid types are: {valid_names}")


def parse_scraped_recipe(recipe):
    d = {
        'Title': recipe.title(),
        'Time': recipe.total_time(),
        'Yield': recipe.yields(),
        'Ingredients': recipe.ingredients(),
        'Instructions': recipe.instructions(),
        'Image': recipe.image(),
        'Tags': None
    }
    return d


def add_to_recipe_file(recipe, overwrite=False):
    all_recipes = load_yaml('recipes')

    if (recipe['Title'] in all_recipes.keys()) & (overwrite == False):
        raise FileExistsError(
            f"{recipe.title()} already found in the file, and overwrite set to false")

    all_recipes[recipe['Title']] = recipe

    with open(f"data/recipes.yaml", 'w') as f:
        yaml.safe_dump(all_recipes, f)

# Yknow what. let's just build a simple version first
# No combining ingredients, just picking meals and pasting the ingredients together


class Ingredient(sc.Ingredient):

    def present(self):
        """
        Returns a human readable amount: 9 Quarts -> 2 Gallons 1 Quart
        It gets the highest unit where you're > 1, and then if necessary gives the remainder in terms of the next unit, rounded to one of the breakpoints
        """

        relevant_units = self.amount.unit.measure.units

        invalid_unit_names = [
            name for name in relevant_units.keys() if 'liter' in name]

        unit_list = [(unit, round(self.to(unit).amount.value, 3))
                     for unit in relevant_units.values() if unit.name not in invalid_unit_names]
        unit_list.sort(key=lambda x: x[1], reverse=True)

        whole_list = [(unit, value) for unit, value in unit_list if value >= 1]

        first = whole_list.pop()
        first_unit = first[0]
        first_value = int(first[1] - (first[1] % 1))
        remainder = first[1] % 1

        # Granularity down to the 1/8 of a unit
        cutoffs = [i/8 for i in range(9)]

        try:
            remainder = cutoffs[bisect(cutoffs, remainder)]
        except IndexError as err:
            logger.info(f"Remainder: {remainder}")
            logger.info(f"cutoffs: {cutoffs}")
            logger.info(f"bisect: {bisect(cutoffs, remainder)}")
            logger.info(err.args)
            raise

        if remainder > 0:
            remainder = Fraction(remainder)
            return f"{first_value} {remainder.numerator}/{remainder.denominator} {first_unit}s"
        else:
            return f"{first_value} {first_unit}s"

    def __add__(self, other):
        if isinstance(other, Ingredient):
            if self.element.name != other.element.name:
                raise TypeError(
                    f'Your trying to add ingredients that are different elements: {self.element.name} and {other.element.name}')

            return Ingredient(sc.Amount(self.amount.value + other.to(self.amount.unit).amount.value, self.amount.unit), self.element)

        elif isinstance(other, (int, float)):
            if self.element.is_int:
                assert (
                    other % 1) == 0, f"{self.element.name} is a whole ingredient, can only add whole numbers"
            return Ingredient(sc.Amount(self.amount.value + other, self.amount.unit), self.element)
        else:
            raise TypeError(
                f"Dont know how to add an ingredient and an object of type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            # Can you multiply 1 egg by 1.5? or should that be illegal? It might blow up scaling :/
            return Ingredient(sc.Amount(self.amount.value * other, self.amount.unit), self.element)
        else:
            raise TypeError(
                f"Dont know how to multiply an ingredient and an object of type {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def _from_strings(amount_str, element_str):
        logger.info(amount_str)
        logger.info(element_str)
        # Parse amount
        amount_list = str.split(amount_str)
        value = float(amount_list[0])
        if (value % 1) == 0:
            value = int(value)
        unit_str = ' '.join(amount_list[1:])

        matched = False
        for u in sc.Volume.units:
            if unit_str == u:
                unit = u
                matched = True
        for u in sc.Mass.units:
            if unit_str == u:
                unit = u
                matched = True
        for u in sc.Mass.units:
            if unit_str == u:
                unit = u
                matched = True
        if not matched:
            raise ValueError(f'Unrecognized unit: {unit_str}')

        if element_str not in known_elements.keys():
            raise ValueError(
                f"Unrecognized element: {element_str}, you might need to add it to the master list")

        element = known_elements[element_str]

        return Ingredient(sc.Amount(value, unit), element)


class Recipe(object):
    def __init__(self, name, ingredients, instructions=None):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

    def __str__(self) -> str:
        return f"Recipe for {self.name}: {self.ingredients}"


def yaml_to_recipe(recipe_name, recipe_dict):
    logger.info(recipe_dict)
    ingredients = {ingredient_name: Ingredient._from_strings(
        amount_str, ingredient_name) for ingredient_name, amount_str in recipe_dict['ingredients'].items()}
    return Recipe(recipe_name, ingredients, recipe_dict['instructions'])


class Cookbook(object):
    def __init__(self, title, recipe_dict):
        self.title = title
        self.recipes = recipe_dict
        #self.recipes = {name: yaml_to_recipe(name, rec) for name, rec in recipe_dict.items()}


# Populating Classes

def random_ingredient():
    i = randint(1, 10)

    unit = sc.Volume.units[choice(list(sc.Volume.units.keys()))]
    amount = sc.Amount(i, unit=unit)
    sample_elements = [sc.Element(f'Ingredient_{i}') for i in range(20)]
    element = sample(sample_elements, 1)[0]
    return Ingredient(amount, element)


def random_cookbook():

    instructions = 'Cook them up real nice'

    my_recipes = [Recipe(f'sammy_{i}', [random_ingredient()
                         for i in range(6)], instructions) for i in range(50)]
    my_cookbook = Cookbook("Lando's Cookbook")
    my_cookbook.recipes = my_recipes

    return my_cookbook
# Recipes are entered into an excel template sheet, I will format it so that it can be read in and parsed to this
# we can always bulk process into json format for faster read times



def pick_recipes_randomly(cookbook, n_recipes):
    recipes = sample(
        [recipe for recipe in cookbook.recipes.values()], k=n_recipes)
    return recipes


def create_shopping_list(recipe_list):
    ingredients = list(itertools.chain.from_iterable(
        [rec['Ingredients'] for rec in recipe_list]))
    return ingredients
# def create_shopping_list(recipes):
#     shopping_list = {}

#     ### Add Ingredients
#     for recipe in recipes:
#         for ingredient in recipe.ingredients:
#             if ingredient.element.name in shopping_list.keys():
#                 shopping_list[ingredient.element.name] += ingredient
#             else:
#                 shopping_list[ingredient.element.name] = ingredient

#     return shopping_list


def css_style():
    with open('./meal_plan_style.css', 'r') as f:
        x = f.read()
    return x


def create_meal_plan_html(meal_plan):
    shopping_list = meal_plan['Shopping List']
    recipes = meal_plan['Recipes']

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
    html += """<ul>"""

    for item in shopping_list:
        html += "<li>" + item + "</li>"
    html += "</ul>"
    html += "<hr>"

    for recipe in recipes:
        html += "<div style='break-before:all'>"
        html += "<hr><hr>"
        html += f"""<h1 style='text-align:center'> {recipe['Title']}</h1>"""
        html += "<br>"
        html += f"""
        <img 
            src='{recipe['Image']}'; 
            alt='{recipe['Title']}'; 
            class='center';
        >"""

        html += "</div>"

        ingredient_html = "<h2 style='text-align:center'> Ingredients: </h2>"
        ingredient_html += "<ul>"
        for ingredient in recipe['Ingredients']:
            ingredient_html += "<li>" + ingredient + "</li>"
        ingredient_html += "</ul>"

        instructions_html = "<h2 style='text-align:center'> Instructions: </h2>"
        instructions_html += "<p>"+recipe['Instructions']+"</p>"
        html += f"""
        <div class="row";>
            <div class="col left">{ingredient_html}</div>
            <div class="col right">{instructions_html}</div>
        </div>
        """

    html += """
    </body>
    </html>
    """
    return html


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        source_html,                # the HTML to convert
        dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err

# d = {
#         'Title': recipe.title(),
#         'Time': recipe.total_time(),
#         'Yield': recipe.yields(),
#         'Ingredients': recipe.ingredients(),
#         'Instructions': recipe.instructions(),
#         'Image': recipe.image(),
#         'Tags': None
#     }


# This should really be in a separate file:
known_elements = {
    'flour': sc.Element('Flour',  density=0.7),
    'sugar': sc.Element('Sugar',  density=1.2),
    'salt': sc.Element('Salt',   density=1.2),
    'butter': sc.Element('Butter', density=0.9),
    'chicken': sc.Element('Chicken'),
    'salsa': sc.Element('salsa'),
    'eggs': sc.Element('eggs', is_int=True)
}
