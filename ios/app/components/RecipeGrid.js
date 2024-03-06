import { React, useEffect, useState, useContext } from "react";
import { View, ScrollView, StyleSheet, RefreshControl } from "react-native";
import RecipeCard from "./RecipeCard";
import routes from "../navigation/routes";

const RecipeGrid = ({ recipes, navigation, onScrollToBottom, onRefresh }) => {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    onRefresh();
    setRefreshing(false);
  };
  const handleScroll = (event) => {
    const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;

    const isCloseToBottom =
      layoutMeasurement.height + contentOffset.y >= contentSize.height - 100;

    if (isCloseToBottom) {
      onScrollToBottom();
    }
  };

  return (
    <View>
      <ScrollView
        onScroll={handleScroll}
        scrollEventThrottle={0}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        <View style={styles.GridContainer}>
          {recipes.map((recipe) => (
            <RecipeCard
              recipe={recipe}
              key={recipe.id}
              onPress={() =>
                navigation.navigate(routes.RECIPE_DETAILS, { recipe })
              }
            />
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  GridContainer: {
    flex: 1,
    marginBottom: 16,
    justifyContent: "center",
    alignItems: "center",
  },
});

export default RecipeGrid;
