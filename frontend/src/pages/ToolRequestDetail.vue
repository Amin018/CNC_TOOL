<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="bg-white p-6 rounded-xl shadow max-w-3xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Tool Request Details</h1>

      <div v-if="isLoading" class="text-center text-gray-500">Loading...</div>
      <div v-else>
        <!-- Tool Request Info -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div><strong>ID:</strong> {{ tool.id }}</div>
          <div><strong>Status:</strong> {{ tool.status }}</div>
          <div><strong>Machine:</strong> {{ tool.machine_no }}</div>
          <div><strong>Part No:</strong> {{ tool.part_no }}</div>
          <div><strong>Tool Name:</strong> {{ tool.tool_name }}</div>
          <div><strong>Quantity:</strong> {{ tool.quantity }}</div>
          <div><strong>Requested By:</strong> {{ tool.requested_by }}</div>
          <div><strong>Time Requested:</strong> {{ formatDate(tool.time_requested) }}</div>
          <div><strong>Concurred By:</strong> {{ tool.concurred_by || "None" }}</div>
          <div><strong>Time Concurred:</strong> {{ formatDate(tool.time_concurred) || "None" }}</div>
          <div><strong>Prepared By:</strong> {{ tool.prepared_by || "None" }}</div>
          <div><strong>Time Prepared:</strong> {{ formatDate(tool.time_prepared) || "None" }}</div>
          <div><strong>Received By:</strong> {{ tool.received_and_completed_by || "None" }}</div>
          <div><strong>Time Completed:</strong> {{ formatDate(tool.time_completed) || "None" }}</div>
          <div><strong>Remark:</strong> {{ tool.remark || "None" }}</div>
        </div>

        <!-- Tool Replace (Tool role) -->
        <div
          v-if="user.role === 'tool' && tool.status === 'In_Progress' && !tool.prepared_by"
          class="mt-6 border-t pt-6"
        >
          <h2 class="text-xl font-bold mb-4">Prepare/Replace Tool</h2>
          <form @submit.prevent="submitToolReplace" class="space-y-4">

            <label class="flex items-center">
              <input type="checkbox" v-model="tool_checklist.UnusableTool" class="mr-2" />
              Receive Unusable Cutting Tool
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="tool_checklist.NewTool" class="mr-2" />
              Replace Cutting Tool
            </label>

            <textarea
              v-model="remark"
              placeholder="Enter remarks about preparation..."
              class="w-full border p-2 rounded"
            ></textarea>
            <button
              type="submit"
              :disabled="!allCheckedforTool"
              class="px-4 py-2 rounded text-white"
              :class="allCheckedforTool ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-400 cursor-not-allowed'"
            >
              Submit Preparation
            </button>
          </form>
        </div>

        <!-- Actions -->
        <div class="flex flex-wrap gap-4 mt-6 border-t pt-6">
          <button
            v-if="(user.role === 'leader' || user.role === 'admin') && tool.status === 'Pending' && !tool.concurred_by"
            @click="concurTool"
            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Concur
          </button>

          <button
            v-if="user.role === 'user' && tool.prepared_by && tool.status === 'In_Progress'"
            @click="completeTool"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Receive & Complete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import api from "../api/axios"

const route = useRoute()
const router = useRouter()

const tool = ref({})
const user = ref({ username: "", role: "" })
const isLoading = ref(true)
const remark = ref("")

const tool_checklist = ref({
  UnusableTool: false,
  NewTool: false
})

// Enable submit only if all checked
const allCheckedforTool = computed(() => {
  return Object.values(tool_checklist.value).every(Boolean)
})

const formatDate = (dateStr) => {
  if (!dateStr) return "-"
  return new Date(dateStr).toLocaleString()
}

async function fetchToolRequest() {
  try {
    const res = await api.get(`/tools/${route.params.id}`)
    tool.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

async function fetchUser() {
  try {
    const res = await api.get("/auth/me")
    user.value = res.data
  } catch (err) {
    console.error(err)
    router.push("/login")
  }
}

async function concurTool() {
  await api.put(`/tools/${route.params.id}/concur`)
  await fetchToolRequest()
}

async function submitToolReplace() {
  try {
    await api.put(`/tools/${route.params.id}/toolreplace`, {
      remark: remark.value
    })
    alert("Tool prepared successfully!")
    remark.value = ""
    await fetchToolRequest()
  } catch (err) {
    console.error(err)
    alert("Failed to prepare tool")
  }
}

async function completeTool() {
  await api.put(`/tools/${route.params.id}/toolcomplete`)
  await fetchToolRequest()
}

let intervalId
onMounted(() => {
  fetchUser()
  fetchToolRequest()
  intervalId = setInterval(fetchToolRequest, 3000)
})
onUnmounted(() => clearInterval(intervalId))
</script>
