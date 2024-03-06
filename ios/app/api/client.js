import { create } from "apisauce";

const apiClient = create({
  baseURL: "http://10.0.0.72:5001/",
  timeout: 10000,
});

export default apiClient;
