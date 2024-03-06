import { React, useEffect, useState, useContext } from "react";
import { StyleSheet, ActivityIndicator, Text } from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import { Button } from "../components/Button";

const Explore = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [page, setPage] = useState(1);
  const [pageLoading, setPageLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const onRefresh = async () => {
    await recipesAPI.refreshExplore();
    setPage(1);
    setRecipes([]);
    fetchRecipes(1);
  };

  const fetchRecipes = async (pageNumber) => {
    console.log("Fetching page number: ", pageNumber);
    setLoading(true);
    const response = await recipesAPI.loadRandomRecipes(pageNumber);
    if (!response.ok) return setError(true);

    setRecipes((prevRecipes) => [...prevRecipes, ...response.data.recipes]);
    setLoading(false);
  };

  const handleScrollToBottom = () => {
    // Increment the page and fetch new recipes
    setLoading(true);
    const nextPage = page + 1;
    if (nextPage > 10) {
      setRecipes([]);
    }
    fetchRecipes(nextPage);
    setPage(nextPage);
  };

  useEffect(() => {
    setPageLoading(true);
    fetchRecipes(page);
    setPageLoading(false);
  }, []);

  return (
    <Screen style={styles.screen}>
      {error && (
        <>
          <AppText>Couldn't retrieve the recipes.</AppText>
          <Button title="Retry" onPress={() => fetchRecipes(page)} />
        </>
      )}
      <LottieActivityIndicator key="loading1" visible={pageLoading} />
      <RecipeGrid
        recipes={recipes}
        navigation={navigation}
        onScrollToBottom={handleScrollToBottom}
        onRefresh={onRefresh}
      />
      {loading && (
        <ActivityIndicator
          style={styles.loading}
          size="large"
          color={colors.primary}
        />
      )}
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
