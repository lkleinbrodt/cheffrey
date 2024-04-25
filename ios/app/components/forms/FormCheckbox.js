import React from "react";
import { Text, View } from "react-native";
import defaultStyles from "../../config/styles";
import colors from "../../config/colors";
import BouncyCheckbox from "react-native-bouncy-checkbox";

function AppFormCheckbox({ name, formRef, header, label, initialValue }) {
  // i dont think this will play as nicely with the formik context as other stuff
  // but it works well enough so far

  const [checked, setChecked] = React.useState(initialValue);

  return (
    <>
      <Text style={defaultStyles.formFieldLabel}>{header}</Text>
      <View style={styles.checkboxContainer}>
        <BouncyCheckbox
          onPress={(value) => {
            formRef.current.setFieldValue(name, value);
            setChecked(value);
          }}
          fillColor={colors.primary}
          isChecked={checked}
        />
        <Text style={defaultStyles.text}>{label}</Text>
      </View>
    </>
  );
}

const styles = {
  checkboxContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    marginTop: 10,
    marginLeft: 10,
  },
};

export default AppFormCheckbox;
