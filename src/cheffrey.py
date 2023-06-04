
from random import sample, randint, choice
from bisect import bisect
from fractions import Fraction

# from xhtml2pdf import pisa
import sugarcube as sc
from config import *
from s3 import *
import logging
import yaml
# import openai
import numpy as np
import gensim
import json
from annoy import AnnoyIndex
logger = logging.getLogger(__name__)

# openai.api_key = os.getenv("OPENAI_KEY")

def get_embedding(model: gensim.models.KeyedVectors, text: str):
    tokens = text.lower().split()  # Tokenize and preprocess the text
    embeddings = [model[word] for word in tokens if word in model]  # Get embeddings for each token
    num_embeddings = len(embeddings)
    if num_embeddings > 0:
        embedding = np.sum(embeddings, axis=0) / num_embeddings  # Calculate the average embedding
        return embedding
    else:
        return None

def search_recipes(query: str, annoy_index: AnnoyIndex, embedding_model: gensim.models.KeyedVectors, recipe_id_to_title: dict, n = 5) -> list:
    query_embedding = get_embedding(embedding_model, query)
    nearest_indices = annoy_index.get_nns_by_vector(query_embedding, n)
    recommended_recipes = [recipe_id_to_title[i] for i in nearest_indices]
    return recommended_recipes


