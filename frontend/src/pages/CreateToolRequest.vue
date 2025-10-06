<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="bg-white p-6 rounded-xl shadow max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Request New Tool</h1>

      <form @submit.prevent="submitToolRequest" class="space-y-4">

        <!-- Production Line -->
        <div>
          <label class="block font-semibold mb-1">Production Line</label>
          <select v-model="selectedLine" @change="filterMachines" class="w-full border p-2 rounded" required>
            <option v-for="line in productionLines" :key="line" >{{ line }}</option>
          </select>
        </div>

        <!-- Machine Number -->
        <div>
          <label class="block font-semibold mb-1">Machine No</label>
          <select v-model="form.machine_no" class="w-full border p-2 rounded" required>
            <option v-for="m in filteredMachines" :key="m.id" >{{ m.machine_no }}</option>
          </select>
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
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import api from "../api/axios"

const router = useRouter()

// Form state
const form = ref({
  production_line: "",
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

    // Set part number from selected autocomplete
    form.value.part_no = partInput.value

    await api.post("/tools/", form.value)
    alert("Tool request created successfully!")
    router.push("/tools") // redirect back to list
  } catch (err) {
    console.error("Error creating tool request:", err)
    alert("Failed to create tool request")
  }
}

const machines = ref([])
const productionLines = ref([])
const filteredMachines = ref([])
const selectedLine = ref("")

async function fetchMachines() {
  const res = await api.get("/machines/")
  machines.value = res.data
  productionLines.value = [...new Set(machines.value.map(m => m.production_line))]
}

function filterMachines() {
  filteredMachines.value = machines.value.filter(m => m.production_line === selectedLine.value)
}

onMounted(fetchMachines)

</script>
