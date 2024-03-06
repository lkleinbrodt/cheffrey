import React from "react";
import LottieView from "lottie-react-native";

export default function LottieActivityIndicator({ visible = false }) {
  if (!visible) return null;
  console.log("displaying loader");
  return (
    <LottieView
      style={{ flex: 1 }}
      source={require("../assets/animations/loader.json")}
      autoPlay
      loop
    />
  );
}
