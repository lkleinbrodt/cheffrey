import React from "react";
import { useFormikContext } from "formik";
import { Text, View } from "react-native";

import Picker from "../Picker";
import ErrorMessage from "./ErrorMessage";
import defaultStyles from "../../config/styles";

import colors from "../../config/colors";

function AppFormPicker({
  items,
  name,
  label,
  icon,
  caption,
  isRequired,
  numberOfColumns,
  PickerItemComponent,
  placeholder,
  width,
}) {
  const { errors, setFieldValue, touched, values } = useFormikContext();

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
      <Picker
        items={items}
        numberOfColumns={numberOfColumns}
        onSelectItem={(item) => setFieldValue(name, item.value)}
        PickerItemComponent={PickerItemComponent}
        placeholder={placeholder}
        //this below solution enables us to set the value to just the value (instead of all the other metadata that sits inside the picker item)
        //but perhaps it is not performant on large lists
        selectedItem={items.find((item) => item.value === values[name])}
        width={width}
        icon={icon}
      />
      {caption && <Text style={defaultStyles.formFieldCaption}>{caption}</Text>}
      <ErrorMessage error={errors[name]} visible={touched[name]} />
    </View>
  );
}

const styles = {};

export default AppFormPicker;
