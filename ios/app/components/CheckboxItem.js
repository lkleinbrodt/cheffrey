// CheckboxItem.js

import React, { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { FontAwesome } from "@expo/vector-icons"; // Make sure to install the FontAwesome package if not already installed

const CheckboxItem = ({ label, checked = false, onCheck }) => {
  const [isChecked, setChecked] = useState(checked);

  const handlePress = () => {
    setChecked(!isChecked);
    onCheck();
  };

  return (
    <TouchableOpacity onPress={handlePress} style={styles.container}>
      <FontAwesome
        name={isChecked ? "check-square" : "square-o"}
        size={20}
        color={isChecked ? "green" : "black"}
        style={styles.checkboxIcon}
      />
      <View style={styles.textContainer}>
        <Text style={[styles.label, isChecked && styles.strikethrough]}>
          {label}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 8,
  },
  checkboxIcon: {
    marginRight: 10,
  },
  textContainer: {
    flex: 1,
  },
  label: {
    fontSize: 16,
  },
  strikethrough: {
    textDecorationLine: "line-through",
    color: "gray",
  },
});

export default CheckboxItem;
