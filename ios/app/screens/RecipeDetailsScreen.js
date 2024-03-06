import React from "react";
import { View, Text, Image, TouchableOpacity } from "react-native";
import colors from "../config/colors";
import Screen from "../components/Screen";

const RecipeDetailsScreen = ({ route }) => {
  console.log(route);

  const recipe = route.params.recipe;
  console.log(recipe.title);

  return (
    <View>
      <Image
        source={{ uri: recipe.image_url }}
        style={styles.image}
        alt={recipe.title}
      />
      <View style={styles.detailsContainer}>
        <Text style={styles.title}>{recipe.title}</Text>
        <Text style={styles.description}>{recipe.description}</Text>
      </View>
    </View>
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
    fontSize: 24,
    fontWeight: "500",
  },
};

export default RecipeDetailsScreen;
