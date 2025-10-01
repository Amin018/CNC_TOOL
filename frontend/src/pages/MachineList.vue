<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Machine Management</h1>

    <!-- Add Machine -->
     <div v-if="user.role === 'admin'" class="mb-4">
      <form v-if="user.role === 'admin'" @submit.prevent="addMachine" class="flex gap-2 mb-4">
      <input v-model="newMachine.production_line" placeholder="Production Line" class="border p-2 rounded w-1/3" required />
      <input v-model="newMachine.machine_no" placeholder="Machine No" class="border p-2 rounded w-1/3" required />
      <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">Add</button>
      </form>
    </div>

    <!-- List Machines -->
    <table class="table-auto border w-full">
      <thead>
        <tr class="bg-gray-100">
          <th class="px-4 py-2 border">ID</th>
          <th class="px-4 py-2 border">Production Line</th>
          <th class="px-4 py-2 border">Machine No</th>
          <th class="px-4 py-2 border">Status</th>
          <th v-if="user.role === 'admin'" class="px-4 py-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="machine in machines" :key="machine.id">
          <td class="px-4 py-2 border">{{ machine.id }}</td>
          <td class="px-4 py-2 border">{{ machine.production_line }}</td>
          <td class="px-4 py-2 border">{{ machine.machine_no }}</td>
          <td class="px-4 py-2 border">
            <span :class="machine.status === 'Active' ? 'text-green-600' : 'text-red-600'">
                {{ machine.status }}
            </span>
        </td>
        <td v-if="user.role === 'admin'" class="px-4 py-2 border flex gap-2">
        <button @click="toggleStatus(machine)" class="bg-yellow-500 text-white px-2 py-1 rounded">
            {{ machine.status === 'Active' ? 'Set Offline' : 'Set Active' }}
        </button>
        <button  @click="deleteMachine(machine.id)" class="bg-red-500 text-white px-2 py-1 rounded">Delete</button>
        </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "../api/axios"

const machines = ref([])
const newMachine = ref({ production_line: "", machine_no: "" })
const user = ref({ username: "", role: "" })

async function fetchUser() {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
    //console.log("STEP1 -> Fetched user:", user.value)
  } catch (err) {
    console.error("Error fetching user:", err)
  }
}

async function fetchMachines() {
  const res = await api.get("/machines")
  machines.value = res.data
}

async function addMachine() {
  await api.post("/machines/", newMachine.value)
  newMachine.value = { production_line: "", machine_no: "" }
  await fetchMachines()
}

async function deleteMachine(id) {
  if (!confirm("Delete this machine?")) return
  await api.delete(`/machines/${id}`)
  await fetchMachines()
}

async function toggleStatus(machine) {
  const newStatus = machine.status === "Active" ? "Offline" : "Active"
  await api.put(`/machines/${machine.id}/status`, null, { params: { status: newStatus } })
  await fetchMachines()
}

function filterMachines() {
  filteredMachines.value = machines.value.filter(
    m => m.production_line === selectedLine.value && m.status === "Active"
  )
}


onMounted(async () => {
  try{
    await fetchUser();
    await fetchMachines();
  } catch (error) {
    console.error("Error during onMounted:", error);
  }
})
</script>
