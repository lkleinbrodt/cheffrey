import { React, useEffect, useState } from "react";
import { View, Text } from "react-native";
import axios from "../components/axios";
import RecipeGrid from "../components/RecipeGrid";

const Explore = () => {
  const [recipes, setRecipes] = useState([]);

  const fetchData = async () => {
    axios
      .get("load-more-recipes/2", {
        headers: {
          "Content-Type": "application/json",
        },
      })
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

export default Explore;
