import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, Pressable } from "react-native";
import ImageViewer from "../components/ImageViewer.js";
import * as SecureStore from "expo-secure-store";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import { router } from "expo-router";

const CheffreyLogo = require("../assets/chef.png");

const Home = () => {
  const handleNavPress = (option) => {
    console.log(option);
    router.replace(option);
  };
  useEffect(() => {
    SecureStore.getItemAsync("token").then((token) => {
      if (!token) {
        consolelog("Token does not exist, redirecting to login");
        router.replace("Login");
      }
    });
  }, []);
  return (
    <View style={styles.container}>
      <View style={styles.imageContainer}>
        <ImageViewer placeholderImageSource={CheffreyLogo} />
      </View>
      <Text style={styles.title}>Cheffrey</Text>
      <View style={[styles.buttonContainer]}>
        <Pressable
          style={[styles.button, { backgroundColor: "#fff" }]}
          onPress={() => handleNavPress("Explore")}
        >
          <FontAwesome name="sign-in" size={18} style={styles.buttonIcon} />
          <Text style={[styles.buttonLabel]}>Explore</Text>
        </Pressable>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#faf1e4",
    alignItems: "center",
  },
  imageContainer: {
    paddingTop: 58,
  },
  title: {
    fontSize: 36,
    color: "#435334",
    marginTop: 20,
    textAlign: "center",
    marginBottom: 0,
    paddingBottom: 0,
  },
  buttonContainer: {
    width: 180,
    height: 60,
    marginHorizontal: 20,
    alignItems: "center",
    justifyContent: "center",
    padding: 3,
  },
  button: {
    borderRadius: 10,
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
  },
  buttonIcon: {
    paddingRight: 8,
    color: "#435334",
  },
  buttonLabel: {
    color: "#435334",
    fontSize: 16,
  },
});

export default Home;