def load_yaml(name):
    valid_names = ['config', 'recipes']
    if name in valid_names:
        with open(ROOT_DIR/f"data/{name}.yaml", 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(
            f"Unrecognized name: {name}. Valid types are: {valid_names}")


def load_annoy_index(embedding_dim):
    new_index = AnnoyIndex(embedding_dim, metric = 'euclidean')
    new_index.load(str(ROOT_DIR/'data/annoy_index.ann'))
    return new_index


def load_embedding_model():
    path = ROOT_DIR/'data/embedding_model.pkl'
    return gensim.models.KeyedVectors.load(str(path))

def add_to_recipe_file(recipe, overwrite=False):
    #TODO: inefficient
    all_recipes = load_s3_recipes()

    if (recipe['Title'] in all_recipes.keys()) & (overwrite == False):
        raise FileExistsError(
            f"{recipe.title()} already found in the file, and overwrite set to false")

    all_recipes[recipe['Title']] = recipe

    return save_s3_recipes(all_recipes)


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
    sample_elements = [sc.Element(f'ingredient_{i}') for i in range(20)]
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

from urllib import request as ulreq
from PIL import ImageFile
def getsizes(uri):
    # get image size (None if not known)
    with  ulreq.urlopen(uri) as file:
        p = ImageFile.Parser()
        while 1:
            data = file.read(1024)
            if not data:
                break
            p.feed(data)
            if p.image:
                return p.image.size

def __create_shopping_list(recipe_list, nlp):
    """deprecated, back when using spacy for parsing ingredients"""
    all_ingredients = [item for recipe in recipe_list for item in recipe['ingredients']]
    parsed_ingredients = [__parse_ingredient(ing, nlp) for ing in all_ingredients]
    shopping_list = combine_ingredients(parsed_ingredients)
    return shopping_list


def __parse_ingredient(ingredient, nlp):
    """deprecated, back when using spacy for parsing ingredients"""
    ing = ingredient.replace('-', ' ').split(',')[0]
    ing = nlp(ing)
    pos = [i.pos_ for i in ing]

    if pos[0] != 'NUM':
        return create_ingredient(
            amount = None, 
            measure = None, 
            item = ing.text
        )

    else:
        
        modifier = 1
        i = 0
        amount_list = []
        while pos[i] == 'NUM':
            
            if ing[i].text.lower() in number_dict.keys():
                x = number_dict[ing[i].text.lower()]
                modifier = x
            else:
                amount_list += [ing[i].text]
            if i == (len(pos) - 1):
                return create_ingredient(None, None, ing.text)
            i += 1
        
        amount = float(sum(Fraction(s) for s in amount_list))
        amount *= modifier
        non_numerical_start = i

        if ing[i].text == '(':

            end_idx = i
            while ')' not in ing[end_idx].text:
                end_idx += 1
                if end_idx > len(ing):
                    return create_ingredient(None, None, ing.text)
            
            paran_text = [ing[x].text for x in range(i+1, end_idx)]
            
            if any([measure in paran_text for measure in sc.available_measures]):
                modifier = amount
                unit = float(ing[i+1].text)
                measure = ing[i+2].text
                item = ' '.join([x.text for x in ing[i+4:]])
                return create_ingredient(modifier*unit, measure, item)
            else:
                return create_ingredient(None, None, ing.text)

        
        while ing[i].text not in sc.available_measures:
            if i == (len(pos)-1):
                t = ' '.join([x.text for x in ing[non_numerical_start:]])
                a = amount if amount else ''
                return create_ingredient(a, 'unit', t)

            if ing[i].text in ['small', 'medium', 'large', 'fat']:
                item = ' '.join([i.text for i in ing[i:]])
                return create_ingredient(
                    amount = amount,
                    measure = 'unit',
                    item = item
                )

            i += 1
        
        measure = ing[i].text
        item = ' '.join([i.text for i in ing[i+1:]])

        if item == '':
            return create_ingredient(None, None, ing.text)
        else:
            return create_ingredient(amount, measure, item)

def create_ingredient(amount, measure, item):

    measure = sc.available_measures.get(measure, None)

    if amount is None:
        amount = ''

    if measure is None:
        return str(amount) + ' ' + str(item)

    

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

def create_recipe_html(recipe, standalone = False):

    if standalone:
        html = ""
    else:
        html = "<div style='break-before:all'>"
        html += "<hr><hr>"
    html += f"""<h1 style='text-align:center'> {recipe['title']}</h1>"""
    html += "<br>"
    
    image_size = getsizes(recipe['image'])
    if image_size:
        image_width, image_height = image_size
        image_height /= (image_width / 350)
        image_width = 350

    html += f"""
    <img 
        src='{recipe['image']}'; 
        alt='{recipe['title']}'; 
        width='{image_width}';
        height='{image_height}';
        class='center';
    >"""

    html += "</div>"

    ingredient_html = "<h2 style='text-align:center'> Ingredients: </h2>"
    ingredient_html += f"<p> Yields: {recipe['yields']}</p>"
    ingredient_html += "<ul>"
    for ingredient in recipe['ingredients']:
        ingredient_html += "<li>" + ingredient + "</li>"
    ingredient_html += "</ul>"

    instructions_html = "<h2 style='text-align:center'> Instructions: </h2>"
    instructions_html += "<ol>"
    instructions = recipe['instructions'].split('. ')
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
        html += create_recipe_html(recipe)
        

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

def load_local_recipes():
    with open(ROOT_DIR/'data/recipes.json', 'r') as f:
        x = json.load(f)
    return x


def load_s3_recipes():
    return load_s3_yaml('recipes.yaml')

def save_s3_recipes(recipes):
    return save_s3_yaml(recipes, 'recipes.yaml')

carriers = {
    'att': 'txt.att.net',
    'verizon': 'vtext.com',
    'tmobile': 'tmomail.net',
    'sprint': 'messaging.sprintpcs.com',
}

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def text_meal_plan(phone_number, meal_plan):
    email_address = 'lkleinbrodt@gmail.com'
    try:
        email_password = st.secrets['email_password']
        
    except FileNotFoundError:
        email_password = os.getenv('email_password')
    
    phone_carrier_domain = carriers['att'] #TODO: try all combos
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = f"{phone_number}@{phone_carrier_domain}"

    html_part = MIMEText(meal_plan, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email_address, email_password)

        # Send the message
        server.sendmail(
            email_address, 
            f"{phone_number}@{phone_carrier_domain}", 
            msg.as_string()
        )

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