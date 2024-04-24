import React, { useState } from "react";
import { StyleSheet, Image, ActivityIndicator, View } from "react-native";
import Screen from "../components/Screen.js";
import {
  Form,
  FormField,
  SubmitButton,
  ErrorMessage,
} from "../components/forms/index.js";
import authAPI from "../api/auth.js";
import { Button } from "react-native";
import * as Yup from "yup";
import useAuth from "../auth/useAuth.js";
import colors from "../config/colors.js";
import routeNames from "../navigation/routeNames.js";
import Text from "../components/Text.js";

//required to properly decode the token
import "core-js/stable/atob";

const validationSchema = Yup.object().shape({
  email: Yup.string().required().email().label("Email"),
  password: Yup.string().required().min(4).label("Password"),
});

function LoginScreen({ navigation }) {
  const auth = useAuth();
  const [loginFailed, setLoginFailed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async ({ email, password }) => {
    setLoading(true);
    const result = await authAPI.login(email, password);
    if (!result.ok) return setLoginFailed(true);
    setLoginFailed(false);
    auth.logIn(result.data.access_token, result.data.refresh_token);
    setLoading(false);
  };

  return (
    <Screen style={styles.container}>
      <View style={styles.welcomeBanner}>
        <Image
          source={require("../assets/chef_head.png")}
          style={styles.logo}
        />
        <Text style={styles.welcomeText}>Welcome Back!</Text>
      </View>
      <View style={styles.formContainer}>
        <Form
          initialValues={{ email: "", password: "" }}
          onSubmit={handleSubmit}
          validationSchema={validationSchema}
        >
          <ErrorMessage
            error="Invalid email or password"
            visible={loginFailed}
          />
          <FormField
            autoCapitalize="none"
            autoCorrect={false}
            icon="email"
            keyboardType="email-address"
            name="email"
            placeholder="Email"
            textContentType="emailAddress"
          />
          <FormField
            autoCapitalize="none"
            autoCorrect={false}
            icon="lock"
            name="password"
            placeholder="Password"
            secureTextEntry
            textContentType="password"
          />

          {loading ? (
            <ActivityIndicator
              style={styles.loading}
              size="large"
              color={colors.primary}
            />
          ) : (
            <SubmitButton title="Login" />
          )}
        </Form>
      </View>
      <Button
        title="Forgot my password"
        onPress={() => navigation.navigate(routeNames.FORGOT_PASSWORD)}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
  formContainer: {
    padding: 15,
  },
  registerButton: {
    alignSelf: "center",
    marginTop: 80,
    backgroundColor: colors.secondary,
    borderRadius: 25,
    justifyContent: "center",
    alignItems: "center",
    padding: 15,
    width: "50%",
  },
  welcomeBanner: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    marginBottom: 20,
    marginTop: 20,
  },
  logo: {
    width: 50,
    height: 50,
    resizeMode: "contain",
    marginHorizontal: 20,
  },
  welcomeText: {
    fontSize: 32,
    color: colors.primary,
    fontWeight: "bold",
    paddingTop: 10,
  },
});

export default LoginScreen;
