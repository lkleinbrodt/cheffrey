import React from "react";
import LottieView from "lottie-react-native";
import { View, StyleSheet } from "react-native";
import colors from "../config/colors";

function ActivityIndicator({ visible = false }) {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <LottieView
        autoPlay
        loop
        source={require("../assets/animations/loader.json")}
        style={{ flex: 1 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: "absolute",
    backgroundColor: colors.background,
    height: "100%",
    opacity: 0.8,
    width: "100%",
    zIndex: 1,
  },
});

export default ActivityIndicator;
