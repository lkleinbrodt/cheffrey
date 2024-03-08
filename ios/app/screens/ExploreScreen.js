import { React, useEffect, useState, useContext } from "react";
import { StyleSheet, ActivityIndicator, Text, Button } from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import SearchBar from "../components/SearchBar";
import routes from "../navigation/routes";

const Explore = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [page, setPage] = useState(1);
  const [pageLoading, setPageLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [atBottom, setAtBottom] = useState(false);
  const [maxPages, setMaxPages] = useState(10);
  const [query, setQuery] = useState("");

  const onSearch = async (query) => {
    setQuery(query);
    if (!query) {
      setMaxPages(10);
      setPage(1);
      setPageLoading(true);
      fetchExploreRecipes(1);
      setPageLoading(false);
    } else {
      setPageLoading(true);
      setRecipes([]);
      setPage(1);
      fetchSearchRecipes(query, 1);
      setPageLoading(false);
    }
  };

  const onRefresh = async () => {
    setPageLoading(true);
    setRecipes([]);
    setQuery("");
    await recipesAPI.refreshExplore();
    setPage(1);
    await fetchExploreRecipes(1);
    setPageLoading(false);
  };

  const fetchExploreRecipes = async (pageNumber) => {
    setLoading(true);
    const response = await recipesAPI.loadRandomRecipes(pageNumber);
    if (!response.ok) return setError(true);

    setRecipes((prevRecipes) => [...prevRecipes, ...response.data.recipes]);
    setLoading(false);
  };

  const fetchSearchRecipes = async (query, pageNumber) => {
    setLoading(true);
    const response = await recipesAPI.searchRecipes(query, pageNumber);
    if (!response.ok) return setError(true);
    setRecipes((prevRecipes) => [...prevRecipes, ...response.data.recipes]);
    setLoading(false);
  };

  const handleScrollToBottom = () => {
    const nextPage = page + 1;
    if (nextPage > maxPages) {
      return;
    }
    if (query) {
      fetchSearchRecipes(query, nextPage);
    } else {
      fetchExploreRecipes(nextPage);
    }
    setPage(nextPage);
  };

  useEffect(() => {
    setPageLoading(true);
    fetchExploreRecipes(page);
    setPageLoading(false);
  }, []);

  return (
    <Screen style={styles.screen}>
      <RecipeGrid
        recipes={recipes}
        navigation={navigation}
        navigateScreen={routes.FEED_RECIPE_DETAILS}
        onScrollToBottom={handleScrollToBottom}
        onRefresh={onRefresh}
        searchBar={<SearchBar onSearch={onSearch} />}
      />
      {loading && (
        <ActivityIndicator
          style={styles.loading}
          size="large"
          color={colors.primary}
        />
      )}
      <LottieActivityIndicator key="loading1" visible={pageLoading} />
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    backgroundColor: colors.background,
  },
  loading: {
    position: "absolute",
    bottom: 16,
    alignSelf: "center",
  },
});

export default Explore;
