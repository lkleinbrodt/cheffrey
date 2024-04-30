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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [query, setQuery] = useState("");

  const onSearch = async (query) => {
    console.log(query);
    setQuery(query);
    if (!query) {
      fetchRecipes();
    } else {
      setRecipes([]);
      fetchSearchRecipes(query);
    }
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

  const fetchSearchRecipes = async (query) => {
    setLoading(true);
    const response = await recipesAPI.searchCookbook(query);
    if (!response.ok) return setError(true);
    setRecipes((prevRecipes) => [...prevRecipes, ...response.data]);
    setLoading(false);
  };

  const Header = () => {
    return (
      <View style={styles.header}>
        <SearchBar onSearch={onSearch} query={query} />
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
    fetchRecipes();
  }, []);
  //if you want to refresh the page every time you navigate to it
  // useEffect(() => {
  //   const unsubscribe = navigation.addListener("focus", () => {
  //     fetchRecipes();
  //   });
  //   return unsubscribe;
  // }, [navigation]);

  if (loading) {
    return (
      <Screen style={styles.screen}>
        <ActivityIndicator
          style={styles.loading}
          size="large"
          color={colors.primary}
        />
      </Screen>
    );
  }

  if ((recipes.length === 0) & (query === "")) {
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
  } else if (recipes.length === 0) {
    return (
      <Screen style={styles.screen}>
        <Header />
        <Message message="No matching recipes" />
      </Screen>
    );
  }

  console.log(query);

  return (
    <Screen style={styles.screen}>
      <RecipeGrid
        recipes={recipes}
        navigation={navigation}
        navigateScreen={routeNames.COOKBOOK_RECIPE_DETAILS}
        onScrollToBottom={() => {}}
        onRefresh={onRefresh}
        header={Header}
      />
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
  loading: {
    position: "absolute",
    top: "50%",
    alignSelf: "center",
  },
});

export default Cookbook;
