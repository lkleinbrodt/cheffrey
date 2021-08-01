

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
import src.sugarcube as sc

class Ingredient(sc.Ingredient):

    def __add__(self, other):
        if self.element.name != other.element.name:
            raise TypeError(f'Your trying to add ingredients that are different elements: {self.element.name} and {other.element.name}')

        return Ingredient(sc.Amount(self.amount.value + other.to(self.amount.unit).amount.value, self.amount.unit), self.element)

    def scale_up(self):
        relevant_units = self.amount.unit.measure.units

        invalid_unit_names = ['decaliter', 'hectoliter', 'kiloliter']

        unit_list = [(unit, self.to(unit).amount.value) for unit in relevant_units.values() if unit.name not in invalid_unit_names]
        unit_list.sort(key=lambda x: x[1], reverse=True)
        print(unit_list)

        #Start at the smallest value, if you can go up a unit and still be >2, then do it
        unit, value = unit_list.pop()
        


        pass






class Recipe(object):
    def __init__(self, name, ingredients, instructions=None):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

    def __str__(self) -> str:
        return f"Recipe for {self.name}: {self.ingredients}"


class Cookbook(object):
    def __init__(self, title):
        self.title = title
        self.recipes = None


### Populating Classes

def random_ingredient():
    i = randint(1,10)

    unit = sc.Volume.units[choice(list(sc.Volume.units.keys()))]
    amount = sc.Amount(i, unit = unit)
    sample_elements = [sc.Element(f'Ingredient_{i}') for i in range(20)]
    element = sample(sample_elements, 1)[0]
    return Ingredient(amount, element)
        
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

    ### Add Ingredients
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            if ingredient.element.name in shopping_list.keys():
                print(f'Existing: {shopping_list[ingredient.element.name]}')
                print(f"New: {ingredient}")
                shopping_list[ingredient.element.name] += ingredient
            else:
                shopping_list[ingredient.element.name] = ingredient
    
    #TODO: Round ingredient amounts accordingly

    return shopping_list