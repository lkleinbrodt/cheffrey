import { React, useEffect, useState, useContext } from "react";
import { StyleSheet, ActivityIndicator, Text } from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import { Button } from "../components/Button";
import Message from "../components/Message";
import routes from "../navigation/routes";

const FavoritesScreen = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState(false);

  const onRefresh = async () => {
    setPageLoading(true);
    fetchRecipes();
    setPageLoading(false);
  };

  const fetchRecipes = async () => {
    setPageLoading(true);
    const response = await recipesAPI.loadFavorites();
    if (!response.ok) return setError(true);
    setRecipes(response.data.favorites);
    setPageLoading(false);
  };

  useEffect(() => {
    fetchRecipes();
  }, []);

  const handleScrollToBottom = () => {};

  if (pageLoading) {
    return (
      <Screen style={styles.screen}>
        <LottieActivityIndicator key="loading1" visible={pageLoading} />
      </Screen>
    );
  }

  return (
    <Screen style={styles.screen}>
      {recipes.length === 0 ? (
        <Message message="No favorites yet." subMessage="Get to browsing!" />
      ) : (
        <RecipeGrid
          recipes={recipes}
          navigation={navigation}
          navigateScreen={routes.FAVORITES_RECIPE_DETAILS}
          onScrollToBottom={handleScrollToBottom}
          onRefresh={onRefresh}
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

export default FavoritesScreen;
