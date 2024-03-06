import { React, useEffect, useState } from "react";
import { StyleSheet, ActivityIndicator } from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import axios from "../components/axios";
import RecipeGrid from "../components/RecipeGrid";
import * as SecureStore from "expo-secure-store";
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

  useEffect(() => {
    SecureStore.getItemAsync("token").then((token) => {
      if (token) {
        console.log("Token exists:", token);
        axios.defaults.headers["Authorization"] = `Bearer ${token}`;
      } else {
        console.log("Token does not exist, redirecting to login");
        navigation.replace("login");
      }
    });
  }, []);

  const fetchRecipes = async (pageNumber) => {
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
