import React, { useState } from "react";
import { View, TextInput, StyleSheet } from "react-native";

const SearchBar = ({ onSearch }) => {
  const [searchText, setSearchText] = useState("");

  const handleSearch = () => {
    onSearch(searchText);
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Enter search text"
        value={searchText}
        onChangeText={(text) => setSearchText(text)}
        onSubmitEditing={handleSearch} // Trigger search on "return" or "search" button press
        returnKeyType="search" // Set the keyboard return key type to "search"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 10,
    paddingHorizontal: 30,
    position: "relative",
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 5,
    padding: 8,
  },
});

export default SearchBar;
