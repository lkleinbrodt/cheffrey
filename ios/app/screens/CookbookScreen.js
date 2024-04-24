import { React, useEffect, useState, useContext } from "react";
import { StyleSheet, ActivityIndicator } from "react-native";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import SearchBar from "../components/SearchBar";
import routeNames from "../navigation/routeNames";
import { ScrollView } from "react-native-gesture-handler";
import Message from "../components/Message";
import Button from "../components/Button";
import { View } from "react-native";

const Cookbook = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  //   const [page, setPage] = useState(1);
  const [pageLoading, setPageLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  //   const [maxPages, setMaxPages] = useState(10);
  const [error, setError] = useState(false);
  const [query, setQuery] = useState("");

  const onSearch = async (query) => {
    console.log("not implemented");
    // setQuery(query);
    // if (!query) {
    // //   setMaxPages(10);
    // //   setPage(1);
    //   setPageLoading(true);
    //   fetchExploreRecipes(1);
    //   setPageLoading(false);
    // } else {
    //   setPageLoading(true);
    //   setRecipes([]);
    //   setPage(1);
    //   fetchSearchRecipes(query, 1);
    //   setPageLoading(false);
    // }
  };

  const onRefresh = async () => {
    setRecipes([]);
    setQuery("");
    await fetchRecipes();
  };

  const fetchRecipes = async () => {
    setLoading(true);
    const response = await recipesAPI.loadCookbook();
    if (!response.ok) return setError(true);
    setRecipes(response.data.recipes);
    setLoading(false);
  };

  //   const fetchSearchRecipes = async (query, pageNumber) => {
  //     setLoading(true);
  //     const response = await recipesAPI.searchRecipes(query, pageNumber);
  //     if (!response.ok) return setError(true);
  //     setRecipes((prevRecipes) => [...prevRecipes, ...response.data.recipes]);
  //     setLoading(false);
  //   };

  const Header = () => {
    return (
      <View style={styles.header}>
        <SearchBar onSearch={onSearch} />
        <Button title="Add New Recipe" onPress={addNewRecipe} width="50%" />
      </View>
    );
  };

  const addNewRecipe = () => {
    //take you to the add recipe screen
    navigation.navigate(routeNames.COOKBOOK_EDIT_RECIPE, {
      recipe: {},
      title: "New Recipe",
      fromCookbook: true,
    });
  };

  useEffect(() => {
    setPageLoading(true);
    fetchRecipes();
    setPageLoading(false);
  }, []);

  if (pageLoading) {
    return (
      <Screen style={styles.screen}>
        <SearchBar onSearch={onSearch} />
        <ActivityIndicator
          style={styles.pageLoading}
          size="large"
          color={colors.primary}
        />
      </Screen>
    );
  }

  if (recipes.length === 0) {
    return (
      <Screen style={styles.emptyScreen}>
        <Message message="Your cookbook is empty!" />
        <View
          style={{
            width: "50%",
            alignSelf: "center",
          }}
        >
          <Button title="Add New Recipe" onPress={addNewRecipe} />
        </View>

        <Message
          message=""
          subMessage="Or use the explore page to discover new ones!"
        />
      </Screen>
    );
  }

  return (
    <Screen style={styles.screen}>
      {/* button to add new recipe */}

      <RecipeGrid
        recipes={recipes}
        navigation={navigation}
        navigateScreen={routeNames.COOKBOOK_RECIPE_DETAILS}
        onScrollToBottom={() => {}}
        onRefresh={onRefresh}
        searchBar={Header}
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
  header: {
    flexDirection: "column",
    justifyContent: "space-between",
    alignItems: "center",
  },
  emptyScreen: {
    backgroundColor: colors.background,
    justifyContent: "center",
    alignItems: "center",
    gap: 5,
    paddingVertical: 100,
  },
  pageLoading: {
    position: "absolute",
    top: "50%",
    alignSelf: "center",
  },
  loading: {
    position: "absolute",
    bottom: 20,
    alignSelf: "center",
  },
});

export default Cookbook;
