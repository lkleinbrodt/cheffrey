from random import sample, randint, choice
from bisect import bisect
from fractions import Fraction
import sugarcube as sc
from config import *
from s3 import *
import logging
import yaml

logger = logging.getLogger(__name__)
logger.debug("Start of program")


def load_yaml(name):
    """
    Load a YAML file based on a valid name.

    Args:
        name (str): name of the YAML file to load.

    Returns:
        A dictionary with the contents of the YAML file.

    Raises:
        ValueError: if the name provided is not valid.
    """
    valid_names = ["config", "recipes"]
    if name in valid_names:
        with open(ROOT_DIR / f"data/{name}.yaml", "r") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unrecognized name: {name}. Valid types are: {valid_names}")


def parse_scraped_recipe(recipe):
    """
    Return a dictionary containing the parsed information of a scraped recipe

    Args:
        recipe: An object containing information/details of a scraped recipe

    Returns:
        A dictionary containing the following keys:
            - Title: String containing the title of the recipe
            - Time: String containing the cooking time of the recipe
            - Yield: String containing the yield/serving size of the recipe
            - Ingredients: List containing the ingredients of the recipe
            - Instructions: List containing the instructions for preparing the recipe
            - Image: String containing the URL of the recipe's image
            - Tags: None by default

    Example Usage:
        >>> recipe = scrape_website()
        >>> parsed_recipe = parse_scraped_recipe(recipe)"""
    d = {
        "Title": recipe.title(),
        "Time": recipe.total_time(),
        "Yield": recipe.yields(),
        "Ingredients": recipe.ingredients(),
        "Instructions": recipe.instructions(),
        "Image": recipe.image(),
        "Tags": None,
    }
    return d


def add_to_recipe_file(recipe, overwrite=False):
    """
    Add a recipe to the recipe file in AWS S3.

    Keyword arguments:
    recipe - a dictionary containing recipe information.
    overwrite - If False, the function will raise a FileExistsError if there is already a recipe by the same name.

    Returns:
    The output of save_s3_recipes function, which saves all the recipes."""
    all_recipes = load_s3_recipes()
    if (recipe["Title"] in all_recipes.keys()) & (overwrite == False):
        raise FileExistsError(
            f"{recipe.title()} already found in the file, and overwrite set to false"
        )
    all_recipes[recipe["Title"]] = recipe
    return save_s3_recipes(all_recipes)


class Ingredient(sc.Ingredient):
    def display(self):
        return str(self)

    def display_amount(self):
        """
        Returns a human readable amount: 9 Quarts -> 2 Gallons 1 Quart
        It gets the highest unit where you're > 1, and then if necessary gives the remainder in terms of the next unit, rounded to one of the breakpoints
        """
        relevant_units = self.amount.unit.measure.units
        invalid_unit_names = [name for name in relevant_units.keys() if "liter" in name]
        if self.amount.unit.name in ["teaspoon", "tablespoon"]:
            invalid_unit_names += ["fluidOunce"]
        if self.amount.unit in sc.Mass.units:
            relevant_units = [sc.Mass.units["ounce"], sc.Mass.units["pound"]]
        unit_list = [
            (unit, round(self.to(unit).amount.value, 3))
            for unit in relevant_units.values()
            if unit.name not in invalid_unit_names
        ]
        unit_list.sort(key=lambda x: x[1], reverse=True)
        whole_list = [(unit, value) for (unit, value) in unit_list if value >= 1]
        first = whole_list.pop()
        first_unit = first[0]
        first_value = int(first[1] - first[1] % 1)
        remainder = first[1] % 1
        cutoffs = [i / 8 for i in range(9)]
        try:
            remainder = cutoffs[bisect(cutoffs, remainder) - 1]
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
                    f"Your trying to add ingredients that are different elements: {self.element.name} and {other.element.name}"
                )
            return Ingredient(
                sc.Amount(
                    self.amount.value + other.to(self.amount.unit).amount.value,
                    self.amount.unit,
                ),
                self.element,
            )
        elif isinstance(other, (int, float)):
            if self.element.is_int:
                assert (
                    other % 1 == 0
                ), f"{self.element.name} is a whole ingredient, can only add whole numbers"
            return Ingredient(
                sc.Amount(self.amount.value + other, self.amount.unit), self.element
            )
        else:
            raise TypeError(
                f"Dont know how to add an ingredient and an object of type {type(other)}"
            )

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Ingredient(
                sc.Amount(self.amount.value * other, self.amount.unit), self.element
            )
        else:
            raise TypeError(
                f"Dont know how to multiply an ingredient and an object of type {type(other)}"
            )

    def __rmul__(self, other):
        return self.__mul__(other)

    def _from_strings(amount_str, element_str):
        logger.info(amount_str)
        logger.info(element_str)
        amount_list = str.split(amount_str)
        value = float(amount_list[0])
        if value % 1 == 0:
            value = int(value)
        unit_str = " ".join(amount_list[1:])
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
            raise ValueError(f"Unrecognized unit: {unit_str}")
        if element_str not in known_elements.keys():
            raise ValueError(
                f"Unrecognized element: {element_str}, you might need to add it to the master list"
            )
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
    """
    Converts a YAML format recipe dictionary into a Recipe class object.

    Args:
    recipe_name (str): Name of the recipe.
    recipe_dict (dict): Dictionary containing recipe information.

    Returns:
    Recipe: A Recipe object containing the information from recipe_dict.
    """
    logger.info(recipe_dict)
    ingredients = {
        ingredient_name: Ingredient._from_strings(amount_str, ingredient_name)
        for (ingredient_name, amount_str) in recipe_dict["ingredients"].items()
    }
    return Recipe(recipe_name, ingredients, recipe_dict["instructions"])


