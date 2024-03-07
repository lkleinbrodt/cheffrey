import React from "react";
import { StyleSheet, SafeAreaView, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { createMaterialTopTabNavigator } from "@react-navigation/material-top-tabs";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import FavoritesScreen from "../screens/FavoritesScreen.js";
import CookedScreen from "../screens/CookedScreen.js";
import colors from "../config/colors";

const Tab = createMaterialTopTabNavigator();

const SavedNavigator = () => {
  const insets = useSafeAreaInsets();
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: {
          height: 50 + insets.top,
          justifyContent: "flex-end",
        },
        tabBarLabelStyle: {
          fontSize: 16,
          fontWeight: "bold",
        },
      }}
    >
      <Tab.Screen
        name="Favorites"
        component={FavoritesScreen}
        options={
          {
            // tabBarIcon: ({ color, size }) => (
            //   <MaterialCommunityIcons
            //     containerStyle={{ marginTop: 1 }}
            //     name="heart"
            //     color={color}
            //     size={size}
            //   />
            // ),
          }
        }
      />
      <Tab.Screen
        name="Cooked"
        component={CookedScreen}
        // options={{
        //   tabBarIcon: ({ color, size }) => (
        //     <MaterialCommunityIcons
        //       name="silverware-fork-knife"
        //       color={color}
        //       size={size}
        //     />
        //   ),
        // }}
      />
    </Tab.Navigator>
  );
};

export default SavedNavigator;

// const AppNavigator = () => (
//   <Tab.Navigator screenOptions={{ headerShown: false }}>
//     <Tab.Screen
//       name="Explore"
//       component={FeedNavigator}
//       options={{
//         tabBarIcon: ({ color, size }) => (
//           <MaterialCommunityIcons name="compass" color={color} size={size} />
//         ),
//       }}
//     />
//     <Tab.Screen
//       name="Recipes"
//       component={RecipesScreen}
//       options={{
//         tabBarIcon: ({ color, size }) => (
//           <MaterialCommunityIcons
//             name="format-list-bulleted"
//             color={color}
//             size={size}
//           />
//         ),
//         unmountOnBlur: true,
//       }}
//     />
//   </Tab.Navigator>
// );

// export default AppNavigator;
