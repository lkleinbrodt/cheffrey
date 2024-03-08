import { React, useEffect, useState, useContext } from "react";
import {
  StyleSheet,
  SectionList,
  TouchableOpacity,
  View,
  Text,
  FlatList,
} from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import CheckboxItem from "../components/CheckboxItem";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import Message from "../components/Message";

const ShoppingScreen = ({ navigation }) => {
  const [ingredientsDict, setIngredientsDict] = useState({});
  const [checkedIngredients, setCheckedIngredients] = useState([]);

  const [loading, setLoading] = useState(false);

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

  useEffect(() => {
    fetchIngredients();
  }, []);

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

  return (
    <Screen style={styles.screen}>
      <LottieActivityIndicator key="loading1" visible={loading} />
      {Object.keys(ingredientsDict).length === 0 ? (
        <Message
          message="Empty"
          subMessage="Add items to your list to see their ingredients here."
        />
      ) : (
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
      )}
      {renderFloatingButton()}
    </Screen>
  );
};

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    padding: 10,
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
});

export default ShoppingScreen;
