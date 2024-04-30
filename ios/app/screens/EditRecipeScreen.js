import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  TouchableOpacity,
} from "react-native";
import {
  Form,
  FormField,
  SubmitButton,
  FormPicker,
  FormCheckbox,
  FormList,
} from "../components/forms";

import Screen from "../components/Screen";
import defaultStyles from "../config/styles";
import colors from "../config/colors";
import * as Yup from "yup";
import routeNames from "../navigation/routeNames";
import recipesAPI from "../api/recipes";
import { MaterialCommunityIcons } from "@expo/vector-icons";

const validationSchema = Yup.object().shape({
  title: Yup.string().required().min(1).label("Title"),
  description: Yup.string().label("Description"),
  ingredients: Yup.array()
    .of(Yup.string().required("No blank ingredients").min(1))
    .required("At least one ingredient is required")
    .min(1, "At least one ingredient is required")
    .label("Ingredients"),
  instructions: Yup.string().min(1).label("Instructions"),
  category: Yup.string().required().nullable().label("Category"),
  is_public: Yup.boolean().label("Public"),
});

const initializeFormData = (initialFormData) => {
  //for each key in validationSchema, check if a value exists in initialFormData
  //if it does not, add it to initialFormData with a value of ""
  //you have to do this because Formik requires all fields to have initial values
  //and it only uses initial values on first mount, so they have to be ready immediately

  //do this elsewhere
  //if instructions is in initialFormData, and if it's an array, join it with newlines
  if (initialFormData.instructions) {
    if (Array.isArray(initialFormData.instructions)) {
      initialFormData.instructions = initialFormData.instructions.join("\n");
    }
  }

  const schemaKeys = Object.keys(validationSchema.fields);
  const initialFormDataKeys = Object.keys(initialFormData);
  const missingKeys = schemaKeys.filter(
    (key) => !initialFormDataKeys.includes(key)
  );
  const newInitialFormData = { ...initialFormData };
  missingKeys.forEach((key) => {
    if (key === "ingredients") newInitialFormData[key] = [];
    else if (key === "is_public") newInitialFormData[key] = true;
    else newInitialFormData[key] = "";
  });

  return newInitialFormData;
};

const EditRecipeScreen = ({ navigation, route }) => {
  const [recipeData, setRecipeData] = useState(
    initializeFormData(route.params.recipe)
  );
  console.log(route.params);
  const formRef = useRef();

  const goToCamera = () => {
    navigation.navigate(routeNames.CAMERA);
  };

  useEffect(() => {
    if (route.params.recipe) {
      setRecipeData(initializeFormData(route.params.recipe));
    }
  }, [route.params.recipe]);

  const handleSubmit = async () => {
    const values = formRef.current.values;

    const newRecipeData = { ...recipeData, ...values };

    //take the array and remove commas from every item, then join them back together with commas
    newRecipeData.ingredients = newRecipeData.ingredients
      .map((ingredient) => ingredient.replace(",", ""))
      .join(", ");

    if (recipeData.id) {
      newRecipeData.id = recipeData.id;
      const response = await recipesAPI.updateRecipe(newRecipeData);
      if (!response.ok) {
        Alert.alert("Error", "Could not update recipe.");
        return;
      }
      Alert.alert("Success", "Recipe updated successfully.");
    } else {
      const response = await recipesAPI.createRecipe(newRecipeData);
      if (!response.ok) {
        if (response.data.error === "Recipe already exists") {
          Alert.alert("Error", "This recipe already exists.");
          return;
        } else if (
          response.data.error === "Recipe with that title already exists"
        ) {
          Alert.alert("Error", "A recipe with this title already exists.");
          return;
        }
        Alert.alert("Error", "Could not create recipe.");
        return;
      }
      if (route.params.fromCookbook) {
        const recipeID = response.data.id;
        console.log("Adding to cookbook", recipeID);
        const response2 = await recipesAPI.addToCookbook(recipeID);
        if (!response2.ok) {
          Alert.alert("Error", "Could not add recipe to cookbook.");
        }
        Alert.alert("Success", "Recipe created successfully.");
      }
    }

    navigation.goBack();
  };

  return (
    <Screen style={styles.container}>
      <ScrollView>
        <TouchableOpacity style={styles.cameraButton} onPress={goToCamera}>
          <MaterialCommunityIcons
            name="camera"
            size={40}
            color={colors.primary}
          />
        </TouchableOpacity>
        <Form
          enableReinitialize={true}
          initialValues={recipeData}
          onSubmit={handleSubmit}
          validationSchema={validationSchema}
          innerRef={formRef}
        >
          <FormField name="title" label="Title" isRequired={true} />
          <FormField
            name="description"
            label="Description"
            isRequired={false}
          />
          <FormPicker
            name="category"
            label="Category"
            items={[
              { label: "Breakfast", value: "breakfast" },
              { label: "Lunch", value: "lunch" },
              { label: "Dinner", value: "dinner" },
              { label: "Dessert", value: "dessert" },
              { label: "Snack", value: "snack" },
              { label: "other", value: "other" },
            ]}
            isRequired={true}
            placeholder={"Select one..."}
          />

          {/* TODO: ingredients, which is some sort of list thing. */}

          <FormList name="ingredients" label="Ingredients" isRequired={true} />

          <FormField
            name="instructions"
            label="Instructions"
            isRequired={false}
            multiline={true}
            numberOfLines={10}
            height={200}
            autoCapitalize="sentences"
            autoCorrect={true}
          />

          <FormCheckbox
            name="is_public"
            header="Visibility"
            label="This recipe is public."
            formRef={formRef}
            initialValue={recipeData.is_public}
          />
          <SubmitButton title="Save" />
        </Form>
      </ScrollView>
    </Screen>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
});

export default EditRecipeScreen;
