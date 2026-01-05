<template>
  <div class="p-6 max-w-4xl mx-auto ">
    <h1 class="text-lg sm:text-2xl font-bold mb-4">
      Part Details: {{ part.part_no }}
    </h1>

    <!-- PART INFO CARD -->
    <div class="bg-white shadow rounded p-6 mb-6 w-full">
      <h2 class="text-lg sm:text-2xl font-semibold mb-4">Part Information</h2>

      <div class="grid grid-cols-2 gap-4 text-sm sm:text-base">
        <div>
          <label class="font-medium">Part No</label>
          <input class="w-full p-2 border rounded bg-gray-100" disabled
                 :value="part.part_no" />
        </div>

        <div>
          <label class="font-medium">Package</label>
          <input class="w-full p-2 border rounded"
                 v-model="part.package" />
        </div>

        <div class="col-span-2">
          <label class="font-medium">Description</label>
          <textarea class="w-full p-2 border rounded"
                    v-model="part.description"></textarea>
        </div>
      </div>

      <div class="flex justify-between mt-auto text-sm sm:text-base" v-if="user.role === 'admin'">
        <button class="bg-blue-500 text-white px-6 py-2 hover:bg-blue-600 rounded" @click="savePart">Save</button>
        <button class="bg-red-500 text-white px-6 py-2 hover:bg-red-600 rounded" @click="deletePart">Delete</button>
      </div>

    </div>

    <!-- LINKED PARTS -->
    <div class="bg-white shadow rounded p-6 text-sm sm:text-base">
      <h2 class="text-lg font-semibold mb-4">Linked Parts</h2>
      <div v-if="user.role === 'admin'" class="space-y-3">
        <input
          v-model="linkSearch"
          @input="fetchParts(linkSearch)"
          type="text"
          placeholder="Type part number..."
          class="border p-2 w-full rounded"
        />

        <ul
          v-if="suggestions.length"
          class="border rounded bg-white max-h-40 overflow-y-auto shadow"
        >
          <li
            v-for="part in suggestions"
            :key="part.id"
            @click="selectPart(part)"
            class="p-2 hover:bg-gray-200 cursor-pointer"
          >
            {{ part.part_no }} ; {{ part.description }}
          </li>
        </ul>

          <button
            @click="addLink"
            class="bg-green-500 text-white px-4 py-2 mb-4 rounded hover:bg-green-600 w-full sm:w-auto"
          >
            Add Link
          </button>
      </div>

      <!-- List -->
      <table class="table-fixed w-full mt-4 border text-sm sm:text-base">
        <thead>
          <tr class="bg-gray-100 break-normal whitespace-normal">
            <th class="border px-4 py-2">Part No</th>
            <th class="border px-4 py-2">Description</th>
            <th v-if="user.role === 'admin'" class="border px-4 py-2" >Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="p in linkedParts" :key="p.id" class="break-normal whitespace-normal">
            <td class="border px-4 py-2 break-all whitespace-normal">{{ p.part_no }}</td>
            <td class="border px-4 py-2 break-all whitespace-normal">{{ p.description }}</td>
            <td v-if="user.role === 'admin'" class="border px-4 py-2 text-center">
              <button @click="removeLink(p.id)"
                      class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                       >
                Remove
              </button>
            </td>
          </tr>

          <tr v-if="linkedParts.length === 0 && user.role === 'admin'">
            <td colspan="3" class="text-center py-4 text-gray-500">
              No linked parts
            </td>
          </tr>
          <tr v-if="linkedParts.length === 0 && user.role !== 'admin'">
            <td colspan="2" class="text-center py-4 text-gray-500">
              No linked parts
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/axios";

const route = useRoute();
const router = useRouter();
const partId = route.params.id;
const linkId = ref(null)
const user = ref({ username: "", role: "" });

const part = ref({});
const linkedParts = ref([]);


async function fetchRole() {
  const res = await api.get("/auth/me");
  user.value = res.data;
}

// Load part
async function fetchPart() {
  const res = await api.get(`/parts/${partId}`);
  part.value = res.data;
}

// Load linked parts
async function fetchLinks() {
  const res = await api.get(`/partlinks/${partId}`);
  linkedParts.value = res.data;
}

// Save edits
async function savePart() {
  try {
    await api.put(`/parts/${partId}`, {
      description: part.value.description,
      package: part.value.package
    });
    alert("Part updated!");
  } catch (err) {
    alert("Failed to update");
  }
}

// Delete part
async function deletePart() {
  if(window.confirm("Are you sure you want to delete this part?")){
    try {
      await api.delete(`/parts/${partId}`);
      fetchParts();
      router.push("/admin/parts")
    } catch (err) {
      alert("Error deleting part");
      console.error(err);
    }}
    
}

// Autocomplete for next part
const linkSearch = ref("")
const suggestions = ref([])

async function fetchParts(query) {
  if (query.length < 2) {
    suggestions.value = []
    return
  }
  try {
    const res = await api.get(`/parts/search?query=${query}`)
    suggestions.value = res.data
  } catch (err) {
    console.error("Error fetching parts:", err)
  }
}

function selectPart(part) {
  linkSearch.value = part.part_no       // visible text
  linkId.value = part.id                // real id for backend
  suggestions.value = []
}

// Add link
async function addLink() {
  if (!linkSearch.value) {
    alert("Enter part number");
    return;
  }

  if (partId == linkId.value) {
    alert("Cannot link same part no");
    return;
  }

  try {
    await api.post(`/partlinks/${partId}/${linkId.value}`)
    linkSearch.value = "";
    fetchLinks();
  } catch (err) {
    alert("Failed to link");
  }
}

// Remove link
async function removeLink(linkedId) {
  if (!confirm("Remove link?")) return;

  await api.delete(`/partlinks/${partId}/${linkedId}`);
  fetchLinks();
}

onMounted(() => {
  fetchRole();
  fetchPart();
  fetchLinks();
});
</script>
