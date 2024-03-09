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

const CookedScreen = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [pageLoading, setPageLoading] = useState(false);
  const [error, setError] = useState(false);

  const onRefresh = async () => {
    setPageLoading(true);
    fetchRecipes();
    setPageLoading(false);
  };

  const fetchRecipes = async () => {
    const response = await recipesAPI.loadCooked();
    if (!response.ok) return setError(true);
    setRecipes(response.data.cooked);
  };

  useEffect(() => {
    setPageLoading(true);
    fetchRecipes();
    setPageLoading(false);
  }, []);

  const handleScrollToBottom = () => {};

  return (
    <Screen style={styles.screen}>
      <LottieActivityIndicator key="loading1" visible={pageLoading} />
      {recipes.length === 0 ? (
        <Message
          message="No cooked recipes yet."
          subMessage="Get to cooking!"
        />
      ) : (
        <RecipeGrid
          recipes={recipes}
          navigation={navigation}
          navigateScreen={routes.COOKED_RECIPE_DETAILS}
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

export default CookedScreen;
