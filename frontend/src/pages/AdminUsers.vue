<template>
  <div class="p-6">
    <h1 class="text-lg sm:text-2xl font-bold mb-6">Manage Users</h1>

    <!-- Add User Form -->
    <div class="bg-white shadow-md rounded-lg p-4 mb-6">
      <h2 class="text-xl font-semibold mb-3">Add New User</h2>
      <form @submit.prevent="createUser" class="space-y-3">
        <input v-model="newUser.username" placeholder="Username" class="border p-2 rounded w-full" />
        <input v-model="newUser.password" type="password" placeholder="Password" class="border p-2 rounded w-full" />
        <input v-model="newUser.full_name" placeholder="Work ID" class="border p-2 rounded w-full" />
        <select v-model="newUser.role" class="border p-2 rounded w-full">
          <option value="user">User</option>
          <option value="tool">Tool</option>
          <option value="leader">Leader</option>
          <option value="admin">Admin</option>
        </select>
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
          Create User
        </button>
      </form>
    </div>

    <!-- User List -->
    <div class="bg-white shadow-md rounded-lg p-4">
      <h2 class="text-xl font-semibold mb-3">All Users</h2>
      <table class="table-auto w-full border-collapse border">
        <thead>
          <tr class="bg-gray-100">
            <th class="border p-2">ID</th>
            <th class="border p-2">Username</th>
            <th class="border p-2">Role</th>
            <th class="border p-2">Work ID</th>
            <th class="border p-2">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="border p-2">{{ user.id }}</td>
            <td class="border p-2">{{ user.username }}</td>
            <td class="border p-2">{{ user.role }}</td>
            <td class="border p-2">{{ user.full_name }}</td>
            <td class="border p-2 text-center space-x-2 space-y-2">
              <button 
                @click="openEditModal(user)" 
                class="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600">
                Edit
              </button>

              <button 
                @click="deleteUser(user.id)" 
                class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditModal" 
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center">

      <div class="bg-white p-6 rounded-lg shadow-lg w-96">
        <h2 class="text-xl font-semibold mb-4">Edit User</h2>

        <div class="space-y-3">
         <input 
            v-model="selectedUser.username" 
            class="border p-2 rounded w-full" disabled
            placeholder="Username" />

          <input 
            v-model="selectedUser.full_name" 
            class="border p-2 rounded w-full" 
            placeholder="Work ID" />

          <select 
            v-model="selectedUser.role" 
            class="border p-2 rounded w-full">
            <option value="user">User</option>
            <option value="tool">Tool</option>
            <option value="leader">Leader</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="flex justify-end space-x-2 mt-4">
          <button 
            @click="showEditModal = false" 
            class="px-4 py-2 bg-gray-300 rounded">
            Cancel
          </button>

          <button 
            @click="saveUserUpdate" 
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/axios";

const users = ref([]);
const newUser = ref({
  username: "",
  password: "",
  role: "user",
  full_name: ""
});

// Fetch all users
const fetchUsers = async () => {
  try {
    const res = await api.get("/admin/users");
    users.value = res.data;
  } catch (err) {
    console.error("Error fetching users:", err);
  }
};

// Create new user
const createUser = async () => {
  try {
    await api.post("/admin/users", newUser.value);
    alert("User created!");
    newUser.value = { username: "", password: "", role: "user", full_name: "" };
    fetchUsers();
  } catch (err) {
    console.error("Error creating user:", err);
    alert("Failed to create user");
  }
};

// Update user role
const updateUserRole = async (user) => {
  if (window.confirm("Update Role?")) {
    try {
      await api.put(`/admin/users/${user.id}`, { role: user.role });
      alert("User role updated!");
    } catch (err) {
      console.error("Error updating role:", err);
      user.role = oldRole // rollback on API error too
    }
  } else {
    fetchUsers();
  }
 
};

// Delete user
const deleteUser = async (id) => {
  if (window.confirm("Are you sure?")){
    try {
    await api.delete(`/admin/users/${id}`);
    alert("User deleted!");
    fetchUsers();
  } catch (err) {
    console.error("Error deleting user:", err);
  }}

};

const showEditModal = ref(false);
const selectedUser = ref(null);

const openEditModal = (user) => {
  selectedUser.value = { ...user }; // clone object
  showEditModal.value = true;
};

const saveUserUpdate = async () => {
  try {
    await api.put(`/admin/users/${selectedUser.value.id}`, {
      role: selectedUser.value.role,
      full_name: selectedUser.value.full_name
    });

    alert("User updated!");
    showEditModal.value = false;
    fetchUsers();

  } catch (err) {
    console.error("Update failed:", err);
    alert("Failed to update user");
  }
};

onMounted(fetchUsers);
</script>
