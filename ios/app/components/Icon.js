import React from "react";
import { View, TouchableOpacity } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import colors from "../config/colors";

function Icon({
  name,
  size = 40,
  backgroundColor = colors.primary,
  iconColor = colors.white,
  onPress,
}) {
  if (onPress) {
    return (
      <View
        style={{
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <TouchableOpacity onPress={onPress}>
          <MaterialCommunityIcons
            name={name}
            color={iconColor}
            size={size * 0.5}
          />
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        backgroundColor,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <MaterialCommunityIcons name={name} color={iconColor} size={size * 0.5} />
    </View>
  );
}

export default Icon;