class Cookbook(object):
    def __init__(self, title, recipe_dict):
        self.title = title
        self.recipes = recipe_dict


def random_ingredient():
    """
    Return a random Ingredient object with a randomly generated quantity, unit and element from provided sample elements.

    No arguments required.

    Returns:
        A randomly generated Ingredient object, consisting of a Quantity with a randomly generated amount and unit, and an Element
        chosen at random from the provided sample elements."""
    i = randint(1, 10)
    unit = sc.Volume.units[choice(list(sc.Volume.units.keys()))]
    amount = sc.Amount(i, unit=unit)
    sample_elements = [sc.Element(f"Ingredient_{i}") for i in range(20)]
    element = sample(sample_elements, 1)[0]
    return Ingredient(amount, element)


def random_cookbook():
    """
    Generates a Cookbook object with 50 randomly generated Recipe objects. Recipe objects are made with 6 random ingredients and instructions "Cook them up real nice"
    """
    instructions = "Cook them up real nice"
    my_recipes = [
        Recipe(f"sammy_{i}", [random_ingredient() for i in range(6)], instructions)
        for i in range(50)
    ]
    my_cookbook = Cookbook("Lando's Cookbook")
    my_cookbook.recipes = my_recipes
    return my_cookbook


def pick_recipes_randomly(cookbook, n_recipes):
    """
    Randomly picks n_recipes from the cookbook

    Arguments:
        cookbook {Cookbook} -- An instance of Cookbook class that contains a dictionary with all recipes
        n_recipes {int} -- number of recipes to pick from all available in cookbook

    Returns:
        list -- a list containing the randomly selected recipes
    """
    recipes = sample([recipe for recipe in cookbook.recipes.values()], k=n_recipes)
    return recipes


def combine_ingredients(ingredient_list: list):
    """
    Combines a list of ingredients into a dictionary per element based on their name

    Args:
        ingredient_list (list): A list of Ingredient objects or strings

    Returns:
        A list of Ingredient objects or strings with the same order as the original ingredient_list
    """
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


def create_shopping_list(recipe_list, nlp):
    """
    Create a consolidated shopping list from a list of recipes.

    Args:
        recipe_list (list): A list of recipe dictionaries. Each dictionary should contain an 'Ingredients' key with a list of ingredients.
        nlp: An instance of the Natural Language Processing library (spaCy)

    Returns:
        list: A list of combined and parsed ingredients from the input recipe list.
    """
    all_ingredients = [item for recipe in recipe_list for item in recipe["Ingredients"]]
    parsed_ingredients = [parse_ingredient(ing, nlp) for ing in all_ingredients]
    shopping_list = combine_ingredients(parsed_ingredients)
    return shopping_list


