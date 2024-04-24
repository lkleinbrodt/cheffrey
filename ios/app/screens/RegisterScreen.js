import React from "react";
import { StyleSheet, Alert, Image, View } from "react-native";
import * as Yup from "yup";

import Screen from "../components/Screen";
import { Form, FormField, SubmitButton } from "../components/forms";
import usersAPI from "../api/users";
import authApi from "../api/auth";
import useAuth from "../auth/useAuth";
import Text from "../components/Text";
import colors from "../config/colors";

const validationSchema = Yup.object().shape({
  email: Yup.string().required().email().label("Email"),
  password: Yup.string().required().min(4).label("Password"),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref("password"), null], "Passwords must match")
    .required("Password confirmation is required")
    .label("Confirm Password"),
});

function RegisterScreen({ navigation }) {
  const auth = useAuth();

  const handleSubmit = async ({ email, password }) => {
    const result = await usersAPI.register(email, password);
    if (!result.ok) {
      if (result.data) return Alert.alert("Error", result.data.message);
      else {
        return alert("Error", "Asssn unexpected error occurred.");
      }
    }
    const loginResult = await authApi.login(email, password);
    auth.logIn(loginResult.data.access_token, loginResult.data.refresh_token);
  };

  return (
    <Screen style={styles.container}>
      <View style={styles.welcomeBanner}>
        <Image
          source={require("../assets/chef_head.png")}
          style={styles.logo}
        />
        <Text style={styles.welcomeText}>Welcome to Cheffrey!</Text>
      </View>
      <View style={styles.formContainer}>
        <Form
          initialValues={{ email: "", password: "", confirmPassword: "" }}
          onSubmit={handleSubmit}
          validationSchema={validationSchema}
        >
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
          <FormField
            autoCapitalize="none"
            autoCorrect={false}
            icon="lock"
            name="confirmPassword"
            placeholder="Confirm Password"
            secureTextEntry
            textContentType="password"
          />
          <SubmitButton title="Register" />
        </Form>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
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
    marginHorizontal: 15,
  },
  welcomeText: {
    fontSize: 24,
    color: colors.primary,
    fontWeight: "bold",
    paddingTop: 10,
  },
  formContainer: {
    padding: 15,
  },
});

export default RegisterScreen;
