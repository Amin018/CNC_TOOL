<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="bg-white p-6 rounded-xl shadow max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Request New Tool</h1>

      <form @submit.prevent="submitToolRequest" class="space-y-4">
        <!-- Machine Number -->
        <div>
          <label class="block font-semibold mb-1">Machine No</label>
          <input
            v-model="form.machine_no"
            type="text"
            class="w-full border p-2 rounded"
            required
          />
        </div>

        <!-- Part Number with autocomplete -->
        <div>
          <label class="block font-semibold mb-1">Part No</label>
          <input
            v-model="partInput"
            @input="fetchParts(partInput)"
            type="text"
            placeholder="Type part number..."
            class="w-full border p-2 rounded"
            required
          />

          <!-- Suggestions -->
          <ul
            v-if="suggestions.length"
            class="border rounded bg-white mt-1 max-h-40 overflow-y-auto"
          >
            <li
              v-for="part in suggestions"
              :key="part.id"
              @click="selectPart(part.part_no)"
              class="p-2 hover:bg-gray-200 cursor-pointer"
            >
              {{ part.part_no }} ; {{ part.description }}
            </li>
          </ul>
        </div>

        <!-- Tool Name -->
        <div>
          <label class="block font-semibold mb-1">Tool Name</label>
          <input
            v-model="form.tool_name"
            type="text"
            class="w-full border p-2 rounded"
            required
          />
        </div>

        <!-- Quantity -->
        <div>
          <label class="block font-semibold mb-1">Quantity</label>
          <input
            v-model.number="form.quantity"
            type="number"
            min="1"
            class="w-full border p-2 rounded"
            required
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Submit Tool Request
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import api from "../api/axios"

const router = useRouter()

// Form state
const form = ref({
  machine_no: "",
  part_no: "",
  tool_name: "",
  quantity: 1,
})

// Autocomplete state
const partInput = ref("")
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

function selectPart(partNo) {
  form.value.part_no = partNo
  partInput.value = partNo
  suggestions.value = []
}

async function submitToolRequest() {
  try {
    await api.post("/tools/", form.value)
    alert("Tool request created successfully!")
    router.push("/tools") // redirect back to list
  } catch (err) {
    console.error("Error creating tool request:", err)
    alert("Failed to create tool request")
  }
}
</script>
