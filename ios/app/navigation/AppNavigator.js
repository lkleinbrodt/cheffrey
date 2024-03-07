import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import FeedNavigator from "./FeedNavigator.js";
import SavedNavigator from "./SavedNavigator.js";
import ListNavigator from "./ListNavigator.js";
const Tab = createBottomTabNavigator();

const AppNavigator = () => (
  <Tab.Navigator screenOptions={{ headerShown: false }}>
    <Tab.Screen
      name="Explore"
      component={FeedNavigator}
      options={{
        tabBarIcon: ({ color, size }) => (
          <MaterialCommunityIcons name="compass" color={color} size={size} />
        ),
      }}
    />
    <Tab.Screen
      name="Saved"
      component={SavedNavigator}
      options={{
        tabBarIcon: ({ color, size }) => (
          <MaterialCommunityIcons
            name="bookmark-multiple"
            color={color}
            size={size}
          />
        ),
        unmountOnBlur: true,
      }}
    />
    <Tab.Screen
      name="My List"
      component={ListNavigator}
      options={{
        tabBarIcon: ({ color, size }) => (
          <MaterialCommunityIcons
            name="format-list-bulleted"
            color={color}
            size={size}
          />
        ),
      }}
    />
  </Tab.Navigator>
);

export default AppNavigator;
