// axiosConfig.js
import axios from "axios";
import * as SecureStore from "expo-secure-store";

const instance = axios.create({
  baseURL: "http://10.0.0.72:5001/", // Replace with your actual API base URL
  timeout: 10000, // Set a timeout (optional)
  withCredentials: true,
});

export default instance;
