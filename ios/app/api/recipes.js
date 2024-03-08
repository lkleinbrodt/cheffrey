import client from "./client";

function loadRandomRecipes(page = 1) {
  return client.get("/load-more-recipes/", { page });
}

function loadRecipeList() {
  return client.get("/recipe-list");
}

function refreshExplore() {
  return client.get("/refresh-explore");
}

function toggleRecipeInList(recipe_id) {
  return client.post("/toggle-recipe-in-list/", { recipe_id });
}

function toggleRecipeInFavorites(recipe_id) {
  return client.post("/toggle-favorite/", { recipe_id });
}

function clearRecipeList() {
  return client.post("/clear-recipe-list");
}

function loadFavorites() {
  return client.get("/get-favorites");
}
function loadCooked() {
  return client.get("/get-cooked");
}

function loadShoppingList() {
  return client.get("/get-shopping-list");
}

function searchRecipes(query, page) {
  return client.post("/search-recipes/", { query, page });
}
export default {
  loadRandomRecipes,
  loadRecipeList,
  refreshExplore,
  toggleRecipeInList,
  toggleRecipeInFavorites,
  clearRecipeList,
  loadFavorites,
  loadCooked,
  loadShoppingList,
  searchRecipes,
};
