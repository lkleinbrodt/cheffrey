import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import ExploreScreen from "../screens/ExploreScreen";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import routeNames from "./routeNames";

const Stack = createStackNavigator();

const FeedNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Recipes" component={ExploreScreen} />
    <Stack.Screen
      name={routeNames.FEED_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={{ headerShown: true, title: "Details" }}
    />
  </Stack.Navigator>
);

export default FeedNavigator;
