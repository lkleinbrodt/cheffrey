import React from "react";
import { StyleSheet, Text, TouchableOpacity } from "react-native";

import colors from "../config/colors";
import defaultStyles from "../config/styles";

function AppButton({ title, onPress, width, color = "primary" }) {
  return (
    <TouchableOpacity
      style={[
        styles.button,
        { backgroundColor: colors[color], width: width ? width : "100%" },
      ]}
      onPress={onPress}
    >
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: colors.primary,
    borderRadius: 25,
    justifyContent: "center",
    alignItems: "center",
    padding: 15,
    marginVertical: 10,
  },
  text: {
    ...defaultStyles.text,
    color: colors.white,
    fontSize: 18,
    // textTransform: "uppercase",
    fontWeight: "bold",
  },
});

export default AppButton;
