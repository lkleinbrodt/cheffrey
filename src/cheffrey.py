

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
import sugarcube as sc

class Recipe:
    def __init__(self, name, ingredients, instructions=None):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

class Cookbook:
    def __init__(self, title):
        self.title = title
        self.recipes = None


### Populating Classes

def random_ingredient():
    i = randint(1,10000)

    unit = sc.Volume.units[choice(list(sc.Volume.units.keys()))]
    amount = sc.Amount(i, unit = unit)
    sample_elements = [sc.Element(f'Ingredient_{i}') for i in range(20)]
    element = sample(sample_elements, 1)
    return sc.Ingredient(amount, element)
        
def random_cookbook():
    
    instructions = 'Cook them up real nice'
    
    my_recipes = [Recipe(f'sammy_{i}', [random_ingredient() for i in range(6)], instructions) for i in range(50)]
    my_cookbook = Cookbook("Lando's Cookbook")
    my_cookbook.recipes = my_recipes

    return my_cookbook
# Recipes are entered into an excel template sheet, I will format it so that it can be read in and parsed to this 
# we can always bulk process into json format for faster read times

def pick_recipes_randomly(cookbook, n_recipes):
    recipes = sample([recipe for recipe in cookbook.recipes], k=n_recipes)
    return recipes

def create_shopping_list(recipes):
    shopping_list = {}

    for recipe in recipes:
        for ingredient in recipe.ingredients:
            if ingredient.element.name in shopping_list.keys():
                existing_ingredient = shopping_list[ingredient.element.name]
                ingredient.to(existing_ingredient.amount.unit)
                # ing1 = random_ingredient()
                # ing2 = ing1

                # ing1.amount.value + ing2.amount.value

            else:
                shopping_list[ingredient] = ingredient