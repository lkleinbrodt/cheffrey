import { React, useEffect, useState, useContext } from "react";
import { StyleSheet, ActivityIndicator } from "react-native";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import SearchBar from "../components/SearchBar";
import routeNames from "../navigation/routeNames";
import { ScrollView } from "react-native-gesture-handler";
import { Text } from "react-native";
import Icon from "../components/Icon";

const Explore = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [page, setPage] = useState(1);
  const [pageLoading, setPageLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [maxPages, setMaxPages] = useState(10);
  const [error, setError] = useState(false);
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
    setError(false);
    console.log("refreshing");
    // setPageLoading(true);
    setRecipes([]);
    setQuery("");
    await recipesAPI.refreshExplore();
    setPage(1);
    await fetchExploreRecipes(1);
    // setPageLoading(false);
  };

  const fetchExploreRecipes = async (pageNumber) => {
    setError(false);
    setLoading(true);
    const response = await recipesAPI.loadRandomRecipes(pageNumber);
    if (!response.ok) {
      setLoading(false);
      return setError(true);
    }

    //remove any recipes in the response that are already in the list
    //#TODO: can we be more efficient here?
    const newRecipes = response.data.recipes.filter(
      (recipe) => !recipes.some((r) => r.id === recipe.id)
    );

    setRecipes((prevRecipes) => [...prevRecipes, ...newRecipes]);
    setLoading(false);
  };

  const fetchSearchRecipes = async (query, pageNumber) => {
    setError(false);
    setLoading(true);
    const response = await recipesAPI.searchRecipes(query, pageNumber);
    if (!response.ok) {
      setLoading(false);

      return setError(true);
    }
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

  if (error) {
    return (
      <Screen style={styles.screen}>
        <SearchBar onSearch={onSearch} />
        <ScrollView
          contentContainerStyle={{
            flex: 1,
            justifyContent: "center",
            alignItems: "center",
            alignSelf: "center",
            textAlign: "center",
            gap: 20,
            padding: 20,
          }}
        >
          <Text
            style={{
              textAlign: "center",
            }}
          >
            There was an error loading recipes.
          </Text>
          <Icon
            name="refresh"
            size={50}
            color={colors.danger}
            backgroundColor={colors.primary}
            onPress={onRefresh}
          />
          <Text
            style={{
              textAlign: "center",
            }}
          >
            If the problem persists, try closing and reopening the app.
          </Text>
          <Text>{error}</Text>
        </ScrollView>
      </Screen>
    );
  }

  return (
    <Screen style={styles.screen}>
      <RecipeGrid
        recipes={recipes}
        navigation={navigation}
        navigateScreen={routeNames.FEED_RECIPE_DETAILS}
        onScrollToBottom={handleScrollToBottom}
        onRefresh={onRefresh}
        header={<SearchBar onSearch={onSearch} />}
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

export default Explore;
