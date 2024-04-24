import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import CookbookScreen from "../screens/CookbookScreen";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import routeNames from "./routeNames";
import EditRecipeScreen from "../screens/EditRecipeScreen";

const Stack = createStackNavigator();

const CookbookNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen
      name={routeNames.COOKBOOK_RECIPES}
      component={CookbookScreen}
      options={({ route }) => ({ headerShown: false, title: "Cookbook" })}
    />
    <Stack.Screen
      name={routeNames.COOKBOOK_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={{ headerShown: true, title: "Details" }}
    />
    <Stack.Screen
      name={routeNames.COOKBOOK_EDIT_RECIPE}
      component={EditRecipeScreen}
      options={({ route }) => ({
        headerShown: true,
        title: route.params.title ? route.params.title : "Edit Recipe",
      })}
    />
  </Stack.Navigator>
);

export default CookbookNavigator;
