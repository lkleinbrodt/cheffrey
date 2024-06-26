import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import CookedScreen from "../screens/CookedScreen.js";
import routeNames from "./routeNames";

const Stack = createStackNavigator();

const CookedNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="CookedRecipes" component={CookedScreen} />
    <Stack.Screen
      name={routeNames.COOKED_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={{ headerShown: true, title: "Details" }}
    />
  </Stack.Navigator>
);

export default CookedNavigator;
