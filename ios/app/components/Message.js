import React from "react";
import { View, Text, StyleSheet } from "react-native";

const Message = ({ message, subMessage }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.message}>{message}</Text>
      <Text style={styles.subMessage}>{subMessage}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  image: {
    width: 150,
    height: 150,
    marginBottom: 20,
  },
  message: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#333",
    textAlign: "center",
  },
  subMessage: {
    fontSize: 16,
    color: "#555",
    textAlign: "center",
    marginTop: 10,
  },
});

export default Message;
