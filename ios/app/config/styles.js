import { Platform } from "react-native";

import colors from "./colors";

export default {
  colors,
  text: {
    color: colors.dark,
    fontSize: 18,
    fontFamily: Platform.OS === "android" ? "Roboto" : "Avenir",
  },
  textInput: {
    flexDirection: "row",
    color: colors.dark,
    fontSize: 18,
    fontFamily: Platform.OS === "android" ? "Roboto" : "Avenir",
  },

  formFieldContainer: {
    marginVertical: 5,
  },

  formFieldLabel: {
    color: colors.dark,
    fontSize: 18,
    fontFamily: Platform.OS === "android" ? "Roboto" : "Avenir",
    fontWeight: "bold",
  },

  formFieldCaption: {
    color: colors.dark,
    fontFamily: Platform.OS === "android" ? "Roboto" : "Avenir",
    fontSize: 12,
    marginTop: 0,
    fontStyle: "italic",
  },
  formFieldRequiredTag: {
    backgroundColor: colors.lightGrey,
    fontSize: 12,
  },
  formFieldHeaderContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
};
