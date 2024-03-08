import React from "react";
import { View, Text, Image, TouchableOpacity } from "react-native";

const RecipeModal = ({ recipe, closeModal }) => {
  return (
    <View style={styles.container}>
      <View style={styles.modal}>
        <Image
          source={{ uri: recipe.image_url }}
          style={styles.image}
          alt={recipe.title}
        />
        <Text style={styles.modalTitle}>{recipe.title}</Text>
        <Text style={styles.modalText}>{recipe.description}</Text>

        <TouchableOpacity style={styles.closeButton} onPress={closeModal}>
          <Text style={styles.buttonText}>Close</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = {
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.5)",
  },
  modal: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 20,
    width: "80%",
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
  },
  modalText: {
    fontSize: 16,
    marginBottom: 20,
  },
  image: {
    height: 200,
    borderRadius: 10,
  },
  closeButton: {
    backgroundColor: "#007bff",
    padding: 10,
    borderRadius: 5,
    alignSelf: "flex-end",
  },
  buttonText: {
    color: "#ffffff",
    textAlign: "center",
  },
};

export default RecipeModal;
