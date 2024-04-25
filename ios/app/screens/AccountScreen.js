import React, { useState } from "react";
import { View, StyleSheet, Text } from "react-native";
import Screen from "../components/Screen";
import ListItem from "../components/lists/ListItem";
import useAuth from "../auth/useAuth";
import Icon from "../components/Icon";
import colors from "../config/colors";
import ActivityIndicator from "../components/ActivityIndicator";
import routenames from "../navigation/routeNames";

function AccountScreen({ navigation }) {
  const { user, logOut } = useAuth();
  const [loading, setLoading] = useState(false);

  const verifyEmail = async () => {
    setLoading(true);
    //sleep for 5 seconds
    await new Promise((resolve) => setTimeout(resolve, 5000));
    // const result = await usersApi.sendVerificationEmail();
    setLoading(false);
    // if (!result.ok) return Alert.alert("Error", result.data.error);
    // if (result.data.message === "Email already verified") {
    //   return Alert.alert("No need!", "Email already verified");
    // } else {
    //   Alert.alert("Success", "Verification email sent!");
    // }
  };

  return (
    <Screen>
      <ActivityIndicator visible={loading} />
      <View style={styles.screen}>
        <View style={styles.header}>
          <Text style={styles.title}>Account</Text>
          <Text style={styles.subtitle}>{user.email}</Text>
        </View>

        <View style={styles.listContainer}>
          {!user.emailVerified && (
            <>
              <ListItem
                title="Verify Email"
                IconComponent={
                  <Icon
                    name="email"
                    iconColor={colors.primary}
                    backgroundColor={colors.secondary}
                  />
                }
                onPress={() => verifyEmail()}
                backgroundColor={colors.danger}
              />
              <View style={styles.horizontalRule} />
            </>
          )}

          <ListItem
            title="Change Password"
            IconComponent={
              <Icon
                name="lock"
                iconColor={colors.primary}
                backgroundColor={colors.secondary}
              />
            }
            onPress={() => navigation.navigate(routenames.UPDATE_PASSWORD)}
          />
          <ListItem
            title="Log Out"
            IconComponent={
              <Icon
                name="logout"
                iconColor={colors.primary}
                backgroundColor={colors.secondary}
              />
            }
            onPress={logOut}
          />
        </View>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: {
    padding: 20,
  },
  header: {
    alignItems: "center",
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 18,
    color: colors.medium,
  },
  listContainer: {
    marginTop: 20,
    gap: 20,
  },
  horizontalRule: {
    height: 2,
    backgroundColor: colors.secondary,
    marginVertical: 0,
    width: "75%",
    alignSelf: "center",
  },
});

export default AccountScreen;
