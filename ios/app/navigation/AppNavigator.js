import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import FeedNavigator from "./FeedNavigator.js";
import SavedNavigator from "./SavedNavigator.js";
import ListNavigator from "./ListNavigator.js";
import AccountNavigator from "./AccountNavigator.js";
import ApiInterceptor from "../api/apiInterceptor";
const Tab = createBottomTabNavigator();

const AppNavigator = () => (
  <>
    <ApiInterceptor />
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
          unmountOnBlur: true,
        }}
      />
      <Tab.Screen
        name="Account"
        component={AccountNavigator}
        options={{
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  </>
);

export default AppNavigator;
