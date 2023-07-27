import numpy as np
import json
import re
from dotenv import load_dotenv
import cheffrey
from config import ROOT_DIR

load_dotenv()

model = cheffrey.load_embedding_model()
recipes = cheffrey.load_local_recipes()


def remove_non_alphabetic_chars(string):
    # Use regular expressions to remove non-alphabetic characters
    cleaned_string = re.sub(r"[^a-zA-Z]", "", string)
    return cleaned_string


def recipe_embedding(recipe):
    d = {"title": 1, "instructions": 1, "ingredients": 1, "category": 3}

    l = []
    for type, modifier in d.items():
        text = recipe[type]
        if type == "ingredients":
            text = " ".join(text)
            text = remove_non_alphabetic_chars(text)
        embeddings = cheffrey.get_embedding(model, title)
        if embeddings is not None:
            l.append(embeddings * modifier)

    if len(l) == 0:
        return np.zeros(shape=(model.vector_size))

    recipe_embeddings = np.column_stack([l])
    recipe_embeddings = np.mean(recipe_embeddings, axis=0)

    return recipe_embeddings


# Generate embeddings for each recipe
recipe_embeddings = {}

for title, recipe in recipes.items():
    recipe_embeddings[title] = recipe_embedding(recipe)

from annoy import AnnoyIndex

# Create an AnnoyIndex with the desired embedding dimensions
embedding_dim = model.vector_size
annoy_index = AnnoyIndex(embedding_dim, metric="euclidean")

# Add the recipe embeddings to the AnnoyIndex
# generate sequential ID as you go for use in retrieval
for i, (title, embedding) in enumerate(recipe_embeddings.items()):
    annoy_index.add_item(i, embedding)
    recipes[title]["uid"] = i

with open(ROOT_DIR / "data/recipes.json", "w") as f:
    json.dump(recipes, f)

# Build the index to enable searching
annoy_index.build(n_trees=1000)
annoy_index.save(str(ROOT_DIR / "data/annoy_index.ann"))
