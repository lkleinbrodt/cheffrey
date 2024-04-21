import client from "./client";

function register(email, password) {
  return client.post("/register", { email, password });
}

function changePassword(currentPassword, newPassword) {
  console.log("hitting api");
  return client.post("/change-password", {
    currentPassword,
    newPassword,
  });
}

export default {
  register,
  changePassword,
};
