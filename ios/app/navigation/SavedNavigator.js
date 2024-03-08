import React from "react";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { createMaterialTopTabNavigator } from "@react-navigation/material-top-tabs";
import CookedNavigator from "./CookedNavigator.js";
import FavoritesNavigator from "./FavoritesNavigator.js";

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
        component={FavoritesNavigator}
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
        component={CookedNavigator}
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
