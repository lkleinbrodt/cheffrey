from elasticsearch import Elasticsearch

# from cheffrey.src import cheffrey
# Connect to Elasticsearch
es = Elasticsearch()

# Define the index name
index_name = "recipes"


# Create the index with mapping
def create_index():
    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "ingredients": {"type": "text"},
                "instructions": {"type": "text"},
            }
        }
    }

    es.indices.create(index=index_name, body=index_body)
    print(f"Index '{index_name}' created successfully")


# Index the recipe data
def index_recipes(recipes):
    for recipe in recipes:
        doc = {
            "title": recipe["title"],
            "ingredients": recipe["ingredients"],
            "instructions": recipe["instructions"],
        }

        es.index(index=index_name, body=doc)

    print(f"{len(recipes)} recipes indexed successfully")


# Example recipe data in JSON format
recipe_data = list(cheffrey.load_local_recipes().values())

# Create the index and index the recipe data
create_index()
index_recipes(recipe_data)
