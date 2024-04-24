import { LinearGradient } from "expo-linear-gradient";
import { StyleSheet, View } from "react-native";

const GradientHeader = () => {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={["rgba(0, 0, 0, 0.5)", "rgba(0, 0, 0, 0.0)"]}
        style={styles.gradient}
      />
    </View>
  );
};

export default GradientHeader;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "transparent",
  },
  gradient: {
    flex: 1,
  },
});
