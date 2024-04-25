import { React, useEffect, useState } from "react";
import { StyleSheet, TouchableOpacity, Text, View } from "react-native";
import Screen from "../components/Screen";
import * as ImagePicker from "expo-image-picker";
import { ScrollView } from "react-native-gesture-handler";
import { Image } from "expo-image";
import colors from "../config/colors";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import api from "../api/recipes";
import LongLoadingAnimation from "../components/LongLoadingAnimation";
import routeNames from "../navigation/routeNames";

const CameraScreen = ({ navigation, route }) => {
  const [photos, setPhotos] = useState([]);
  const [hasPermission, setHasPermission] = useState(null);
  const [loading, setLoading] = useState(false);

  const requestPermission = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      navigation.goBack({ photos });
      return false;
    }
    setHasPermission(true);
    return true;
  };

  const takePhoto = async () => {
    if (!hasPermission) {
      await requestPermission();
    }
    let photo = await ImagePicker.launchCameraAsync({
      base64: true,
    });

    if (!photo.canceled) {
      photo = photo["assets"][0];
      setPhotos((prevPhotos) => [...prevPhotos, photo]);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);

    //hide the header while loading
    navigation.setOptions({ headerShown: false });
    const encodings = photos.map((photo) => {
      return photo.base64;
    });

    const result = await api.extractRecipeInfo(encodings);

    setLoading(false);

    if (result.ok) {
      //TODO: i'd rather do this with goback but it isn't working right now
      //   navigation.goBack({ recipe: result.data });
      console.log(result.data);
      navigation.navigate(routeNames.COOKBOOK_EDIT_RECIPE, {
        recipe: result.data,
      });
    } else {
      Alert.alert(
        "Error",
        "Sorry, we couldn't extract your recipe information, try taking a clearer photo."
      );
    }
  };

  useEffect(() => {
    setPhotos([]);
    takePhoto();
  }, []);

  if (loading) {
    return (
      <LongLoadingAnimation
        visible={loading}
        header="Analyzing your recipe..."
      />
    );
  }

  if (photos.length === 0) {
    return (
      <Screen style={styles.container}>
        <TouchableOpacity
          style={[
            styles.cameraButton,
            {
              position: "absolute",
              alignItems: "center",

              top: "50%",
              left: "50%",
              marginTop: -50,
              marginLeft: -50,
            },
          ]}
          onPress={takePhoto}
        >
          <MaterialCommunityIcons
            name="camera"
            size={50}
            color={colors.white}
          />
        </TouchableOpacity>
      </Screen>
    );
  }

  return (
    <Screen style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        {photos.map((photo, index) => (
          <View style={{ flexDirection: "row" }}>
            <Image
              key={index}
              source={{ uri: photo.uri }}
              style={{ width: 200, height: 200 }}
            />
            <TouchableOpacity
              key={"remove" + index}
              onPress={() => {
                setPhotos((prevPhotos) =>
                  prevPhotos.filter((_, i) => i !== index)
                );
              }}
            >
              <View style={[styles.removeBadge]}>
                <MaterialCommunityIcons
                  //should be a trash can icon
                  name={"trash-can-outline"}
                  size={24}
                  color={colors.white}
                  key={"delete" + index}
                />
              </View>
            </TouchableOpacity>
          </View>
        ))}
        <TouchableOpacity style={styles.cameraButton} onPress={takePhoto}>
          <MaterialCommunityIcons
            name="camera"
            size={50}
            color={colors.white}
          />
        </TouchableOpacity>
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.buttonText}>Submit</Text>
        </TouchableOpacity>
      </ScrollView>
    </Screen>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scroll: {
    padding: 10,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 80,
  },
  cameraButton: {
    backgroundColor: colors.primary,
    width: 80,
    height: 80,
    borderRadius: 40,
    margin: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  submitButton: {
    backgroundColor: colors.danger,
    width: 200,
    height: 50,
    borderRadius: 20,
    margin: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 30,
    fontWeight: "bold",
  },
  removeBadge: {
    padding: 7.5,
    borderRadius: 50,
    position: "absolute",
    top: 2.5,
    right: 2.5,
    borderWidth: 0.5,
    borderColor: colors.white,
    //background should be white but mostly transparent
    backgroundColor: "rgba(255, 255, 255, 0.25)",
  },
});

export default CameraScreen;
