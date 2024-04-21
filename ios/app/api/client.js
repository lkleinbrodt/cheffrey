import { create } from "apisauce";
import config from "../../config";
// import { refreshAccessToken, isTokenExpired } from "./refresh";

const apiClient = create({
  baseURL: config.baseURL,
  timeout: 10000,
});

// const addAuthToken = async (request) => {
//   const authToken = await authStorage.getToken();
//   if (!authToken) return;

//   if (await isTokenExpired()) {
//     refreshAccessToken();
//   }

//   request.headers["Authorization"] = `Bearer ${authToken}`;
// };

// apiClient.addAsyncRequestTransform(addAuthToken);

export default apiClient;

//TODO: black/whitelist for which requests to cache
// const get = apiClient.get;
// apiClient.get = async (url, params, axiosConfig) => {
//   //
//   const response = await get(url, params, axiosConfig);
//   if (response.ok) {
//     cache.store(url, response.data);
//     return response;
//   }

//   const data = await cache.get(url);
//   return data ? { ok: true, data } : response;
// };
