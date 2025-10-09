<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="bg-white shadow-lg rounded-xl p-8 w-full max-w-sm text-center">
      <!-- Logo -->
      <img
        src="@/assets/logo.png"
        alt="Company Logo"
        class="mx-auto bg-auto mb-4"
      />

      <h1 class="text-xl font-bold text-gray-800 mb-6">MACHINE SHOP</h1>

      <!-- Login Form -->
      <form @submit.prevent="login" class="space-y-4">
        <div class="text-left">
          <label class="block font-medium text-gray-700 mb-1" for="username">
            Username
          </label>
          <input
            id="username"
            type="text"
            v-model="username"
            class="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400 outline-none"
            placeholder="Enter username"
            required
          />
        </div>

        <div class="text-left">
          <label class="block font-medium text-gray-700 mb-1" for="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            v-model="password"
            class="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400 outline-none"
            placeholder="Enter password"
            required
          />
        </div>

        <button
          type="submit"
          class="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg transition"
        >
          Login
        </button>
      </form>

      <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";

const router = useRouter();
const username = ref("");
const password = ref("");
const error = ref("");

async function login() {
  error.value = "";
  try {
    const formData = new URLSearchParams();
    formData.append("username", username.value);
    formData.append("password", password.value);

    const res = await api.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    localStorage.setItem("token", res.data.access_token);
    alert("Login successful!");
    router.push("/dashboard");
  } catch (err) {
    console.error(err);
    error.value = "Invalid username or password.";
  }
}
</script>

