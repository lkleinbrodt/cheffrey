import { React, useEffect, useState } from "react";
import { View, Text, Alert, StyleSheet, Button } from "react-native";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import useAuth from "../auth/useAuth";

const RecipeList = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const auth = useAuth();

  const fetchRecipes = async () => {
    setLoading(true);
    const response = await recipesAPI.loadRecipeList();
    if (!response.ok) return setError(true);
    console.log(response);
    setRecipes(response.data.recipes);
    setLoading(false);
  };

  useEffect(() => {
    fetchRecipes();
  }, [navigation]);

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
          <Text>Add recipes to your list to see them here.</Text>
        ) : (
          <RecipeGrid recipes={recipes} />
        )}
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
