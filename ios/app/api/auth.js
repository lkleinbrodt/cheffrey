import client from "./client";

const login = async (email, password) => {
  try {
    return await client.post("/login", { email, password });
  } catch (error) {
    console.error("An error occurred during login:", error);
    throw error;
  }
};

export default {
  login,
};
