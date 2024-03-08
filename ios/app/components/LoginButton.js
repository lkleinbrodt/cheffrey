import { StyleSheet, View, Pressable, Text } from "react-native";
import FontAwesome from "@expo/vector-icons/FontAwesome";

export default function LoginButton({ onPress }) {
  return (
    <View style={[styles.buttonContainer]}>
      <Pressable
        style={[styles.button, { backgroundColor: "#fff" }]}
        onPress={onPress}
      >
        <FontAwesome name="sign-in" size={18} style={styles.buttonIcon} />
        <Text style={[styles.buttonLabel]}>Login</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
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
