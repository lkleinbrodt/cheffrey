// import React, { useState, useEffect } from "react";
// import {
//   View,
//   ScrollView,
//   StyleSheet,
//   RefreshControl,
//   TouchableOpacity,
//   Text,
//   Button,
// } from "react-native";
// import RecipeCard from "./RecipeCard";
// import routes from "../navigation/routes";
// import colors from "../config/colors";

// const RecipeGrid = ({ recipes, navigation, onScrollToBottom, onRefresh }) => {
//   const [refreshing, setRefreshing] = useState(false);
//   const [doneScrolling, setDoneScrolling] = useState(false);
//   const scrollViewRef = React.createRef();

//   const handleRefresh = () => {
//     setRefreshing(true);
//     onRefresh();
//     setRefreshing(false);
//   };
//   const handleScroll = (event) => {
//     const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;

//     const isCloseToBottom =
//       layoutMeasurement.height + contentOffset.y >= contentSize.height - 5000;

//     if (isCloseToBottom) {
//       const reached_bottom = onScrollToBottom();
//       if (reached_bottom) {
//         setDoneScrolling(true);
//         console.log("Reached bottom");
//       }
//     }
//   };

//   const scrollToTop = () => {
//     if (scrollViewRef.current) {
//       scrollViewRef.current.scrollTo({ y: 0, animated: true });
//     }
//   };

//   return (
//     <View>
//       <ScrollView
//         ref={scrollViewRef}
//         onScroll={handleScroll}
//         scrollEventThrottle={0}
//         refreshControl={
//           <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
//         }
//       >
//         <View style={styles.GridContainer}>
//           {recipes.map((recipe) => (
//             <RecipeCard
//               recipe={recipe}
//               key={recipe.id}
//               onPress={() =>
//                 navigation.navigate(routes.RECIPE_DETAILS, { recipe })
//               }
//             />
//           ))}
//         </View>
//         {doneScrolling && (
//           <TouchableOpacity
//             style={styles.scrollToTopButton}
//             onPress={scrollToTop}
//           >
//             <Text style={styles.scrollToTopButtonText}>Back to Top</Text>
//           </TouchableOpacity>
//         )}
//       </ScrollView>
//     </View>
//   );
// };

// const styles = StyleSheet.create({
// GridContainer: {
//   flex: 1,
//   marginBottom: 16,
//   justifyContent: "center",
//   alignItems: "center",
// },
//   scrollToTopButton: {
//     backgroundColor: colors.secondary,
//     padding: 10,
//     borderRadius: 5,
//     marginVertical: 20,
//     justifyContent: "center",
//     width: "33%", // Fixed width of 33% of the screen
//     alignSelf: "center", // Center the button horizontally
//   },
//   scrollToTopButtonText: {
//     color: colors.primary,
//     fontSize: 16,
//     textAlign: "center",
//   },
// });

// export default RecipeGrid;

//flatlist approach, which was actually much slower :/
import React, { useState } from "react";
import {
  View,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Text,
  Button,
} from "react-native";
import RecipeCard from "./RecipeCard";
import routes from "../navigation/routes";
import colors from "../config/colors";

const RecipeGrid = ({
  recipes,
  navigation,
  navigateScreen,
  onScrollToBottom,
  onRefresh,
  searchBar,
  footer,
}) => {
  const [refreshing, setRefreshing] = useState(false);

  const flatListRef = React.useRef();

  const handleRefresh = () => {
    setRefreshing(true);
    onRefresh();
    setRefreshing(false);
  };

  const scrollToTop = () => {
    flatListRef.current?.scrollToOffset({ offset: 0, animated: true });
  };

  const renderItem = ({ item }) => (
    <View style={styles.GridContainer}>
      <RecipeCard
        recipe={item}
        onPress={() => navigation.navigate(navigateScreen, { recipe: item })}
      />
    </View>
  );

  const keyExtractor = (item) => item.id.toString();

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={recipes}
        keyExtractor={keyExtractor}
        renderItem={renderItem}
        onEndReached={onScrollToBottom}
        onEndReachedThreshold={0.8}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        ListHeaderComponent={searchBar}
        ListFooterComponent={
          footer ?? (
            <TouchableOpacity
              style={styles.scrollToTopButton}
              onPress={scrollToTop}
            >
              <Text style={styles.scrollToTopButtonText}>Back to Top</Text>
            </TouchableOpacity>
          )
        }
      />
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
  scrollToTopButton: {
    backgroundColor: colors.secondary,
    padding: 10,
    borderRadius: 5,
    marginVertical: 20,
    justifyContent: "center",
    width: "33%", // Fixed width of 33% of the screen
    alignSelf: "center", // Center the button horizontally
  },
  scrollToTopButtonText: {
    color: colors.primary,
    fontSize: 16,
    textAlign: "center",
  },
});

export default RecipeGrid;
