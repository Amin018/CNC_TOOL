<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="bg-white p-6 rounded-xl shadow max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Create New Changeover</h1>

      <form @submit.prevent="submitChangeover" class="space-y-4">

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

        <!-- Current Part No with autocomplete -->
        <div>
          <label class="block font-medium">Current Part</label>
            <input
              v-model="currentPart"
              @input="fetchParts(currentPart)"
              type="text"
              placeholder="Type part number..."
              class="border p-2 w-full rounded"
            />

            <!-- Dropdown suggestions -->
            <ul v-if="suggestions.length" class="border rounded bg-white mt-1 max-h-40 overflow-y-auto">
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

        <!-- Next Part No with autocomplete -->
        <div>
          <label class="block font-medium">Next Part</label>
            <input
              v-model="nextPart"
              @input="fetchNewParts(nextPart)"
              type="text"
              placeholder="Type part number..."
              class="border p-2 w-full rounded"
            />

            <!-- Dropdown suggestions -->
            <ul v-if="nextsuggestions.length" class="border rounded bg-white mt-1 max-h-40 overflow-y-auto">
              <li
                v-for="part in nextsuggestions"
                :key="part.id"
                @click="selectNewPart(part.part_no)"
                class="p-2 hover:bg-gray-200 cursor-pointer"
              >
                {{ part.part_no }} ; {{ part.description }}
              </li>
            </ul>
        </div>

        <!-- Time for Changeover -->
        <div>
          <label class="block font-semibold mb-1">Time for Changeover</label>
          <input
            v-model="form.time_for_changeover"
            type="datetime-local"
            class="w-full border p-2 rounded"
            required
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Submit Request
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { ref, onMounted } from "vue"
import api from "../api/axios"

const router = useRouter()

// Form state
const form = ref({
  production_line: "",
  machine_no: "",
  current_part_no: "",
  next_part_no: "",
  time_for_changeover: ""
})

async function submitChangeover() {
  try {
    await api.post("/changeovers/", form.value)
    alert("Changeover request created successfully!")
    router.push("/changeovers") // redirect back to list
  } catch (err) {
    console.error("Error creating changeover:", err)
    alert("Failed to create changeover request")
  }
}

// Autocomplete for current part
const currentPart = ref("")
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
  currentPart.value = partNo
  suggestions.value = [] // hide dropdown after selection
}

// Autocomplete for next part
const nextPart = ref("")
const nextsuggestions = ref([])

async function fetchNewParts(query) {
  if (query.length < 2) {
    nextsuggestions.value = []
    return
  }
  try {
    const res = await api.get(`/parts/search?query=${query}`)
    nextsuggestions.value = res.data
  } catch (err) {
    console.error("Error fetching parts:", err)
  }
}

function selectNewPart(partNo) {
  nextPart.value = partNo
  nextsuggestions.value = [] // hide dropdown after selection
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
