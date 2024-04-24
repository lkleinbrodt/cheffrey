import * as SecureStore from "expo-secure-store";
import { jwtDecode } from "jwt-decode";
const key = "authToken";
const storeToken = async (authToken) => {
  try {
    await SecureStore.setItemAsync(key, authToken);
  } catch (error) {
    console.log("Error storing the auth token", error);
  }
};

const getToken = async () => {
  try {
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.log("Error getting the auth token", error);
  }
};

const removeToken = async () => {
  try {
    await SecureStore.deleteItemAsync(key);
  } catch (error) {
    console.log("Error removing the auth token", error);
  }
};

const removeRefreshToken = async () => {
  try {
    await SecureStore.deleteItemAsync("refreshToken");
  } catch (error) {
    console.log("Error removing the refresh token", error);
  }
};

const storeRefreshToken = async (refreshToken) => {
  try {
    await SecureStore.setItemAsync("refreshToken", refreshToken);
  } catch (error) {
    console.log("Error storing the refresh token", error);
  }
};

const getRefreshToken = async () => {
  try {
    return await SecureStore.getItemAsync("refreshToken");
  } catch (error) {
    console.log("Error getting the refresh token", error);
  }
};

const getUser = async () => {
  const token = await getToken();
  return token ? jwtDecode(token) : null;
};

const getAuthExpiration = async () => {
  const token = await getToken();
  return token ? jwtDecode(token).exp : null;
};

export default {
  getUser,
  getToken,
  storeToken,
  removeToken,
  getAuthExpiration,
  storeRefreshToken,
  removeRefreshToken,
  getRefreshToken,
};
