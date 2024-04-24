import React from "react";
import { useFormikContext } from "formik";
import { Text, View, TouchableOpacity } from "react-native";
import TextInput from "../TextInput";
import ErrorMessage from "./ErrorMessage";
import defaultStyles from "../../config/styles";
import colors from "../../config/colors";
import { FieldArray, Field } from "formik";
import Button from "../Button";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { array } from "yup";

function AppFormList({
  name,
  width,
  label,
  isRequired,
  itemName,
  ...otherProps
}) {
  const { setFieldTouched, handleChange, errors, touched, values } =
    useFormikContext();
  const style = otherProps.style || defaultStyles.textInput;

  const handleBlur = (index, arrayHelpers) => {
    setFieldTouched(`${name}.${index}`);
    if (index === values[name].length - 1) {
      if (values[name][index] !== "") {
        arrayHelpers.push("");
      }
    }
  };

  return (
    <FieldArray
      name={name}
      render={(arrayHelpers) => (
        <View style={defaultStyles.formFieldContainer}>
          {label || isRequired ? (
            <View style={defaultStyles.formFieldHeaderContainer}>
              {label && (
                <Text style={defaultStyles.formFieldLabel}>{label}</Text>
              )}
              {isRequired && (
                <Text style={defaultStyles.formFieldRequiredTag}>
                  {"REQUIRED"}
                </Text>
              )}
            </View>
          ) : null}
          {values[name] && values[name].length > 0
            ? values[name].map((item, index) => (
                <>
                  <View key={index} style={styles.listRow}>
                    <TextInput
                      onBlur={() => handleBlur(index, arrayHelpers)}
                      onChangeText={handleChange(`${name}.${index}`)}
                      style={style}
                      width="90%"
                      value={item} // use item or use values[name][index] to get the value?
                      {...otherProps}
                      key={"input" + index}
                    />
                    <TouchableOpacity
                      style={styles.minusButton}
                      onPress={() => arrayHelpers.remove(index)}
                      key={"button" + index}
                    >
                      <MaterialCommunityIcons
                        name="trash-can-outline"
                        size={20}
                        color="red"
                      />
                    </TouchableOpacity>
                  </View>
                  {errors[name] && errors[name] && touched[name] ? (
                    <ErrorMessage
                      error={errors[name][index]}
                      visible={touched[name][index]}
                      key={"error" + index}
                    />
                  ) : null}
                </>
              ))
            : null}
          <TouchableOpacity
            style={styles.plusButton}
            onPress={() => arrayHelpers.push("")}
          >
            <MaterialCommunityIcons
              name="plus-circle"
              size={40}
              color={colors.primary}
            />
          </TouchableOpacity>

          {errors[name] ? (
            <ErrorMessage
              error={errors[name]}
              visible={touched[name] && typeof errors[name] === "string"} //if errors[name] is an array, it means that the error is in one of the items
            />
          ) : null}
        </View>
      )}
    />
  );
}

const styles = {
  listRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  minusButton: {
    justifyContent: "center",
    alignItems: "center",
    padding: 5,
  },
  plusButton: {
    padding: 5,
  },
};

export default AppFormList;
