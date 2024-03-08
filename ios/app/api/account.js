import client from "./client";

function register(email, password) {
  return client.post("/register", { email, password });
}

export default {
  register,
};
