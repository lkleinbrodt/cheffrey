import { React, useState } from "react";
import { View, Text, Image, TouchableOpacity, Modal } from "react-native";
import RecipeModal from "./RecipeModal";
const RecipeCard = ({ recipe }) => {
  const [showFullRecipe, setShowFullRecipe] = useState(false);

  const handleFullRecipePress = () => {
    setShowFullRecipe(!showFullRecipe);
  };
  return (
    <View style={styles.card}>
      <Image
        source={{ uri: recipe.image_url }}
        style={styles.cardImage}
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
            style={styles.viewRecipeButton}
            onPress={handleFullRecipePress}
          >
            <Text style={styles.buttonText}>Full Recipe</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.saveButton,
              { backgroundColor: recipe.in_list ? "red" : "gray" },
            ]}
            onPress={() => console.log("Save to List or Remove from List")}
          >
            <Text style={styles.buttonText}>
              {recipe.in_list ? "Remove from List" : "Save to List"}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.favoriteButton}
            onPress={() => console.log("Toggle Favorites")}
          >
            <Text style={styles.buttonText}>Favorite</Text>
          </TouchableOpacity>
        </View>
      </View>
      <Modal
        animationType="slide"
        transparent={true}
        visible={showFullRecipe}
        onRequestClose={handleFullRecipePress}
      >
        <RecipeModal recipe={recipe} closeModal={handleFullRecipePress} />
      </Modal>
    </View>
  );
};

const styles = {
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    margin: 10,
    padding: 10,
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
    justifyContent: "space-between",
    alignItems: "center",
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
