import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import RecipeCard from "./RecipeCard";
import routes from "../navigation/routes";
const RecipeGrid = ({ recipes, navigation, onScrollToBottom }) => {
  const handleScroll = (event) => {
    const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;

    const isCloseToBottom =
      layoutMeasurement.height + contentOffset.y >= contentSize.height - 100;

    if (isCloseToBottom) {
      onScrollToBottom();
    }
  };

  return (
    <ScrollView onScroll={handleScroll} scrollEventThrottle={0}>
      <View style={styles.GridContainer}>
        {recipes.map((recipe) => (
          <RecipeCard
            recipe={recipe}
            key={recipe.id}
            onPress={() =>
              navigation.navigate(routes.RECIPE_DETAILS, { recipe })
            }
          />
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
