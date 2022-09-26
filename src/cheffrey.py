

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

import boto3
import spacy
from random import sample, randint, choice
from bisect import bisect
from fractions import Fraction
import itertools

# from xhtml2pdf import pisa
from src import sugarcube as sc
import logging
import yaml
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

    def display(self):
        # amount = self.display_amount()
        # element = self.element
        # return str(amount) + ' ' + str(element)
        return str(self)

    def display_amount(self):
        """
        Returns a human readable amount: 9 Quarts -> 2 Gallons 1 Quart
        It gets the highest unit where you're > 1, and then if necessary gives the remainder in terms of the next unit, rounded to one of the breakpoints
        """

        relevant_units = self.amount.unit.measure.units

        invalid_unit_names = [
            name for name in relevant_units.keys() if 'liter' in name]
        
        if self.amount.unit.name in ['teaspoon', 'tablespoon']:
            invalid_unit_names += ['fluidOunce']
        if self.amount.unit in sc.Mass.units:
            relevant_units = [sc.Mass.units['ounce'], sc.Mass.units['pound']]


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
            remainder = cutoffs[bisect(cutoffs, remainder)-1]
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


def pick_recipes_randomly(cookbook, n_recipes):
    recipes = sample(
        [recipe for recipe in cookbook.recipes.values()], k=n_recipes)
    return recipes

def combine_ingredients(ingredient_list: list):
    out = {}
    for ingredient in ingredient_list:
        if type(ingredient) == Ingredient:
            if ingredient.element in out.keys():
                out[ingredient.element] += ingredient
            else:
                out[ingredient.element] = ingredient
        else:
            out[ingredient] = ingredient
    
    return list(out.values())

def create_shopping_list(recipe_list):
    all_ingredients = [item for recipe in recipe_list for item in recipe['Ingredients']]
    nlp = spacy.load("en_core_web_sm")
    parsed_ingredients = [parse_ingredient(ing, nlp) for ing in all_ingredients]
    parsed_ingredients = [create_ingredient(p[0], p[1], p[2]) for p in parsed_ingredients]
    shopping_list = combine_ingredients(parsed_ingredients)
    return shopping_list


def parse_ingredient(ingredient, nlp):
    ing = ingredient.replace('-', ' ').split(',')[0]
    ing = nlp(ing)
    pos = [i.pos_ for i in ing]

    if pos[0] == 'NUM':
        if ing[0].text.lower() in number_dict:
            modifier = number_dict[ing[0].text.lower()]
            amount_list = []
        else:
            amount_list = [ing[0].text]
            modifier = 1
        
        i = 1

        while pos[i] == 'NUM':
            amount_list += [ing[i].text]
            if i == (len(pos)-1):
                return (None, None, ing.text)
            i += 1
        amount = float(sum(Fraction(s) for s in amount_list))
        amount *= modifier
        
        # while pos[i] not in ['NOUN', 'PROPN']:
            # if i == (len(pos)-1):
            #     return (None, None, ing.text)
            # i += 1
        while ing[i].text not in sc.available_measures:
            if i == (len(pos)-1):
                return (None, None, ing.text)

            if ing[i].text in ['small', 'medium', 'large']:
                item = ' '.join([i.text for i in ing[i:]])
                measure = sc.Unit('', '')
                return (amount, measure, item)

            i += 1
        
        measure =  ing[i].text
        item = ' '.join([i.text for i in ing[i+1:]])

        if item == '':
            return (None, None, ing.text)
        else:
            return (amount, measure, item)
    
    else:
        return (None, None, ing.text)

def create_ingredient(amount, measure, item):

    if measure is None:
        return item
    elif measure in sc.Volume.units:
        measure = sc.Volume.units[measure]
    elif measure in sc.Mass.units:
        measure = sc.Mass.units[measure]
    else:
        return str(amount) + ' ' + str(item)
        #raise ValueError(f"Unknown measure: {x.Measure}")

    element = sc.Element(item)

    ing = Ingredient(
        amount = amount * measure,
        element = element
    )

    return ing


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

    n_items = len(shopping_list)

    shop1 = shopping_list[:int(n_items/2)]
    shop2 = shopping_list[int(n_items/2):]

    def item_to_html(i):
        if isinstance(i, Ingredient):
            return i.display()
        else:
            return i

    shop1_html = ''.join(["<li>" + item_to_html(item) + "</li>" for item in shop1])
    shop2_html = ''.join(["<li>" + item_to_html(item) + "</li>" for item in shop2])
    html += f"""
        <div class="row";>
            <div class="col"><ul>{shop1_html}</ul></div>
            <div class="col"><ul>{shop2_html}</ul></div>
        </div>
        """

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
        ingredient_html += f"<p> Yields: {recipe['Yield']}</p>"
        ingredient_html += "<ul>"
        for ingredient in recipe['Ingredients']:
            ingredient_html += "<li>" + ingredient + "</li>"
        ingredient_html += "</ul>"

        instructions_html = "<h2 style='text-align:center'> Instructions: </h2>"
        instructions_html += "<ol>"
        instructions = recipe['Instructions'].split('. ')
        for instruction in instructions:
            instructions_html += "<li>" + instruction + "</li>"
        instructions_html += "</ol>"

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


# def convert_html_to_pdf(source_html, output_filename):
#     # open output file for writing (truncated binary)
#     result_file = open(output_filename, "w+b")

#     # convert HTML to PDF
#     pisa_status = pisa.CreatePDF(
#         source_html,                # the HTML to convert
#         dest=result_file)           # file handle to recieve result

#     # close output file
#     result_file.close()                 # close output file

#     # return False on success and True on errors
#     return pisa_status.err

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

number_dict = {
            'one':1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'dozen': 12
        }

# import os
# s3 = boto3.client(
#     's3',
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
# )
# s3.download_file('cheffrey', 'recipes.yaml', './test.yaml')