def parse_ingredient(ingredient, nlp):
    """Return an ingredient in the format (amount, measure, item).

    Keyword arguments:
    ingredient -- The ingredient to be parsed and returned in the correct format.
    nlp -- the spaCy natural language processing object.

    If the ingredient can be parsed into an amount and measure, then create the ingredient with amount, measure, and item as arguments.
    If the ingredient contains a numerical value but no measure, then create the ingredient with the unit measure, numerical value and item as arguments.
    If the ingredient cannot be parsed either as above, then return create_ingredient(None, None, ing.text)
    """
    ing = ingredient.replace("-", " ").split(",")[0]
    ing = nlp(ing)
    pos = [i.pos_ for i in ing]
    if pos[0] != "NUM":
        return create_ingredient(amount=None, measure=None, item=ing.text)
    else:
        modifier = 1
        i = 0
        amount_list = []
        while pos[i] == "NUM":
            if ing[i].text.lower() in number_dict.keys():
                x = number_dict[ing[i].text.lower()]
                modifier = x
            else:
                amount_list += [ing[i].text]
            if i == len(pos) - 1:
                return create_ingredient(None, None, ing.text)
            i += 1
        amount = float(sum((Fraction(s) for s in amount_list)))
        amount *= modifier
        non_numerical_start = i
        if ing[i].text == "(":
            end_idx = i
            while ")" not in ing[end_idx].text:
                end_idx += 1
                if end_idx > len(ing):
                    return create_ingredient(None, None, ing.text)
            paran_text = [ing[x].text for x in range(i + 1, end_idx)]
            if any([measure in paran_text for measure in sc.available_measures]):
                modifier = amount
                unit = float(ing[i + 1].text)
                measure = ing[i + 2].text
                item = " ".join([x.text for x in ing[i + 4 :]])
                return create_ingredient(modifier * unit, measure, item)
            else:
                return create_ingredient(None, None, ing.text)
        while ing[i].text not in sc.available_measures:
            if i == len(pos) - 1:
                t = " ".join([x.text for x in ing[non_numerical_start:]])
                a = amount if amount else ""
                return create_ingredient(a, "unit", t)
            if ing[i].text in ["small", "medium", "large", "fat"]:
                item = " ".join([i.text for i in ing[i:]])
                return create_ingredient(amount=amount, measure="unit", item=item)
            i += 1
        measure = ing[i].text
        item = " ".join([i.text for i in ing[i + 1 :]])
        if item == "":
            return create_ingredient(None, None, ing.text)
        else:
            return create_ingredient(amount, measure, item)


def create_ingredient(amount, measure, item):
    """
    Create an ingredient object from given recipe ingredient parameters.

    Arguments:
    - amount: amount of the ingredient used in the recipe (in float)
    - measure: measurement unit of the ingredient used in the recipe (in string)
    - item: name of the ingredient used in the recipe (in string)

    Returns:
    - An ingredient object containing the given ingredient parameters. (in Ingredient format)
    """
    measure = sc.available_measures.get(measure, None)
    if amount is None:
        amount = ""
    if measure is None:
        return str(amount) + " " + str(item)
    element = sc.Element(item)
    ing = Ingredient(amount=amount * measure, element=element)
    return ing


def css_style():
    """
    Reads the content of the CSS file and returns it as a string.

    Returns:
    :returns string: The content of the CSS file as a string.
    """
    with open("./meal_plan_style.css", "r") as f:
        x = f.read()
    return x


