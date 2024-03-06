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
export default {
  loadRandomRecipes,
  loadRecipeList,
  refreshExplore,
};
