import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import AccountScreen from "../screens/AccountScreen";
import ChangePasswordScreen from "../screens/ChangePasswordScreen";
import routes from "./routes";

const Stack = createStackNavigator();

const AccountNavigator = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="AccountPage" component={AccountScreen} />
    <Stack.Screen
      name="Change Password"
      component={ChangePasswordScreen}
      options={{ headerShown: true }}
    />
  </Stack.Navigator>
);

export default AccountNavigator;
