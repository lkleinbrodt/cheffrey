import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import RecipesScreen from "../screens/RecipesScreen.js";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import routeNames from "./routeNames";

const Stack = createStackNavigator();

const RecipeListNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="RecipeList" component={RecipesScreen} />
    <Stack.Screen
      name={routeNames.RECIPES_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={{ headerShown: true, title: "Details" }}
    />
  </Stack.Navigator>
);

export default RecipeListNavigator;
