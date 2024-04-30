import React, { useState } from "react";
import { View, Text, Image, ScrollView, TouchableOpacity } from "react-native";
import colors from "../config/colors";
import recipesAPI from "../api/recipes";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import useAuth from "../auth/useAuth";
import routeNames from "../navigation/routeNames";
import Message from "../components/Message";

const RecipeDetailsScreen = ({ navigation, route }) => {
  const recipe = route.params.recipe;
  const auth = useAuth();
  const user = auth.user;

  const [isSaved, setIsSaved] = useState(recipe.in_recipe_list);
  const [isInCookbook, setIsInCookbook] = useState(recipe.in_cookbook);

  const handleSavePress = () => {
    recipesAPI.toggleRecipeInList(recipe.id);
    setIsSaved(!isSaved);
  };
  const handleCookbookPress = () => {
    recipesAPI.toggleInCookbook(recipe.id);
    setIsInCookbook(!isInCookbook);
  };

  const editRecipe = () => {
    if (route.name == routeNames.RECIPES_RECIPE_DETAILS) {
      navigation.navigate(routeNames.RECIPES_EDIT_RECIPE, { recipe });
    } else if (route.name == routeNames.COOKBOOK_RECIPE_DETAILS) {
      navigation.navigate(routeNames.COOKBOOK_EDIT_RECIPE, { recipe });
    } else {
      console.log("Error: route name not recognized");
    }
  };

  if (typeof recipe.ingredients === "string") {
    recipe.ingredients = recipe.ingredients.split(", ");
  }
  if (typeof recipe.instructions === "string") {
    recipe.instructions = recipe.instructions.split("\n");
  }

  const renderIngredientItem = ({ item, key }) => (
    <Text key={key} style={styles.ingredientsItem}>{`\u2022 ${item}`}</Text>
  );
  const renderInstructionItem = ({ item, key }) => (
    <Text key={key} style={styles.instructionsItem}>{`${
      key + 1
    }. ${item}`}</Text>
  );

  return (
    <ScrollView>
      {/* if no image_url, show placeholder */}
      {recipe.image_url ? (
        <Image
          source={{ uri: recipe.image_url }}
          style={styles.image}
          alt={recipe.title}
        />
      ) : (
        <View style={styles.image}>
          <Text style={styles.message}>No Available Image</Text>
        </View>
      )}

      <View style={styles.detailsContainer}>
        <Text style={styles.title}>{recipe.title}</Text>
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[
              styles.saveButton,
              {
                backgroundColor: isSaved ? colors.danger : colors.primary,
              },
            ]}
            onPress={handleSavePress}
          >
            <Text style={styles.buttonText}>
              {isSaved ? "Remove from List" : "Add to List"}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={{
              padding: 10,
              borderRadius: 50,
            }}
            onPress={handleCookbookPress}
          >
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <MaterialCommunityIcons
                name={isInCookbook ? "notebook" : "notebook-outline"}
                size={32}
                color={colors.primary}
              />
              <View
                style={[
                  styles.iconBadge,
                  {
                    backgroundColor: isInCookbook
                      ? colors.danger
                      : colors.primary,
                  }, // Add a comma after the closing square bracket
                ]}
              >
                <MaterialCommunityIcons
                  name={isInCookbook ? "minus" : "plus"}
                  size={12}
                  color={colors.white}
                />
              </View>
            </View>
          </TouchableOpacity>
        </View>

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
        <View style={styles.instructionsContainer}>
          {recipe.instructions.map((instruction, index) =>
            renderInstructionItem({ item: instruction, key: index })
          )}
        </View>

        {/* if recipe.author == user_id, then allow them to edit the recipe */}

        {recipe.author == user.id ? (
          <TouchableOpacity
            style={{
              backgroundColor: colors.primary,
              padding: 10,
              borderRadius: 5,
              marginTop: 10,
            }}
            onPress={editRecipe}
          >
            <Text style={styles.buttonText}>Edit Recipe</Text>
          </TouchableOpacity>
        ) : null}
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
    justifyContent: "center",
    alignItems: "center",
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
  buttonContainer: {
    flexDirection: "row",
    justifyContent: "space-evenly",
    alignItems: "center",
    gap: 50,
    marginLeft: 30,
  },
  saveButton: {
    padding: 10,
    borderRadius: 5,
    flex: 0.75,
    marginRight: 5,
  },
  buttonText: {
    color: "#ffffff",
    textAlign: "center",
  },
  iconBadge: {
    borderRadius: 12,
    position: "absolute",
    backgroundColor: colors.primary,
    bottom: -3,
    right: -3,
  },
  instructionsItem: {
    marginBottom: 10,
  },
};

export default RecipeDetailsScreen;
