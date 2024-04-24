import { useEffect } from "react";
import useAuth from "../auth/useAuth";
import apiClient from "./client";
import authStorage from "../auth/storage";
import { refreshAccessToken } from "./refresh";

function ApiInterceptor(props) {
  const { user, logOut } = useAuth();
  let refreshing = null;

  const addTransformers = () => {
    const requestTransformers = apiClient.asyncRequestTransforms.length;
    const responseTransformers = apiClient.asyncResponseTransforms.length;
    const transformersAdded = requestTransformers + responseTransformers > 1;

    if (!transformersAdded) {
      apiClient.addAsyncRequestTransform(async (request) => {
        const authToken = await authStorage.getToken();

        if (!authToken) {
          return;
        }
        request.headers["Authorization"] = "Bearer " + authToken;
      });

      // check for a 401 response (expired access token), use refresh token to fetch new access token, retry request
      apiClient.addAsyncResponseTransform(async (response) => {
        if (response.ok) {
          return response.data;
        }

        if (response.problem) {
          const originalConfig = response.config;

          //Access Token was expired, grab a fresh one using the refresh token and try again

          if (
            originalConfig.url !== "/login" &&
            response.status === 401 &&
            !originalConfig.retry
          ) {
            // setting retry flag to allow retrying once and not loop infinitely
            originalConfig.retry = true;
            try {
              const token = await authStorage.getRefreshToken();
              if (token) {
                // first request to refresh will call the method, all the other requests will await the promise
                // so only one call to refresh will be made in the case of multile async 401s
                refreshing = refreshing
                  ? refreshing
                  : refreshAccessToken(logOut);
                await refreshing;
                refreshing = null;

                return apiClient.any(originalConfig);
              } else {
                console.log("refresh token not found, logging user out");
                return logOut();
              }
            } catch (_error) {
              console.log("error checking refresh token, logging user out");
              return logOut();
            }
          }

          // return Promise.reject(response.problem);
          return response;
        }
      });
    }
  };

  useEffect(() => {
    addTransformers();
  }, []);

  return null;
}

export default ApiInterceptor;
