import client from "./client";

function loadRandomRecipes(page = 1) {
  return client.get("/load-more-recipes/", { page });
}

export default {
  loadRandomRecipes,
};
