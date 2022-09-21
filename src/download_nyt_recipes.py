from cheffrey import *
from recipe_scrapers import scrape_me as scrape_recipe
from bs4 import BeautifulSoup
import requests
import os


def pull_existing_recipes():
    master_recipes = load_yaml('recipes')
    titles = list(master_recipes.keys())
    urls = [r['URL'] for r in master_recipes.values()]
    return titles, urls


def download_recipe(url_to_download, existing_titles, existing_urls):
    if url_to_download in existing_urls:
        return
    recipe = scrape_recipe(url_to_download)
    recipe = parse_scraped_recipe(recipe)
    if recipe['Title'] in existing_titles:
        return
    recipe['URL'] = url_to_download
    # we already checked if one exists
    add_to_recipe_file(recipe, overwrite=True)


def download_nyt_recipes(collection_url):
    base_url = 'https://cooking.nytimes.com/'
    res = requests.get(collection_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features='lxml')
    recipe_cards = soup.find_all('a', {'class': 'image-anchor card-link'})

    existing_titles, existing_urls = pull_existing_recipes()
    for card in recipe_cards:
        extension = card.get('href')
        url = base_url + extension

        try:
            download_recipe(url, existing_titles, existing_urls)
            print('Succeeded: ', extension)
        except Exception as e:
            print('Failed: ', extension, e)


def main():
    url_list = [
        'https://cooking.nytimes.com/68861692-nyt-cooking/442044-quick-stir-fries',
        'https://cooking.nytimes.com/68861692-nyt-cooking/22792-best-tofu-recipes',
        'https://cooking.nytimes.com/68861692-nyt-cooking/413086-easy-pasta-recipes'
    ]
    for url in url_list:
        download_nyt_recipes(url)


if __name__ == '__main__':
    main()