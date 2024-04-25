import { React, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  TouchableWithoutFeedback,
} from "react-native";
import colors from "../config/colors";
import recipesAPI from "../api/recipes";

import { MaterialCommunityIcons } from "@expo/vector-icons"; // Import the required icon from Expo Vector Icons
import { Image } from "expo-image";

const blurhash = "L9E:C[ae3GbX?wjZEMRjt-ofw}nj";

const RecipeCard = ({ recipe, onPress }) => {
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

  return (
    <TouchableWithoutFeedback onPress={onPress}>
      <View style={styles.card}>
        <Image
          style={styles.cardImage}
          source={recipe.image_url}
          placeholder={blurhash}
          alt={recipe.title}
        />

        <View style={styles.cardBody}>
          <View style={styles.textContainer}>
            <Text style={styles.cardTitle}>{recipe.title}</Text>
            <View style={styles.hr} />
            <Text style={styles.cardText} numberOfLines={5}>
              {recipe.description}
            </Text>
          </View>
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
                backgroundColor: colors.white,
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
        </View>
      </View>
    </TouchableWithoutFeedback>
  );
};

const styles = {
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    margin: 10,
    padding: 10,
    width: "90%",
  },
  cardImage: {
    height: 200,
    borderRadius: 10,
  },
  cardBody: {
    marginTop: 10,
  },
  textContainer: {
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: "bold",
  },
  hr: {
    height: 1,
    backgroundColor: "#333333",
    marginVertical: 5,
  },
  cardText: {
    fontSize: 16,
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
};

export default RecipeCard;
