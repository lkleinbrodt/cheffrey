import { useContext } from "react";
import AuthContext from "./context";
import authStorage from "./storage";
import { jwtDecode } from "jwt-decode";

const useAuth = () => {
  const { user, setUser } = useContext(AuthContext);

  const logOut = () => {
    setUser(null);
    authStorage.removeToken();
    authStorage.removeRefreshToken();
  };

  const logIn = (authToken, refreshToken) => {
    const user = jwtDecode(authToken);
    setUser(user);
    authStorage.storeToken(authToken);
    authStorage.storeRefreshToken(refreshToken);
  };

  return { user, setUser, logOut, logIn };
};

export default useAuth;
