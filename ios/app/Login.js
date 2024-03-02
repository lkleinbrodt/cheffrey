import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Alert,
  Pressable,
  Keyboard,
} from "react-native";
import LoginButton from "../components/LoginButton.js";
import ImageViewer from "../components/ImageViewer.js";
import axios from "../components/axios.js";
import * as SecureStore from "expo-secure-store";
import { router } from "expo-router";

const CheffreyLogo = require("../assets/chef.png");

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    SecureStore.getItemAsync("token").then((token) => {
      console.log("Token:", token);
      // If token exists, redirect to another page
      if (token) {
        console.log("Token exists:", token);
        router.replace("Explore");
      }
    });
  }, []);

  const handleLogin = async () => {
    // Validate inputs
    if (!username || !password) {
      Alert.alert("Error", "Please enter both username and password");
      return;
    }

    try {
      const response = await axios.post("/login", {
        username,
        password,
      });

      if (response.data.access_token) {
        SecureStore.setItemAsync("token", response.data.access_token);
        router.replace("Explore");
      } else {
        Alert.alert("Error", "Invalid username or password");
      }
    } catch (error) {
      console.error("Error logging in", error);
      Alert.alert("Error", "Invalid username or password");
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.imageContainer}>
        <ImageViewer placeholderImageSource={CheffreyLogo} />
      </View>
      <Text style={styles.title}>Cheffrey</Text>
      <Pressable onPress={() => Keyboard.dismiss()}>
        <View>
          <TextInput
            style={styles.input}
            placeholder="Username"
            onChangeText={(text) => setUsername(text)}
            value={username}
            placeholderTextColor="grey"
            autoCapitalize="none"
          />
        </View>
      </Pressable>

      <Pressable onPress={() => Keyboard.dismiss()}>
        <TextInput
          style={styles.input}
          placeholder="Password"
          secureTextEntry
          onChangeText={(text) => setPassword(text)}
          value={password}
          placeholderTextColor="grey"
        />
      </Pressable>

      <LoginButton onPress={handleLogin} />
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
  input: {
    height: 40,
    width: 120,
    borderColor: "gray",
    borderWidth: 1,
    marginBottom: 10,
    paddingLeft: 10,
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    textAlign: "center",
  },
});

export default Login;
