<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="login">
      <div>
        <label for="username">Username</label>
        <input
          type="text"
          v-model="username"
          id="username"
          placeholder="Enter username"
          required
        />
      </div>

      <div>
        <label for="password">Password</label>
        <input
          type="password"
          v-model="password"
          id="password"
          placeholder="Enter password"
          required
        />
      </div>

      <button type="submit">Login</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from "axios";
import { useRouter } from "vue-router";
import { ref } from "vue";
import api from "../api/axios";

export default {
  name: "LoginPage",
  data() {
    return {
      username: "",
      password: "",
      error: ""
    };
  },
  methods: {
    async login() {
      this.error = "";
      try {
        // Create form-encoded data for FastAPI OAuth2PasswordRequestForm
        const formData = new URLSearchParams();
        formData.append("username", this.username);
        formData.append("password", this.password);

        // Send POST request
        const response = await api.post(
          "/auth/login",
          formData,
          {
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
          }
        );

        // Store token in localStorage for future authenticated requests
        localStorage.setItem("token", response.data.access_token);

        alert("Login successful!");
        this.$router.push("/dashboard"); // Redirect after login (adjust route)
      } catch (err) {
        this.error = "Invalid username or password.";
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  text-align: center;
}

input {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 10px;
}

button {
  background: #42b983;
  color: white;
  padding: 10px;
  border: none;
  width: 100%;
  cursor: pointer;
  border-radius: 5px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
