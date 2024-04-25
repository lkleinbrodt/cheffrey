import { React, useEffect, useState } from "react";
import {
  View,
  Text,
  Alert,
  StyleSheet,
  Button,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import useAuth from "../auth/useAuth";
import Message from "../components/Message";
import routeNames from "../navigation/routeNames";

const RecipeList = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const auth = useAuth();

  const fetchRecipes = async () => {
    setLoading(true);
    const response = await recipesAPI.loadRecipeList();
    if (!response.ok) return setError(true);
    setError(false);
    setRecipes(response.data.recipes);
    setLoading(false);
  };

  useEffect(() => {
    fetchRecipes();
  }, [navigation]);

  const clearList = () => {
    //first, confirm that the user wants to clear the list
    Alert.alert(
      "Clear List",
      "Are you sure you want to clear your list?",
      [
        {
          text: "Cancel",
          onPress: () => console.log("Cancel Pressed"),
          style: "cancel",
        },
        {
          text: "OK",
          onPress: async () => {
            await recipesAPI.clearRecipeList();
            setRecipes([]);
          },
        },
      ],
      { cancelable: false }
    );
  };

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

  return (
    <Screen style={styles.screen}>
      {error && (
        <>
          <Text>Couldn't retrieve the recipes.</Text>
          <Button title="Retry" onPress={fetchRecipes} />
        </>
      )}
      {recipes.length === 0 ? (
        <Message
          message="No recipes yet."
          subMessage="Add recipes to your list to see them here."
        />
      ) : (
        <RecipeGrid
          recipes={recipes}
          navigation={navigation}
          navigateScreen={routeNames.RECIPES_RECIPE_DETAILS}
          onScrollToBottom={() => {}}
          onRefresh={fetchRecipes}
          footer={
            <TouchableOpacity style={styles.clearButton} onPress={clearList}>
              <Text style={styles.clearButtonText}>Clear List</Text>
            </TouchableOpacity>
          }
        />
      )}
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    backgroundColor: colors.background,
  },
  clearButton: {
    backgroundColor: colors.secondary,
    padding: 10,
    borderRadius: 5,
    marginVertical: 20,
    justifyContent: "center",
    width: "33%", // Fixed width of 33% of the screen
    alignSelf: "center", // Center the button horizontally
  },
  clearButtonText: {
    color: colors.primary,
    fontSize: 16,
    textAlign: "center",
  },
  loading: {
    position: "absolute",
    top: "50%",
    alignSelf: "center",
  },
});
export default RecipeList;
