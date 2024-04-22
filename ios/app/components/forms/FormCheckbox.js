// import React from "react";
// import { Text, View } from "react-native";
// import defaultStyles from "../../config/styles";
// import colors from "../../config/colors";
// import BouncyCheckbox from "react-native-bouncy-checkbox";

// function AppFormCheckbox({ name, formRef, header, label }) {
//   // i dont think this will play as nicely with the formik context as other stuff
//   // but it works well enough so far

//   return (
//     <>
//       <Text style={defaultStyles.text}>{header}</Text>
//       <View style={styles.checkboxContainer}>
//         <BouncyCheckbox
//           onPress={(value) => {
//             formRef.current.setFieldValue(name, value);
//           }}
//           fillColor={colors.primary}
//         />
//         <Text style={defaultStyles.text}>{label}</Text>
//       </View>
//     </>
//   );
// }

// const styles = {
//   checkboxContainer: {
//     flexDirection: "row",
//     alignItems: "center",
//     marginBottom: 20,
//     marginTop: 10,
//     marginLeft: 10,
//   },
// };

// export default AppFormCheckbox;
