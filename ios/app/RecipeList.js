import { React, useEffect, useState } from "react";
import { View, Text } from "react-native";
import axios from "../components/axios";
import RecipeGrid from "../components/RecipeGrid";
import * as SecureStore from "expo-secure-store";

const RecipeList = () => {
  const [recipes, setRecipes] = useState([]);

  SecureStore.getItemAsync("token").then((token) => {
    if (token) {
      axios.defaults.headers["Authorization"] = `Bearer ${token}`;
    } else {
      console.log("Token does not exist, redirecting to login");
      router.replace("Login");
    }
  });

  const fetchData = async () => {
    axios
      .get("recipe-list")
      .then((response) => {
        setRecipes(response.data.recipes);
      })
      .catch((error) => {
        //log the error with plenty of context
        console.error("Error loading recipes", error);
      });
  };
  useEffect(() => {
    fetchData();
  }, []);

  return (
    <View>
      <RecipeGrid recipes={recipes} />
    </View>
  );
};

export default RecipeList;
