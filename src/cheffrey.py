

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

import src.sugarcube as sc

class Ingredient(sc.Ingredient):

    

    def present(self):
        """
        Returns a human readable amount: 9 Quarts -> 2 Gallons 1 Quart
        It gets the highest unit where you're > 1, and then if necessary gives the remainder in terms of the next unit, rounded to one of the breakpoints
        """

        relevant_units = self.amount.unit.measure.units

        invalid_unit_names = [name for name in relevant_units.keys() if 'liter' in name]

        unit_list = [(unit, round(self.to(unit).amount.value, 3)) for unit in relevant_units.values() if unit.name not in invalid_unit_names]
        unit_list.sort(key=lambda x: x[1], reverse=True)

        whole_list = [(unit, value) for unit, value in unit_list if value >= 1]

        first = whole_list.pop()
        first_unit = first[0]
        first_value = int(first[1] - (first[1] % 1))
        remainder = first[1] % 1

        #Granularity down to the 1/8 of a unit
        cutoffs = [i/8 for i in range(8)]
        print(remainder)
        remainder = cutoffs[bisect(cutoffs, remainder)]

        if remainder > 0:
            remainder = Fraction(remainder)
            return f"{first_value} {remainder.numerator}/{remainder.denominator} {first_unit}s"
        else:
            return f"{first_value} {first_unit}s"


        # Instead of giving another unit, we're just gonna round the first unit
        # second = whole_list.pop()
        # second_unit = second[0]
        # second_value = sc.Amount(remainder, first_unit).to(second_unit).value


        
        



        
        

        return unit_list

        #Start at the smallest value, if you can go up a unit and still be >2, then do it
        unit, value = unit_list.pop()

        # relevant_units

        # if self.unit.measure == sc.Mass:
        #     pass

        # elif self.unit.measure == sc.sc.Volume:
        #     pass
            
        # else:
        #     raise TypeError(f"Cannot scale up measure: {self.unit.measure}")

        


        


        pass

    def __add__(self, other):
        if isinstance(other, Ingredient):
            if self.element.name != other.element.name:
                raise TypeError(f'Your trying to add ingredients that are different elements: {self.element.name} and {other.element.name}')

            return Ingredient(sc.Amount(self.amount.value + other.to(self.amount.unit).amount.value, self.amount.unit), self.element)
        elif isinstance(other, (int, float)):
            return Ingredient(sc.Amount(self.amount.value + other, self.amount.unit), self.element)
        else:
            raise TypeError(f"Dont know how to add an ingredient and an object of type {type(other)}")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Ingredient(sc.Amount(self.amount.value * other, self.amount.unit), self.element)
        else:
            raise TypeError(f"Dont know how to multiply an ingredient and an object of type {type(other)}")
    
    def __rmul__(self, other):
        return self.__mul__(other)






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
                shopping_list[ingredient.element.name] += ingredient
            else:
                shopping_list[ingredient.element.name] = ingredient
    
    #TODO: Round ingredient amounts accordingly

    return shopping_list