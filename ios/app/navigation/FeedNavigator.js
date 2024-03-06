import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import ExploreScreen from "../screens/ExploreScreen";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import routes from "./routes";

const Stack = createStackNavigator();

const FeedNavigator = () => (
  <Stack.Navigator
    screenOptions={{ presentation: "modal", headerShown: false }}
  >
    <Stack.Screen name="Recipes" component={ExploreScreen} />
    <Stack.Screen
      name={routes.RECIPE_DETAILS}
      component={RecipeDetailsScreen}
    />
  </Stack.Navigator>
);

export default FeedNavigator;
