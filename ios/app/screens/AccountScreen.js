import React from "react";
import { View, StyleSheet, Text } from "react-native";
import Screen from "../components/Screen";
import ListItem from "../components/lists/ListItem";
import useAuth from "../auth/useAuth";
import Icon from "../components/Icon";
import colors from "../config/colors";

function AccountScreen({ navigation }) {
  const { user, logOut } = useAuth();
  return (
    <Screen style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Account</Text>
        <Text style={styles.subtitle}>{user.email}</Text>
      </View>

      <ListItem
        title="Change Password"
        IconComponent={
          <Icon
            name="lock"
            iconColor={colors.primary}
            backgroundColor={colors.secondary}
          />
        }
        onPress={() => navigation.navigate("Change Password")}
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
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    gap: 10,
    flex: 1,
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
});

export default AccountScreen;
