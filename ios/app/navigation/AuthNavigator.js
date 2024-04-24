import React from "react";
import { createStackNavigator } from "@react-navigation/stack";

import LoginScreen from "../screens/LoginScreen";
import WelcomeScreen from "../screens/WelcomeScreen";
import RegisterScreen from "../screens/RegisterScreen";
import ForgotPasswordScreen from "../screens/ForgotPasswordScreen";
import colors from "../config/colors";
import routeNames from "./routeNames";

const Stack = createStackNavigator();

const AuthNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.background,
          shadowColor: "transparent",
        },
        headerTintColor: colors.primary,
        headerTitleStyle: {
          display: "none",
        },
      }}
    >
      <Stack.Screen
        name={routeNames.WELCOME}
        component={WelcomeScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen name={routeNames.LOGIN} component={LoginScreen} />
      <Stack.Screen name={routeNames.REGISTER} component={RegisterScreen} />
      <Stack.Screen
        name={routeNames.FORGOT_PASSWORD}
        component={ForgotPasswordScreen}
      />
    </Stack.Navigator>
  );
};

export default AuthNavigator;
