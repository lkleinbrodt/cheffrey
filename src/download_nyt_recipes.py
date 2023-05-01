from cheffrey import *
from recipe_scrapers import scrape_me as scrape_recipe
from bs4 import BeautifulSoup
import requests
import os


def pull_existing_recipes():
    """
    Return a tuple with titles and URLs of existing recipes stored in an S3 bucket.

    Returns:
      tuple: A tuple contains the titles and URLs of existing recipes."""
    "Return a tuple with titles and URLs of existing recipes stored in an S3 bucket.\n\n    Returns:\n      tuple: A tuple contains the titles and URLs of existing recipes.\n    "
    "Return a tuple with titles and URLs of existing recipes stored in an S3 bucket.\n\n    Returns:\n      tuple: A tuple contains the titles and URLs of existing recipes.\n    "
    master_recipes = load_s3_recipes()
    titles = list(master_recipes.keys())
    urls = [r["URL"] for r in master_recipes.values()]
    return (titles, urls)


def download_recipe(url_to_download, existing_titles, existing_urls):
    """Download recipe from given url and add to recipe database.

    Check if url_to_download is already in the database. If so,
    then returns without downloading the recipe. Then scrapes the
    recipe from the given url and parse it. Checks if recipe title is
    already in the existing_titles. If so, it skips the recipe.
    Otherwise, adds the recipe to the database and writes to
    recipe file.

    Args:
        url_to_download (str): The url to download the recipe from.
        existing_titles (List[str]): A list of existing recipe titles.
        existing_urls (List[str]): A list of existing recipe urls.

    Returns:
        None.

    Raises:
        Any errors raised by scrape_recipe() or add_to_recipe_file().

    Restrictions:
        Can only be used to download recipes from valid urls."""
    "Download recipe from given url and add to recipe database.\n\n    Check if url_to_download is already in the database. If so,\n    then returns without downloading the recipe. Then scrapes the\n    recipe from the given url and parse it. Checks if recipe title is\n    already in the existing_titles. If so, it skips the recipe.\n    Otherwise, adds the recipe to the database and writes to\n    recipe file.\n\n    Args:\n        url_to_download (str): The url to download the recipe from.\n        existing_titles (List[str]): A list of existing recipe titles.\n        existing_urls (List[str]): A list of existing recipe urls.\n\n    Returns:\n        None.\n\n    Raises:\n        Any errors raised by scrape_recipe() or add_to_recipe_file().\n\n    Restrictions:\n        Can only be used to download recipes from valid urls.\n"
    "Download recipe from given url and add to recipe database.\n\n    Check if url_to_download is already in the database. If so,\n    then returns without downloading the recipe. Then scrapes the\n    recipe from the given url and parse it. Checks if recipe title is\n    already in the existing_titles. If so, it skips the recipe.\n    Otherwise, adds the recipe to the database and writes to\n    recipe file.\n\n    Args:\n        url_to_download (str): The url to download the recipe from.\n        existing_titles (List[str]): A list of existing recipe titles.\n        existing_urls (List[str]): A list of existing recipe urls.\n\n    Returns:\n        None.\n\n    Raises:\n        Any errors raised by scrape_recipe() or add_to_recipe_file().\n\n    Restrictions:\n        Can only be used to download recipes from valid urls."
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

    Given the URL of a collection page, downloads all recipe pages linked from it.
    Downloads the HTML and saves it in the /data directory.
    On each download, checks if the recipe already exists in the /data directory based on title or URL.
    If the recipe already exists, it is not downloaded again.
    This function calls download_recipe() function internally.

    Args:
    collection_url (str): The URL of the collection page.

    Returns:
    None"""
    "Download recipes from a New York Times cooking collection page.\n\n    Given the URL of a collection page, downloads all recipe pages linked from it.\n    Downloads the HTML and saves it in the /data directory.\n    On each download, checks if the recipe already exists in the /data directory based on title or URL.\n    If the recipe already exists, it is not downloaded again.\n    This function calls download_recipe() function internally.\n\n    Args:\n    collection_url (str): The URL of the collection page.\n\n    Returns:\n    None"
    "Download recipes from a New York Times cooking collection page.\n\n    Given the URL of a collection page, downloads all recipe pages linked from it.\n    Downloads the HTML and saves it in the /data directory.\n    On each download, checks if the recipe already exists in the /data directory based on title or URL.\n    If the recipe already exists, it is not downloaded again.\n    This function calls download_recipe() function internally.\n\n    Args:\n    collection_url (str): The URL of the collection page.\n\n    Returns:\n    None"
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
    """
    Download NY Times recipes from a list of URLs.

    Downloads recipe data from the New York Times website listed in url_list using the `download_nyt_recipes` method.

    Args:
        None.

    Returns:
        None.

    Raises:
        None

    Example:
        url_list = ['https://cooking.nytimes.com/recipes/12345']
        main(url_list)"""
    "\n    Download NY Times recipes from a list of URLs.\n    \n    This function downloads recipe data from the New York Times website listed in url_list using the `download_nyt_recipes` method.\n    \n    Args:\n        None.\n    \n    Returns:\n        None.\n    \n    Raises:\n        None\n    \n    Example:\n        url_list = ['https://cooking.nytimes.com/recipes/12345']\n        main(url_list)\n    "
    "Download NY Times recipes from a list of URLs.\n\n    Downloads recipe data from New York Times website listed in url_list using `download_nyt_recipes` method.\n\n    Args:\n        None.\n\n    Returns:\n        None.\n\n    Raises:\n        None\n\n    Example:\n        url_list = ['https://cooking.nytimes.com/recipes/12345']\n        main(url_list)\n    "
    url_list = []
    for url in url_list:
        download_nyt_recipes(url)


if __name__ == "__main__":
    main()
