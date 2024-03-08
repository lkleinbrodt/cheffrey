import { create } from "apisauce";
import authStorage from "../auth/storage";
// import cache from "../utility/cache";

const apiClient = create({
  baseURL: "http://10.0.0.72:5001/api/",
  timeout: 10000,
});

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

apiClient.addAsyncRequestTransform(async (request) => {
  const authToken = await authStorage.getToken();
  if (!authToken) return;
  request.headers["Authorization"] = `Bearer ${authToken}`;
  request.headers["x-auth-token"] = authToken;
});

export default apiClient;