def create_recipe_html(recipe, standalone=False):
    """Return an HTML string with the recipe details including a title, an image, ingredient list, yields, and instructions.

    Args:
        recipe: A dictionary containing recipe details including title, image, ingredients, yields, and instructions
        standalone: A boolean value determining whether the HTML should stand on its own or be wrapped in a div. The default is False.

    Returns:
        An HTML string containing the recipe details including a title, an image, ingredient list, yields, and instructions.
    """
    if standalone:
        html = ""
    else:
        html = "<div style='break-before:all'>"
        html += "<hr><hr>"
    html += f"<h1 style='text-align:center'> {recipe['Title']}</h1>"
    html += "<br>"
    html += f"\n    <img \n        src='{recipe['Image']}'; \n        alt='{recipe['Title']}'; \n        class='center';\n    >"
    html += "</div>"
    ingredient_html = "<h2 style='text-align:center'> Ingredients: </h2>"
    ingredient_html += f"<p> Yields: {recipe['Yield']}</p>"
    ingredient_html += "<ul>"
    for ingredient in recipe["Ingredients"]:
        ingredient_html += "<li>" + ingredient + "</li>"
    ingredient_html += "</ul>"
    instructions_html = "<h2 style='text-align:center'> Instructions: </h2>"
    instructions_html += "<ol>"
    instructions = recipe["Instructions"].split(". ")
    for instruction in instructions:
        instructions_html += "<li>" + instruction + "</li>"
    instructions_html += "</ol>"
    html += f'\n    <div class="row";>\n        <div class="col left">{ingredient_html}</div>\n        <div class="col right">{instructions_html}</div>\n    </div>\n    '
    return html


def create_meal_plan_html(meal_plan):
    """
    Create a simple HTML document that contains a shopping list and a series of recipes.

    Args:
        meal_plan (dict): A dictionary object that contains a shopping list and a list of recipes

    Returns:
        str: An HTML document as a string that displays the shopping list divided into two columns and the recipe contents added with a horizontal divider.
    """
    shopping_list = meal_plan["Shopping List"]
    recipes = meal_plan["Recipes"]
    html = f'\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <style type="text/css" media="screen">\n    {css_style()}\n    </style>\n    </head>\n    <body>\n    '
    html += "<h1 style='text-align:center'>Shopping List</h1>"
    n_items = len(shopping_list)
    shop1 = shopping_list[: int(n_items / 2)]
    shop2 = shopping_list[int(n_items / 2) :]

    def item_to_html(i):
        if isinstance(i, Ingredient):
            return i.display()
        else:
            return i

    shop1_html = "".join(["<li>" + item_to_html(item) + "</li>" for item in shop1])
    shop2_html = "".join(["<li>" + item_to_html(item) + "</li>" for item in shop2])
    html += f'\n        <div class="row";>\n            <div class="col"><ul>{shop1_html}</ul></div>\n            <div class="col"><ul>{shop2_html}</ul></div>\n        </div>\n        '
    html += "<hr>"
    for recipe in recipes:
        html += create_recipe_html(recipe)
    html += "\n    </body>\n    </html>\n    "
    return html


known_elements = {
    "flour": sc.Element("Flour", density=0.7),
    "sugar": sc.Element("Sugar", density=1.2),
    "salt": sc.Element("Salt", density=1.2),
    "butter": sc.Element("Butter", density=0.9),
    "chicken": sc.Element("Chicken"),
    "salsa": sc.Element("salsa"),
    "eggs": sc.Element("eggs", is_int=True),
}
number_dict = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "dozen": 12,
}


def load_s3_recipes():
    """
    Load recipe data from a yaml file stored in S3 bucket.

    Returns:
        A dictionary containing recipes data.

    Raises:
        Any exception that occurs during the process of loading YAML file from S3 bucket.
    """
    return load_s3_yaml("recipes.yaml")


def save_s3_recipes(recipes):
    """
    Saves a list of recipe dictionaries to an AWS S3 bucket in YAML format.

    Args:
        recipes (list): A list of dictionaries containing recipe information.

    Returns:
        None. The function uploads the recipe information to the specified location in an S3 bucket.
    """
    return save_s3_yaml(recipes, "recipes.yaml")


carriers = {
    "att": "txt.att.net",
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
}
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def text_meal_plan(phone_number, meal_plan):
    """
    Send a meal plan to a phone number via text message.

    Arguments:
    phone_number -- a string representing the phone number we have to send the message
    meal_plan -- a string representing the full meal plan

    Returns:
    Nothing, sends a text message to the given phone_number with the meal_plan."""
    email_address = "lkleinbrodt@gmail.com"
    try:
        email_password = st.secrets["email_password"]
    except FileNotFoundError:
        email_password = os.getenv("email_password")
    phone_carrier_domain = carriers["att"]
    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = f"{phone_number}@{phone_carrier_domain}"
    html_part = MIMEText(meal_plan, "html")
    msg.attach(html_part)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(
            email_address, f"{phone_number}@{phone_carrier_domain}", msg.as_string()
        )
