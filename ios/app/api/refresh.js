import { create } from "apisauce";
import authStorage from "../auth/storage";
import config from "../../config";
import { Alert } from "react-native";

// creating a different client just for refreshing the token
// to avoid infinite loops (is there a better way to do this?)

const refreshClient = create({
  baseURL: config.baseURL,
  timeout: 10000,
});

const isTokenExpired = async (buffer = 5 * 60) => {
  const expiration = await authStorage.getAuthExpiration();
  if (!expiration) return true;
  const now = new Date().getTime() / 1000;
  const diff = expiration - now;
  if (diff < buffer) {
    return true;
  }
  return false;
};

async function refreshAccessToken(logOut) {
  try {
    const refreshToken = await authStorage.getRefreshToken();

    if (!refreshToken) {
      throw new Error("Refresh token not found");
    }

    const response = await refreshClient.post(
      "/refresh",
      {},
      {
        headers: { Authorization: `Bearer ${refreshToken}` },
      }
    );

    if (response.status === 401) {
      console.log("refresh token expired");
      logOut();
      Alert.alert("Session expired", "Please log in again");
      return;
    }

    const newAccessToken = response.data.access_token;
    authStorage.storeToken(newAccessToken);
  } catch (error) {
    console.error("Token refresh error:", error);
    logOut();
    Alert.alert("Session expired", "Please log in again");
    throw error;
  }
}

export { refreshAccessToken, isTokenExpired };
