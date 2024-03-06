import React, { useState } from "react";
import { StyleSheet, Image } from "react-native";
import Screen from "../components/Screen.js";
import {
  Form,
  FormField,
  SubmitButton,
  ErrorMessage,
} from "../components/forms/index.js";
import authAPI from "../api/auth.js";
import * as Yup from "yup";
import useAuth from "../auth/useAuth.js";

//required to properly decode the token
import "core-js/stable/atob";

const validationSchema = Yup.object().shape({
  username: Yup.string().required().label("Username"),
  password: Yup.string().required().min(4).label("Password"),
});

function LoginScreen(props) {
  const auth = useAuth();
  const [loginFailed, setLoginFailed] = useState(false);

  const handleSubmit = async ({ username, password }) => {
    const result = await authAPI.login(username, password);
    if (!result.ok) return setLoginFailed(true);
    setLoginFailed(false);
    auth.logIn(result.data);
  };
  return (
    <Screen style={styles.container}>
      <Image source={require("../assets/chef.png")} style={styles.logo} />
      <Form
        initialValues={{ email: "", password: "" }}
        onSubmit={handleSubmit}
        validationSchema={validationSchema}
      >
        <ErrorMessage
          error="Invalid username or password"
          visible={loginFailed}
        />
        <FormField
          autoCapitalize="none"
          autoCorrect={false}
          icon="account"
          name="username"
          placeholder="Username"
          textContentType="username"
        />
        <FormField
          autoCapitalize="none"
          autoCorrect={false}
          icon="lock"
          name="password"
          placeholder="Password"
          secureTextEntry
          textContentType="password"
        />
        <SubmitButton title="Login" />
      </Form>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
  logo: {
    width: 80,
    height: 80,
    alignSelf: "center",
    marginTop: 50,
    marginBottom: 20,
  },
});

export default LoginScreen;

// const L = () => {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");

//   useEffect(() => {
//     SecureStore.getItemAsync("token").then((token) => {
//       console.log("Token:", token);
//       // If token exists, redirect to another page
//       if (token) {
//         console.log("Token exists:", token);
//         router.replace("tabs/explore");
//       }
//     });
//   }, []);

//   const handleLogin = async () => {
//     // Validate inputs
//     if (!username || !password) {
//       Alert.alert("Error", "Please enter both username and password");
//       return;
//     }

//     try {
//       const response = await axios.post("/login", {
//         username,
//         password,
//       });

//       if (response.data.access_token) {
//         SecureStore.setItemAsync("token", response.data.access_token);
//         router.replace("tabs/explore");
//       } else {
//         Alert.alert("Error", "Invalid username or password");
//       }
//     } catch (error) {
//       console.error("Error logging in", error);
//       Alert.alert("Error", "Invalid username or password");
//     }
//   };

//   return (
//     <Screen style={styles.container}>
//       <View style={styles.imageContainer}>
//         <Image source={CheffreyLogo} style={styles.image} />
//       </View>
//       <Text style={styles.title}>Cheffrey</Text>
//       <Pressable onPress={() => Keyboard.dismiss()}>
//         <View>
//           <TextInput
//             style={styles.input}
//             placeholder="Username"
//             onChangeText={(text) => setUsername(text)}
//             value={username}
//             placeholderTextColor="grey"
//             autoCapitalize="none"
//           />
//         </View>
//       </Pressable>

//       <Pressable onPress={() => Keyboard.dismiss()}>
//         <TextInput
//           style={styles.input}
//           placeholder="Password"
//           secureTextEntry
//           onChangeText={(text) => setPassword(text)}
//           value={password}
//           placeholderTextColor="grey"
//         />
//       </Pressable>

//       <LoginButton onPress={handleLogin} />
//     </Screen>
//   );
// };

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     backgroundColor: "#faf1e4",
//     alignItems: "center",
//   },
//   imageContainer: {
//     paddingTop: 30,
//   },
//   image: {
//     width: 320,
//     height: 320,
//     borderRadius: 18,
//   },
//   title: {
//     fontSize: 36,
//     color: "#435334",
//     marginTop: 20,
//     textAlign: "center",
//     marginBottom: 0,
//     paddingBottom: 0,
//   },
//   input: {
//     height: 40,
//     width: 120,
//     borderColor: "gray",
//     borderWidth: 1,
//     marginBottom: 10,
//     paddingLeft: 10,
//   },
//   buttonText: {
//     color: "white",
//     fontSize: 16,
//     textAlign: "center",
//   },
// });

// export default LoginScreen;
