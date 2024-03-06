import { React, useEffect, useState } from "react";
import { View, Text, Alert, StyleSheet } from "react-native";
import axios from "../components/axios";
import RecipeGrid from "../components/RecipeGrid";
import * as SecureStore from "expo-secure-store";
import Colors from "../config/colors";
import Screen from "../components/Screen";
const RecipeList = ({ navigation }) => {
  const [recipes, setRecipes] = useState([]);

  SecureStore.getItemAsync("token").then((token) => {
    if (token) {
      axios.defaults.headers["Authorization"] = `Bearer ${token}`;
    } else {
      console.log("Token does not exist, redirecting to login");
      router.replace("login");
    }
  });

  const fetchData = async () => {
    console.log("trying to fetch recipe list");
    axios
      .get("recipe-list")
      .then((response) => {
        setRecipes(response.data.recipes);
      })
      .catch((error) => {
        //log the error with plenty of context
        console.error("Error loading recipes", error);
        Alert.alert("Error", "Error loading recipes");
      });
  };

  useEffect(() => {
    fetchData();
  }, [navigation]);

  return (
    <Screen style={styles.screen}>
      <View>
        <Text>Recipe List</Text>
        <RecipeGrid recipes={recipes} />
      </View>
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    backgroundColor: Colors.backgroundColor,
  },
});
export default RecipeList;
