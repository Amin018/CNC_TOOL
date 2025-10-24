<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Parts</h1>

    <!-- Add Part Form -->
    <form v-if="user.role === 'admin'" @submit.prevent="addPart" class="flex gap-4 mb-6">
      <input v-model="newPart.part_no" placeholder="Part No" class="border p-2 rounded w-1/3" />
      <input v-model="newPart.description" placeholder="Description" class="border p-2 rounded w-1/2" />
      <input v-model="newPart.package" placeholder="Package" class="border p-2 rounded w-1/4" />
      <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Add</button>
    </form>

    <!-- Search Filter -->
    <input
      v-model="searchPart"
      placeholder="Search Part No..."
      class="border p-2 rounded w-1/4 mb-4"
    />

    <!-- Search by Package -->
    <input
      v-model="searchPackage"
      placeholder="Search Package..."
      class="border p-2 rounded w-1/4 mb-4 ml-4"
    />

    <!-- Parts Table -->
    <table class="min-w-full border border-gray-200">
      <thead>
        <tr class="bg-gray-100">
          <!--<th class="px-4 py-2 border">ID</th>-->
          <th class="px-4 py-2 border">Part No</th>
          <th class="px-4 py-2 border">Description</th>
          <th class="px-4 py-2 border">Package</th>
          <th v-if="user.role == 'admin'" class="px-4 py-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="part in filteredParts" :key="part.id" class="hover:bg-gray-50">
          <!-- <td class="px-4 py-2 border">{{ part.id }}</td> -->
          <td class="px-4 py-2 border">{{ part.part_no }}</td>
          <td class="px-4 py-2 border">{{ part.description }}</td>
          <td class="px-4 py-2 border">{{ part.package }}</td>
          <td v-if="user.role == 'admin'" class="px-4 py-2 border text-center">
            <button  @click="deletePart(part.id)" class="bg-red-500 text-white px-2 py-1 rounded ">
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../api/axios";

const parts = ref([]);
const newPart = ref({ part_no: "", description: "", package: "" });
const searchPart = ref(""); // Add search input
const searchPackage = ref("");
const user = ref({ username: "", role: "" });

async function fetchRole() {
  const res = await api.get("/auth/me");
  user.value = res.data;
}

// Fetch parts
async function fetchParts() {
  const res = await api.get("/parts/");
  parts.value = res.data;
}

// Add part
async function addPart() {
  try {
    await api.post("/parts/", newPart.value);
    newPart.value = { part_no: "", description: "" };
    fetchParts();
  } catch (err) {
    alert("Error adding part");
    console.error(err);
  }
}

// Delete part
async function deletePart(id) {
  if(window.confirm("Are you sure you want to delete this part?")){
    try {
      await api.delete(`/parts/${id}`);
      fetchParts();
    } catch (err) {
      alert("Error deleting part");
      console.error(err);
    }}
    
}

// FILTERED LIST (live search)
//const filteredParts = computed(() => {
// return parts.value.filter(part =>
//    part.part_no.toLowerCase().includes(searchQuery.value.toLowerCase())
//  );
//});

const filteredParts = computed(() => {
  return parts.value.filter(part => {
    const matchPart =
      !searchPart.value ||
      (part.part_no || "").toLowerCase().includes(searchPart.value.toLowerCase());

    const matchPackage =
      !searchPackage.value ||
      (part.package || "").toLowerCase().includes(searchPackage.value.toLowerCase());

    return matchPart && matchPackage; // both conditions must be true
  });
});

onMounted(() => {
  fetchRole();
  fetchParts();
  });
</script>
