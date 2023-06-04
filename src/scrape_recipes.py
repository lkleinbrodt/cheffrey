import cheffrey
from recipe_scrapers import scrape_me as scrape_recipe
from bs4 import BeautifulSoup
import requests
import os
import re
import json


def pull_existing_recipes():
    master_recipes = cheffrey.load_local_recipes()
    titles = list(master_recipes.keys())
    urls = [r['canonical_url'] for r in master_recipes.values()]
    return titles, urls

def add_to_recipe(recipe):
    #TODO: inefficient to load and save everytime
    master_recipes = cheffrey.load_local_recipes()
    master_recipes[recipe['title']] = recipe
    with open(cheffrey.ROOT_DIR/'data/recipes.json', 'w') as f:
        json.dump(master_recipes, f)

def download_recipe(url_to_download, existing_titles, existing_urls, source):
    if url_to_download in existing_urls:
        print(f"Skipping. Already in database")
        return
    recipe = scrape_recipe(url_to_download)
    recipe = recipe.to_json()
    if recipe['title'] in existing_titles:
        recipe['title'] += f' ({source})'
    # we already checked if one exists
    add_to_recipe(recipe)

def scrape_collection(collection_url):
    base_url = collection_url.split('.com')[0] + '.com/'
    res = requests.get(collection_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features='lxml')

    if base_url == 'https://cooking.nytimes.com/':
        recipe_cards = soup.find_all('a', {'class': 'image-anchor card-link'})
        source = 'New York Times'
    elif base_url == 'https://www.bonappetit.com/':
        recipe_cards = soup.find_all('a', {'href': re.compile(r'/recipe')})
        source = 'Bon Appetit'
    else:
        raise ValueError(f"Unrecognized source: {base_url}")

    existing_titles, existing_urls = pull_existing_recipes()
    for card in recipe_cards:
        extension = card.get('href')
        url = base_url + extension

        try:
            download_recipe(url, existing_titles, existing_urls, source)
            print('Succeeded: ', extension)
        except Exception as e:
            print('Failed: ', extension, e)


def main():
    collection_url_list = [
        'https://cooking.nytimes.com/68861692-nyt-cooking/11249289-weekly-plan',
        'https://cooking.nytimes.com/68861692-nyt-cooking/1640510-sam-siftons-suggestions',
        'https://cooking.nytimes.com/68861692-nyt-cooking/16596-healthy-breakfast-ideas',
        'https://cooking.nytimes.com/68861692-nyt-cooking/26963-53-weekend-breakfast-ideas',
        'https://cooking.nytimes.com/68861692-nyt-cooking/475694-easy-weeknight-noodles',
        'https://cooking.nytimes.com/68861692-nyt-cooking/562858-so-many-smoothies-so-little-time',
        'https://cooking.nytimes.com/68861692-nyt-cooking/638891-best-soup-stew-recipes',
        'https://cooking.nytimes.com/68861692-nyt-cooking/12303650-our-best-vegetarian-soups-and-stews',
        # 'https://cooking.nytimes.com/68861692-nyt-cooking/442044-quick-stir-fries',
        # 'https://cooking.nytimes.com/68861692-nyt-cooking/22792-best-tofu-recipes',
        # 'https://cooking.nytimes.com/68861692-nyt-cooking/413086-easy-pasta-recipes',
        # 'https://cooking.nytimes.com/68861692-nyt-cooking/42777420-our-most-popular-recipes-of-2022',
        # 'https://cooking.nytimes.com/topics/our-most-popular-recipes',
        # 'https://cooking.nytimes.com/topics/easy-weeknight',
        'https://cooking.nytimes.com/68861692-nyt-cooking/1604305-easy-weeknight-dinners'
        # 'https://cooking.nytimes.com/35208363-sam-sifton/29654275-our-50-most-popular-vegetarian-recipes-of-2020',
        # 'https://cooking.nytimes.com/42668502-kim-severson/29190084-51-vegetarian-dishes-you-can-cook-in-30-minutes-or-fewer'
        # 'https://www.bonappetit.com/simple-cooking/weeknight-meals', FAILED!
        # 'https://www.bonappetit.com/simple-cooking/quick',
        # 'https://cooking.nytimes.com/topics/what-to-cook-this-week',
        'https://cooking.nytimes.com/68861692-nyt-cooking/17098-easy-salad-recipes',
        'https://cooking.nytimes.com/68861692-nyt-cooking/970976-vegetarian-comfort-food',
        'https://cooking.nytimes.com/68861692-nyt-cooking/2576790-easy-chicken-recipes',
        'https://cooking.nytimes.com/68861692-nyt-cooking/2110373-healthy-weeknight-dinners',
        'https://cooking.nytimes.com/68861692-nyt-cooking/2274598-easy-30-minute-vegetarian-recipes',
        'https://cooking.nytimes.com/68861692-nyt-cooking/2556520-lentil-soups-dals-and-stews',
        'https://cooking.nytimes.com/68861692-nyt-cooking/2780462-best-vegetarian-pasta-recipes',
    ]

    non_collections = {
        'AllRecipes': [
            'https://www.allrecipes.com/recipe/13883/manicotti/',
            'https://www.allrecipes.com/recipe/18417/spanakopita-greek-spinach-pie/',
            'https://www.allrecipes.com/recipe/20876/crustless-spinach-quiche/',
            'https://www.allrecipes.com/recipe/193187/tomato-basil-penne-pasta/',
            'https://www.allrecipes.com/recipe/16641/red-lentil-curry/',
            'https://www.allrecipes.com/recipe/16765/veggie-pot-pie/',

        ]

    }

    for url in collection_url_list:
        scrape_collection(url)
    existing_titles, existing_urls = pull_existing_recipes()
    for source, url_list in non_collections.items():
        for url in url_list:
            download_recipe(url, existing_titles, existing_urls, source)


if __name__ == '__main__':
    main()
