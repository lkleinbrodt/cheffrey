import React from "react";
import { ImageBackground, StyleSheet, View, Image, Text } from "react-native";
import Screen from "../components/Screen";
import Button from "../components/Button";
import colors from "../config/colors";
import defaultStyles from "../config/styles";

function WelcomeScreen({ navigation }) {
  return (
    <Screen style={styles.screen}>
      <View style={styles.logoContainer}>
        {/* <Text style={styles.title}>Cheffrey</Text> */}
        <Image
          style={styles.logo}
          source={require("../assets/chef_hat_stamp.png")}
        />
        <Text style={styles.tagline}>What are we cooking?</Text>
      </View>
      <View style={styles.buttonsContainer}>
        <Button title="Login" onPress={() => navigation.navigate("Login")} />
        <Button
          title="Register"
          color="secondary"
          onPress={() => navigation.navigate("Register")}
        />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: "flex-end",
  },
  buttonsContainer: {
    paddingHorizontal: 30,
    alignItems: "center",
    marginBottom: 50,
    width: "100%",
  },
  logo: {
    height: 200,
    resizeMode: "contain",
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 35,
  },
  tagline: {
    ...defaultStyles.text,
    fontSize: 25,
    fontWeight: "300",
    paddingVertical: 20,
    fontStyle: "italic",
  },
  title: {
    ...defaultStyles.text,
    fontSize: 50,
    fontWeight: "600",
    paddingVertical: 20,
    color: colors.primary,
    fontStyle: "italic",
    fontWeight: "bold",
  },
});

export default WelcomeScreen;
