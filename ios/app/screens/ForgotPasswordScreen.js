import React, { useState } from "react";
import { StyleSheet, Alert } from "react-native";
import * as Yup from "yup";

import {
  ErrorMessage,
  Form,
  FormField,
  SubmitButton,
} from "../components/forms";
import ActivityIndicator from "../components/ActivityIndicator";
import Screen from "../components/Screen";

import usersApi from "../api/users";
import AnimatedCodeVerification from "../components/AnimatedCodeVerification";
import routeNames from "../navigation/routeNames";

const emailValidationSchema = Yup.object().shape({
  email: Yup.string().required().email().label("Email"),
});

const passwordValidationSchema = Yup.object().shape({
  verificationCode: Yup.string().required().label("Verification Code"),
  newPassword: Yup.string().required().min(4).label("New Password"),
  confirmNewPassword: Yup.string()
    .oneOf([Yup.ref("newPassword"), null], "Passwords must match")
    .required("Password confirmation is required")
    .label("Confirm New Password"),
});

function ForgotPasswordScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [resetEmailSent, setResetEmailSent] = useState(false);

  const sendForgotPasswordEmail = async ({ email }) => {
    console.log("sending email");
    console.log(email);
    setLoading(true);
    const result = await usersApi.sendForgotPasswordEmail(email);
    setLoading(false);
    if (!result.ok) {
      if (result.data) return Alert.alert("Error", result.data.error);
      else {
        return Alert.alert("Error", "An unexpected error occurred.");
      }
    }
    Alert.alert(
      "Success",
      "Check your email for a message from landon@coyote-ai."
    );
    setResetEmailSent(true);
    setEmail(email);
  };

  if (!resetEmailSent) {
    return (
      <>
        <ActivityIndicator visible={loading} />
        <Screen style={styles.container}>
          <Form
            initialValues={{ email: "" }}
            onSubmit={sendForgotPasswordEmail}
            validationSchema={emailValidationSchema}
          >
            <ErrorMessage error={error} visible={error} />
            <FormField
              autoCapitalize="none"
              autoCorrect={false}
              icon="email"
              keyboardType="email-address"
              name="email"
              placeholder="Email"
              textContentType="emailAddress"
            />
            <SubmitButton title="Send Reset Email" />
          </Form>
        </Screen>
      </>
    );
  } else {
    //TODO: this is a major copy paste of the update password screen
    const handleSubmit = async (passwordInfo) => {
      setLoading(true);
      //add email to passwordInfo
      passwordInfo.email = email;
      const result = await usersApi.changeForgotPassword(passwordInfo);
      if (!result.ok) {
        setLoading(false);
        if (result.data) return Alert.alert("Error", result.data.error);
        else {
          return alert("Error", "An unexpected error occurred.");
        }
      }
      setLoading(false);
      Alert.alert("Success", "Password changed successfully.");
      navigation.navigate(routeNames.LOGIN);
    };

    return (
      <Screen style={styles.container}>
        <Form
          initialValues={{
            verificationCode: "",
            newPassword: "",
            confirmNewPassword: "",
          }}
          onSubmit={handleSubmit}
          validationSchema={passwordValidationSchema}
        >
          <AnimatedCodeVerification name={"verificationCode"} />
          <FormField
            autoCapitalize="none"
            autoCorrect={false}
            icon="lock"
            name="newPassword"
            label="New Password"
            secureTextEntry
            textContentType="password"
          />
          <FormField
            autoCapitalize="none"
            autoCorrect={false}
            icon="lock"
            name="confirmNewPassword"
            label="Confirm New Password"
            secureTextEntry
            textContentType="password"
          />
          <SubmitButton title="Change Password" />
        </Form>
      </Screen>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
});

export default ForgotPasswordScreen;
