import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import FavoritesScreen from "../screens/FavoritesScreen.js";
import routes from "./routes";

const Stack = createStackNavigator();

const FavoritesNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="FavoriteRecipes" component={FavoritesScreen} />
    <Stack.Screen
      name={routes.FAVORITES_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={{ headerShown: true, title: "Details" }}
    />
  </Stack.Navigator>
);

export default FavoritesNavigator;
