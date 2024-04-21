import client from "./client";

function register(email, password) {
  return client.post("/register", { email, password });
}

function changePassword(currentPassword, newPassword) {
  return client.post("/change-password", {
    currentPassword,
    newPassword,
  });
}

function sendVerificationEmail() {
  return client.get("/send-verification-email");
}

function sendForgotPasswordEmail(email) {
  return client.post("/forgot-password", { email });
}

function changeForgotPassword(passwordInfo) {
  //TODO: perhaps this should be unified with changePassword
  //i didnt, because this one does not require a user to be logged in to work
  return client.post("/change-forgot-password", passwordInfo);
}

export default {
  register,
  changePassword,
  sendVerificationEmail,
  sendForgotPasswordEmail,
  changeForgotPassword,
};
