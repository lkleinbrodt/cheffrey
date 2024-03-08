import React from "react";
import { View, Text, Image, ScrollView } from "react-native";
import colors from "../config/colors";

const RecipeDetailsScreen = ({ route }) => {
  const recipe = route.params.recipe;

  //convert recipe.ingredients from string to array
  //it is stored like this: "['ingredient1', 'ingredient2', 'ingredient3']"
  recipe.ingredients = recipe.ingredients
    .replace("[", "")
    .replace("]", "")
    .replace(/'/g, "")
    .split(", ");

  const renderIngredientItem = ({ item, key }) => (
    <Text key={key} style={styles.ingredientsItem}>{`\u2022 ${item}`}</Text>
  );

  return (
    <ScrollView>
      <Image
        source={{ uri: recipe.image_url }}
        style={styles.image}
        alt={recipe.title}
      />
      <View style={styles.detailsContainer}>
        <Text style={styles.title}>{recipe.title}</Text>
        <View style={styles.hr} />
        <Text style={styles.description}>{recipe.description}</Text>
        <Text style={styles.subtitle}>Ingredients</Text>
        <View style={styles.hr} />
        <View style={styles.ingredientsContainer}>
          {recipe.ingredients.map((ingredient, index) =>
            renderIngredientItem({ item: ingredient, key: index })
          )}
        </View>
        <Text style={styles.subtitle}>Instructions</Text>
        <View style={styles.hr} />
        <Text style={styles.instructions}>{recipe.instructions}</Text>
      </View>
    </ScrollView>
  );
};

const styles = {
  detailsContainer: {
    padding: 20,
  },
  image: {
    width: "100%",
    height: 300,
  },
  price: {
    color: colors.secondary,
    fontWeight: "bold",
    fontSize: 20,
    marginVertical: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: colors.primary,
  },
  subtitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: colors.primary,
    marginTop: 10,
  },
  hr: {
    height: 1,
    backgroundColor: "#333333",
    marginVertical: 5,
  },
  description: {
    fontSize: 16,
    color: "#333333",
  },
};

export default RecipeDetailsScreen;
