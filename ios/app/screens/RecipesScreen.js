import { React, useEffect, useState } from "react";
import { View, Text, Alert, StyleSheet, Button } from "react-native";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import useAuth from "../auth/useAuth";
import Message from "../components/Message";

const RecipeList = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const auth = useAuth();

  const fetchRecipes = async () => {
    console.log("fetching recipes");
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

  return (
    <Screen style={styles.screen}>
      <View>
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
            onScrollToBottom={() => {}}
            onRefresh={() => {}}
          />
        )}
        <Button title="Clear List" onPress={clearList} />
        <Button title="Logout" onPress={() => auth.logOut()} />
      </View>
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    backgroundColor: colors.background,
  },
});
export default RecipeList;
