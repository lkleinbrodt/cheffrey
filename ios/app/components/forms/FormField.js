import React from "react";
import { useFormikContext } from "formik";
import { Text, View } from "react-native";
import TextInput from "../TextInput";
import ErrorMessage from "./ErrorMessage";
import defaultStyles from "../../config/styles";
import colors from "../../config/colors";

function AppFormField({
  name,
  width,
  label,
  caption,
  isRequired,
  ...otherProps
}) {
  const { setFieldTouched, handleChange, errors, touched, values } =
    useFormikContext();

  const style = otherProps.style || defaultStyles.textInput;
  const inputWidth = otherProps.width || "100%";

  return (
    <View style={defaultStyles.formFieldContainer}>
      {label || isRequired ? (
        <View style={defaultStyles.formFieldHeaderContainer}>
          {label && <Text style={defaultStyles.formFieldLabel}>{label}</Text>}
          {isRequired && (
            <Text style={defaultStyles.formFieldRequiredTag}>{"REQUIRED"}</Text>
          )}
        </View>
      ) : null}
      <TextInput
        onBlur={() => setFieldTouched(name)}
        onChangeText={handleChange(name)}
        style={[style, { width: inputWidth }]}
        value={values[name]}
        {...otherProps}
      />
      {caption && <Text style={defaultStyles.formFieldCaption}>{caption}</Text>}
      <ErrorMessage error={errors[name]} visible={touched[name]} />
    </View>
  );
}

const styles = {};

export default AppFormField;
