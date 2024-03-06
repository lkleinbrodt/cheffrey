import { create } from "apisauce";
import authStorage from "../auth/storage";
const apiClient = create({
  baseURL: "http://10.0.0.72:5001/api/",
  timeout: 10000,
});

apiClient.addAsyncRequestTransform(async (request) => {
  const authToken = await authStorage.getToken();
  if (!authToken) return;
  request.headers["Authorization"] = `Bearer ${authToken}`;
  request.headers["x-auth-token"] = authToken;
  console.log("Request: ", request);
});

export default apiClient;
