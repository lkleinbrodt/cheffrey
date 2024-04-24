import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import ExploreScreen from "../screens/ExploreScreen";
import RecipeDetailsScreen from "../screens/RecipeDetailsScreen";
import routeNames from "./routeNames";
import { LinearGradient } from "expo-linear-gradient";
import { View, StyleSheet } from "react-native";

const Stack = createStackNavigator();

// const GradientHeader = () => {
//   return (
//     <View style={styles.container}>
//       <LinearGradient
//         colors={["rgba(0, 0, 0, 0.5)", "rgba(0, 0, 0, 0.0)"]}
//         style={styles.gradient}
//       />
//     </View>
//   );
// };

const FeedNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen
      name={routeNames.EXPLORE_RECIPES}
      component={ExploreScreen}
      options={({ route }) => ({ headerShown: false, title: "Explore" })}
    />
    <Stack.Screen
      name={routeNames.FEED_RECIPE_DETAILS}
      component={RecipeDetailsScreen}
      options={({ route }) => ({
        headerShown: true,
        title: route.params.recipe.title,
        // headerBackground: () => <GradientHeader />,
        // headerTintColor: "white",
        // headerTransparent: true,
      })}
    />
  </Stack.Navigator>
);

export default FeedNavigator;

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     backgroundColor: "transparent",
//   },
//   gradient: {
//     flex: 1,
//   },
// });
