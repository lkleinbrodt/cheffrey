import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import RecipeCard from "./RecipeCard";
const RecipeGrid = ({ recipes }) => {
  const handlePress = () => {
    // Handle press
  };

  const handleSaveToOrRemoveFromList = () => {
    // Handle press
  };

  const handleToggleFavorites = () => {
    // Handle press
  };

  return (
    <ScrollView>
      <View style={styles.GridContainer}>
        {recipes.map((recipe) => (
          <RecipeCard recipe={recipe} key={recipe.id} />
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  GridContainer: {
    flex: 1,
    marginBottom: 16,
    justifyContent: "center",
    alignItems: "center",
  },
});

export default RecipeGrid;
