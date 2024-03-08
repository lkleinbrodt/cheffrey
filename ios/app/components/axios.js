// axiosConfig.js
import axios from "axios";

const instance = axios.create({
  baseURL: "http://10.0.0.72:5001/", // Replace with your actual API base URL
  timeout: 5000, // Set a timeout (optional)
  withCredentials: true,
});

export default instance;
