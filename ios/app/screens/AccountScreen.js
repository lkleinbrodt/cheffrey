import React from "react";
import { View, StyleSheet, Text } from "react-native";
import Screen from "../components/Screen";
import ListItem from "../components/lists/ListItem";
import useAuth from "../auth/useAuth";
import Icon from "../components/Icon";

function AccountScreen({ navigation }) {
  const { user, logOut } = useAuth();
  return (
    <Screen style={styles.screen}>
      <View style={styles.container}>
        <Text>Account Screen</Text>
        <ListItem title={user.email} />
      </View>

      <ListItem
        title="Log Out"
        IconComponent={<Icon name="logout" />}
        onPress={logOut}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {},
});

export default AccountScreen;
