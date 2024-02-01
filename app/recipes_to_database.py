#%%
import logging
from app import db, app
from app.models import Recipe
from config import Config
import json
import random
from openai import OpenAI

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler and set its log level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the console handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)


def char_to_price(n_chars):
    """estimates the price to embed this many chars using openai"""
    chars_per_token = 3.7
    n_tokens = n_chars / chars_per_token
    price_per_token = 0.001 / 1000
    price = price_per_token * n_tokens
    return price


def add_recipes_to_db():
    logger.info('Adding recipes to database')
    with app.app_context():
        
        with open(Config.ROOT_DIR+'/data/recipes.json') as file:
            recipes_data = json.load(file)
            
        for recipe_data in recipes_data.values():
            title = recipe_data.get('title')[:255]
            existing_recipe = Recipe.query.filter_by(title=title).first()

            if existing_recipe:
                existing_recipe.author = recipe_data.get('author')
                existing_recipe.canonical_url = recipe_data.get('canonical_url')
                existing_recipe.category = recipe_data.get('category')
                existing_recipe.image_url = recipe_data.get('image')
                existing_recipe.ingredients = str(recipe_data.get('ingredients'))[:5_000]
                existing_recipe.description = recipe_data.get('description')
                existing_recipe.instructions = recipe_data.get('instructions')[:10_000]
                existing_recipe.instructions_list = str(recipe_data.get('instructions_list'))[:10_000]
                existing_recipe.total_time = recipe_data.get('total_time')
                existing_recipe.yields = recipe_data.get('yields')
            else:
                recipe = Recipe(
                    title=title,
                    author=recipe_data.get('author'),
                    canonical_url=recipe_data.get('canonical_url'),
                    category=recipe_data.get('category'),
                    image_url=recipe_data.get('image'),
                    ingredients=str(recipe_data.get('ingredients'))[:5_000],
                    description=recipe_data.get('description'),
                    instructions=recipe_data.get('instructions')[:10_000],
                    instructions_list=str(recipe_data.get('instructions_list'))[:10_000],
                    total_time=recipe_data.get('total_time'),
                    yields=recipe_data.get('yields')
                )
                db.session.add(recipe)

        db.session.commit()

#%%
def add_recipe_descriptions():
    logger.info('Adding recipe descriptions')
    with open(Config.ROOT_DIR+'/data/recipes.json') as file:
        recipes_data = json.load(file)
        
    recipes_with_descriptions = [recipe for recipe in recipes_data.values() if recipe.get('description') is not None]
    recipes_with_descriptions = [recipe for recipe in recipes_with_descriptions if len(recipe.get('description')) < 200]
    recipes_without_descriptions = [recipe for recipe in recipes_data.values() if recipe.get('description') is None]
    
    logger.info(f"{len(recipes_without_descriptions)} recipes without descriptions.")
    
    client = OpenAI()
    
    def recipe_to_str(recipe):
        return f"""
    Title: {recipe.get('title')}
    category: {recipe.get('category')}
    instructions: {recipe.get('instructions')}
    """
    
    def get_recipe_description(recipe, examples = [], return_messages = False):
        messages = [
            {"role": "system", "content": "You are a foodwriter, adept at writing concise and helpful descriptions for recipes. Use the information given but also feel free to bring in your own cooking knowledge. Your response must be less than 150 characters. Do not copy the structure of previous responses. Do not be too similar to previous responses"},
            {"role": "system", "content": "Rules: Keep your responses to less than 150 characters. Do not repeat the name of the dish. Do not sound too similar to the other examples."},
        ]
        for example in examples:
            messages += [
                {"role": "user", "content": "Write a brief description of the following dish:" + recipe_to_str(example)},
                {"role": "system", "content": example.get('description')[:150]}
            ]
        
        messages += [
            {"role": "user", "content": "Write a brief description (to be used as a blurb/caption on a recipe website) of the following dish:" + recipe_to_str(recipe)},
        ]
        
        completion = client.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages=messages
        )
        
        if return_messages:
            return completion.choices[0].message.content, messages
        else:
            return completion.choices[0].message.content
    
    good_examples = [
        recipes_data['Miso Fish Chowder'],
        recipes_data['Nectarine Tart'],
        recipes_data['Pressure Cooker Kalbi Jjim'],
        recipes_data["Sesame Tofu With Coconut-Lime Dressing and Spinach"],
        recipes_data['Walnut Picadillo'],
    ]
    for i, recipe in enumerate(recipes_without_descriptions):
        examples = random.sample(good_examples, 2)
        examples = []
        description = get_recipe_description(recipe, examples)
        recipes_data[recipe['title']]['description'] = description
        recipe['description'] = description
        if i % 5 == 0:
            logger.info(f"{i} recipes completed.")
            # est_price = char_to_price(len(str(messages)))
            # logger.info(f"Estimated prcie for this recipe: {est_price}. Estimated total price: {est_price * len(recipes_without_descriptions)}")
            with open(Config.ROOT_DIR+'/data/recipes.json', 'w') as file:
                json.dump(recipes_data, file)
            
    with open(Config.ROOT_DIR+'/data/recipes.json', 'w') as file:
        json.dump(recipes_data, file)
    

#%%

def clear_recipes():
    confirmation = input("Are you sure you want to clear all recipes? (y/n): ")
    if confirmation.lower() == "y":
        with app.app_context():
            Recipe.query.delete()
            db.session.commit()


if __name__ == '__main__':
    # logger.info('Start')
    clear_recipes()
    add_recipe_descriptions()
    add_recipes_to_db()