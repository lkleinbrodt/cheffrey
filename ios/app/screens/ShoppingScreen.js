import { React, useEffect, useState, useRef } from "react";
import {
  StyleSheet,
  SectionList,
  TouchableOpacity,
  View,
  Text,
  Animated,
} from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import CheckboxItem from "../components/CheckboxItem";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import Message from "../components/Message";
import * as Clipboard from "expo-clipboard";
import defaultStyles from "../config/styles";

const ShoppingScreen = ({ navigation }) => {
  const [ingredientsDict, setIngredientsDict] = useState({});
  const [checkedIngredients, setCheckedIngredients] = useState([]);
  const [error, setError] = useState(false);
  const [copying, setCopying] = useState(false);

  const [loading, setLoading] = useState(true);

  const fetchIngredients = async () => {
    setLoading(true);
    const response = await recipesAPI.loadShoppingList();
    if (!response.ok) return setError(true);
    setIngredientsDict(response.data);
    setLoading(false);
  };

  const onRefresh = async () => {
    setLoading(true);
    fetchIngredients();
    setLoading(false);
  };

  const opacity = useRef(new Animated.Value(0)).current;

  const copyToClipboard = async () => {
    const ingredientsString = Object.values(ingredientsDict).flat().join("\n");

    await Clipboard.setStringAsync(ingredientsString);
    setCopying(true);
    Animated.timing(opacity, {
      toValue: 1,
      duration: 100,
      useNativeDriver: true,
    }).start(() => {
      setTimeout(() => {
        Animated.timing(opacity, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }).start(() => {
          setCopying(false);
        });
      }, 500);
    });
  };

  const cleanUpIngredients = () => {
    //for every ingredient in ingredientsDict, check if it is in checkedIngredients
    //if it is, remove it from that category and add it to the "Already Bought" category
    const updatedIngredientsDict = { ...ingredientsDict };
    for (const category in updatedIngredientsDict) {
      updatedIngredientsDict[category] = updatedIngredientsDict[
        category
      ].filter((ingredient) => !checkedIngredients.includes(ingredient));
    }
    //if the "Already Bought" category doesn't exist, create it
    if (!updatedIngredientsDict["Already Bought"]) {
      updatedIngredientsDict["Already Bought"] = [];
    }

    updatedIngredientsDict["Already Bought"] = [
      ...updatedIngredientsDict["Already Bought"],
      ...checkedIngredients,
    ];
    setIngredientsDict(updatedIngredientsDict);
    setCheckedIngredients([]);
  };

  //whenever the user comes back to this page, fetch the ingredients
  useEffect(() => {
    const unsubscribe = navigation.addListener("focus", () => {
      fetchIngredients();
    });

    return unsubscribe;
  }, [navigation]);

  const renderItem = ({ item }) => (
    //todo: find a way to keep it checked when it moves to already bought.
    <CheckboxItem
      label={item}
      isChecked={false}
      onCheck={() => handleCheckIngredient(item)}
    />
  );

  const renderSectionHeader = ({ section: { title } }) => (
    <View style={styles.categoryHeader}>
      <Text style={styles.categoryHeaderText}>{title}</Text>
      <View style={styles.hr} />
    </View>
  );

  const renderFloatingButton = () => (
    <TouchableOpacity
      style={styles.floatingButton}
      onPress={cleanUpIngredients}
    >
      <MaterialCommunityIcons name="broom" size={24} color={colors.white} />
    </TouchableOpacity>
  );

  const handleCheckIngredient = (ingredient) => {
    const updatedCheckedIngredients = checkedIngredients.includes(ingredient)
      ? checkedIngredients.filter((item) => item !== ingredient)
      : [...checkedIngredients, ingredient];

    setCheckedIngredients(updatedCheckedIngredients);
  };

  if (error) {
    return (
      <Message
        message="Error"
        subMessage="Could not load ingredients. Please try again."
      />
    );
  }

  //if ingredients empty and loading, show loading indicator

  if (loading && Object.keys(ingredientsDict).length === 0) {
    return (
      <Screen style={styles.screen}>
        <LottieActivityIndicator key="loading1" visible={loading} />
      </Screen>
    );
  }

  //if ingredients empty and not loading, show message

  if (!loading & (Object.keys(ingredientsDict).length === 0)) {
    return (
      <Screen style={styles.screen}>
        <Message
          message="Empty"
          subMessage="Add items to your list to see their ingredients here."
        />
      </Screen>
    );
  }

  //otherwise, show ingredients

  return (
    <Screen style={styles.screen}>
      <View style={styles.copyContainer}>
        <TouchableOpacity onPress={copyToClipboard}>
          <MaterialCommunityIcons
            name="clipboard-text-outline"
            size={32}
            color={colors.primary}
          />
        </TouchableOpacity>
        {copying && (
          <Animated.View style={[styles.headsUp, { opacity }]}>
            <Text style={styles.headsUpMessage}>Copied to clipboard</Text>
          </Animated.View>
        )}
      </View>

      <SectionList
        sections={Object.entries(ingredientsDict).map(
          ([category, ingredients]) => ({
            title: category,
            data: ingredients,
          })
        )}
        keyExtractor={(item, index) => item + index}
        renderItem={renderItem}
        renderSectionHeader={renderSectionHeader}
      />
      {renderFloatingButton()}
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    padding: 20,
    position: "relative",
  },
  bulletPoint: {
    marginLeft: 10,
    fontSize: 18,
  },
  categoryHeader: {
    paddingTop: 12,
    paddingBottom: 6,
    paddingHorizontal: 15,
    backgroundColor: colors.background,
  },
  categoryHeaderText: {
    fontSize: 24,
    fontWeight: "bold",
  },
  hr: {
    borderBottomColor: colors.medium,
    borderBottomWidth: 1,
  },
  floatingButton: {
    position: "absolute",
    bottom: 16,
    right: 16,
    backgroundColor: colors.primary,
    padding: 12,
    borderRadius: 30,
    elevation: 5,
  },
  copyContainer: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 10,
    alignItems: "center",
    marginHorizontal: 10,
  },
  headsUp: {
    padding: 5,
    borderRadius: 5,
    justifyContent: "center",
    backgroundColor: colors.tertiary,
  },
  headsUpMessage: {
    ...defaultStyles.text,
    color: colors.primary,
    fontSize: 16,
    fontWeight: "bold",
  },
});

export default ShoppingScreen;
