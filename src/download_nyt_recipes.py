from cheffrey import *
from recipe_scrapers import scrape_me as scrape_recipe
from bs4 import BeautifulSoup
import requests
import os


def pull_existing_recipes():
    """
    Return a tuple of titles and URLs of existing recipes stored in an S3 bucket.

    Returns:
      tuple: A tuple containing the titles and URLs of existing recipes."""
    master_recipes = load_s3_recipes()
    titles = list(master_recipes.keys())
    urls = [r["URL"] for r in master_recipes.values()]
    return (titles, urls)


def download_recipe(url_to_download, existing_titles, existing_urls):
    """
    Download a recipe from a url and add it to the database.

        Check if the url is already present in the existing urls. If so,
        return without downloading the recipe. Otherwise, scrape the
        recipe from the given url and parse it. Check if the recipe title
        is already in the existing recipe titles. If so, skip recipe.
        Otherwise, add the recipe to the database and write to recipe file.

        Args:
            url_to_download (str): The url to download the recipe from.
            existing_titles (List[str]): A list of existing recipe titles.
            existing_urls (List[str]): A list of existing recipe urls.

        Returns:
            None.

        Raises:
            Any errors raised by scrape_recipe() or add_to_recipe_file() functions.

        Restrictions:
            The function can only be used to download recipes from valid urls."""

    if url_to_download in existing_urls:
        print(f"Skipping. Already in database")
        return
    recipe = scrape_recipe(url_to_download)
    recipe = parse_scraped_recipe(recipe)
    if recipe["Title"] in existing_titles:
        return
    recipe["URL"] = url_to_download
    add_to_recipe_file(recipe, overwrite=True)


def download_nyt_recipes(collection_url):
    """Download recipes from a New York Times cooking collection page.

    Downloads all recipe pages linked from the provided cooking collection URL. It internally checks if the recipe already exists in the /data directory based on title or URL before downloading it again.

    Args:
        collection_url (str): The URL of the New York Times cooking collection page.

    Returns:
        None"""

    base_url = "https://cooking.nytimes.com/"
    res = requests.get(collection_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, features="lxml")
    recipe_cards = soup.find_all("a", {"class": "image-anchor card-link"})
    (existing_titles, existing_urls) = pull_existing_recipes()
    for card in recipe_cards:
        extension = card.get("href")
        url = base_url + extension
        try:
            download_recipe(url, existing_titles, existing_urls)
            print("Succeeded: ", extension)
        except Exception as e:
            print("Failed: ", extension, e)


def main():
    """Download NY Times recipes from a list of URLs. This function downloads recipe data from the New York Times website listed in url_list using the `download_nyt_recipes` method. Returns None."""

    url_list = []
    for url in url_list:
        download_nyt_recipes(url)


if __name__ == "__main__":
    main()
