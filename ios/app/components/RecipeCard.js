import { React, useState } from "react";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  Modal,
  TouchableWithoutFeedback,
} from "react-native";
import colors from "../config/colors";
import recipesAPI from "../api/recipes";
import { FontAwesome } from "@expo/vector-icons"; // Import the required icon from Expo Vector Icons

const RecipeCard = ({ recipe, onPress }) => {
  const [isSaved, setIsSaved] = useState(recipe.in_list);
  const [isFavorite, setIsFavorite] = useState(recipe.in_favorites);

  const handleSavePress = () => {
    recipesAPI.toggleRecipeInList(recipe.id);
    setIsSaved(!isSaved);
  };
  const handleFavoritesPress = () => {
    recipesAPI.toggleRecipeInFavorites(recipe.id);
    setIsFavorite(!isFavorite);
  };

  return (
    <TouchableWithoutFeedback onPress={onPress}>
      <View style={styles.card}>
        <Image
          source={{ uri: recipe.image_url }}
          style={styles.cardImage}
          alt={recipe.title}
          defaultSource={require("../assets/chef.png")}
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
              onPress={handleFavoritesPress}
            >
              <FontAwesome
                name={isFavorite ? "heart" : "heart-o"}
                size={30}
                color={isFavorite ? "red" : colors.primary}
              />
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
  viewRecipeButton: {
    backgroundColor: "#007bff",
    padding: 10,
    borderRadius: 5,
    flex: 1,
    marginRight: 5,
  },
  saveButton: {
    padding: 10,
    borderRadius: 5,
    flex: 1,
    marginRight: 5,
  },
  favoriteButton: {
    padding: 10,
    borderRadius: 5,
    flex: 1,
  },
  buttonText: {
    color: "#ffffff",
    textAlign: "center",
  },
};

export default RecipeCard;
