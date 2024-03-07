import { React, useEffect, useState, useContext } from "react";
import {
  StyleSheet,
  SectionList,
  TouchableOpacity,
  View,
  Text,
} from "react-native";
import LottieActivityIndicator from "../components/ActivityIndicator";
import RecipeGrid from "../components/RecipeGrid";
import colors from "../config/colors";
import Screen from "../components/Screen";
import recipesAPI from "../api/recipes";
import CheckboxItem from "../components/CheckboxItem";

const ShoppingScreen = ({ navigation }) => {
  const [ingredientsDict, setIngredientsDict] = useState({});
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

  useEffect(() => {
    fetchIngredients();
  }, []);

  const renderItem = ({ item }) => <CheckboxItem label={item} />;

  const renderSectionHeader = ({ section: { title } }) => (
    <View style={styles.categoryHeader}>
      <Text style={styles.categoryHeaderText}>{title}</Text>
      <View style={styles.hr} />
    </View>
  );

  return (
    <Screen style={styles.screen}>
      {loading ? (
        <LottieActivityIndicator />
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
});

export default ShoppingScreen;
