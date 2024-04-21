import React, { useState } from "react";
import { StyleSheet, Alert } from "react-native";
import * as Yup from "yup";

import Screen from "../components/Screen";
import { Form, FormField, SubmitButton } from "../components/forms";
import accountAPI from "../api/account";
import useAuth from "../auth/useAuth";

const validationSchema = Yup.object().shape({
  currentPassword: Yup.string().required().label("Current Password"),
  newPassword: Yup.string().required().min(4).label("New Password"),
  confirmNewPassword: Yup.string()
    .oneOf([Yup.ref("newPassword"), null], "Passwords must match")
    .required("Password confirmation is required")
    .label("Confirm New Password"),
});

function ChangePasswordScreen({ navigation }) {
  const [changePasswordFailed, setChangePasswordFailed] = useState(false);

  const handleChangePassword = async ({ currentPassword, newPassword }) => {
    console.log(currentPassword, newPassword);
    const result = await accountAPI.changePassword(
      currentPassword,
      newPassword
    );

    if (!result.ok) {
      setChangePasswordFailed(true);
      if (result.data) return Alert.alert("Error", result.data.message);
      return Alert.alert("Error", "Failed to change password.");
    }
    Alert.alert("Success", "Password changed successfully.");
  };

  return (
    <Screen style={styles.container}>
      <Form
        initialValues={{
          currentPassword: "",
          newPassword: "",
          confirmNewPassword: "",
        }}
        onSubmit={handleChangePassword}
        validationSchema={validationSchema}
      >
        <FormField
          autoCapitalize="none"
          autoCorrect={false}
          icon="lock"
          name="currentPassword"
          placeholder="Current Password"
          secureTextEntry
          textContentType="password"
        />
        <FormField
          autoCapitalize="none"
          autoCorrect={false}
          icon="lock"
          name="newPassword"
          placeholder="New Password"
          secureTextEntry
          textContentType="newPassword"
        />
        <FormField
          autoCapitalize="none"
          autoCorrect={false}
          icon="lock"
          name="confirmNewPassword"
          placeholder="Confirm New Password"
          secureTextEntry
          textContentType="newPassword"
        />
        <SubmitButton title="Change Password" />
      </Form>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
});

export default ChangePasswordScreen;
