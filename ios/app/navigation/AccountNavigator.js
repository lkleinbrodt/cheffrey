import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import AccountScreen from "../screens/AccountScreen";
import ChangePasswordScreen from "../screens/ChangePasswordScreen";
import routeNames from "./routeNames";

const Stack = createStackNavigator();

const AccountNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name={routeNames.ACCOUNT} component={AccountScreen} />
    <Stack.Screen
      name={routeNames.UPDATE_PASSWORD}
      component={ChangePasswordScreen}
      options={{ headerShown: true }}
    />
  </Stack.Navigator>
);

export default AccountNavigator;
