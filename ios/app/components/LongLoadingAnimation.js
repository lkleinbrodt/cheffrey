import React, { useState, useEffect } from "react";
import { View, StyleSheet, Animated, Text } from "react-native";
import LottieView from "lottie-react-native";
import defaultStyles from "../config/styles";

const animations = [
  "https://lottie.host/3e6fd7b7-0fae-41ef-ac1a-c6eb62481fce/Cy49fmdcnX.json",
];

const captions = [
  "Preheating the oven",
  "Chopping vegetables",
  "Running to the store for milk",
  "Setting the table",
  "Polishing the silverware",
  "Grating the cheese",
  "Boiling the pasta",
  "Whipping up a soufflé",
  "Basting the roast",
  "Steaming some veggies",
  "Deglazing the pan",
  "Zesting some citrus",
  "Kneading the dough",
  "Melting two sticks of butter",
  "Cracking some eggs eggs",
  "Caramelizing the sugar",
  "Brewing a pot of coffee",
  "Blending the smoothie",
  "Roasting the nuts",
  "Infusing the herbs",
  "Sharpening our knives",
  "Warming up the stovetop",
  "Seasoning the skillet",
  "Slicing the tomatoes",
  "Searing the steak",
  "Mincing some garlic",
  "Simmering the sauce",
  "Whisking the vinaigrette",
  "Fluffing the rice",
  "Toasting the bread crumbs",
  "Sauteing some onions",
  "Chilling a bottle of wine",
];

function LongLoadingAnimation({ visible = false, header = "" }) {
  const [animationIndex, setAnimationIndex] = useState(
    Math.floor(Math.random() * animations.length)
  );
  const [captionIndex, setCaptionIndex] = useState(
    Math.floor(Math.random() * captions.length)
  );
  const [opacity] = useState(new Animated.Value(1));

  useEffect(() => {
    let intervalId;

    intervalId = setInterval(() => {
      Animated.timing(opacity, {
        toValue: 0,
        duration: 1500,
        useNativeDriver: true,
      }).start(() => {
        setAnimationIndex((prevIndex) => (prevIndex + 1) % animations.length);
        setCaptionIndex((prevIndex) => (prevIndex + 1) % captions.length);

        Animated.timing(opacity, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        }).start();
      });
    }, 10_000);

    return () => {
      clearInterval(intervalId);
    };
  }, [opacity]);

  if (!visible) return null;

  return (
    <View style={styles.container}>
      {/* if header is not "", display header and horizontal rule */}
      <Text style={styles.header}>{header}</Text>
      <View
        style={{
          borderBottomColor: "black",
          borderBottomWidth: 1,
          width: "80%",
          alignSelf: "center",
        }}
      />

      <Animated.View style={{ flex: 1, opacity }}>
        <LottieView
          autoPlay
          loop
          source={{
            uri: animations[animationIndex],
          }}
          style={{ flex: 1 }}
        />
        <Text style={styles.caption}> {captions[captionIndex]} </Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    height: "100%",
    width: "100%",
    zIndex: 1,
    position: "absolute",
    height: "100%",
    width: "100%",
    zIndex: 1,
  },
  animation: {
    flex: 1,
  },
  caption: {
    ...defaultStyles.text,
    marginBottom: 100,
    marginTop: 0,
    textAlign: "center",
    fontSize: 30,
    fontStyle: "italic",
  },
  header: {
    ...defaultStyles.text,
    marginTop: 100,
    textAlign: "center",
    fontSize: 28,
    fontStyle: "italic",
    fontWeight: "bold",
    color: defaultStyles.colors.primary,
  },
});

export default LongLoadingAnimation;
