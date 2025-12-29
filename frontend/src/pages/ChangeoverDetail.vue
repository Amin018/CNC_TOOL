<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <div class="bg-white p-6 rounded-xl shadow max-w-3xl mx-auto">
      <h1 class="text-2xl font-bold mb-4">Changeover Details</h1>

      <div v-if="isLoading" class="text-center text-gray-500">Loading...</div>
      <div v-else>
        <!-- Changeover Info -->
        <div class="space-y-3 mb-6">
          <div class="flex justify-between pb-1">
            <span><strong>ID:</strong> {{ changeover.id }}</span>
            <span><strong>Status:</strong> {{ changeover.status }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Production Line:</strong> {{ changeover.production_line }}</span>
            <span><strong>Machine:</strong> {{ changeover.machine_no }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Current Part:</strong> {{ changeover.current_part_no }}</span>
            <span><strong>Next Part:</strong> {{ changeover.next_part_no }}</span>
          </div>

          <div class="flex justify-between border-b pb-4">
            <span><strong>Changeover Time:</strong> {{ formatDate(changeover.time_for_changeover) }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Requested By:</strong> {{ changeover.requested_by }}</span>
            <span><strong>Time Requested:</strong> {{ formatDate(changeover.time_requested) }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Concurred By:</strong> {{ changeover.concurred_by || "-" }}</span>
            <span><strong>Time Concurred:</strong> {{ formatDate(changeover.time_concurred) || "-" }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Acknowledged By:</strong> {{ changeover.acknowledged_by || "-" }}</span>
            <span><strong>Time Acknowledged:</strong> {{ formatDate(changeover.time_acknowledged) || "-" }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Returned By:</strong> {{ changeover.tool_return_by || "-" }}</span>
            <span><strong>Time Returned:</strong> {{ formatDate(changeover.time_return) || "-" }}</span>
          </div>
          
          <div class="flex justify-between pb-1">
            <span><strong>Received By:</strong> {{ changeover.confirm_and_received_by || "-" }}</span>
            <span><strong>Time Received:</strong> {{ formatDate(changeover.time_received) || "-" }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Tool Setup:</strong> {{ changeover.new_tool_by || "-" }}</span>
            <span><strong>Time Tool Setup:</strong> {{ formatDate(changeover.time_prepared) || "-" }}</span>
          </div>

          <div class="flex justify-between pb-1">
            <span><strong>Completed By:</strong> {{ changeover.completed_and_received_by || "-" }}</span>
            <span><strong>Time Completed:</strong> {{ formatDate(changeover.time_completed) || "-" }}</span>
          </div>

          <div class="flex justify-between ">
            <span><strong>Remarks:</strong> {{ changeover.remark || "-" }}</span>
            <span><strong>Tool Return Remarks:</strong> {{ changeover.remark_return || "-" }}</span>
          </div>
        </div>


        <!-- Tool Return -->
        <div v-if="(user.role === 'user' || user.role === 'leader') && changeover.status === 'In_Progress' && !changeover.tool_return_by" class="mt-6 border-t pt-6">
          <h2 class="text-xl font-bold mb-4">Tool Return</h2>

          <form @submit.prevent="submitToolReturn" class="space-y-4">
            <!-- Checklist -->
            <div class="space-y-2 mb-4">
              <label class="flex items-center">
                <input type="checkbox" v-model="checklist.workInstruction" class="mr-2" />
                Work Instruction Returned
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="checklist.cuttingTool" class="mr-2" />
                Cutting Tool Returned
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="checklist.fixtureJig" class="mr-2" />
                Fixture/Jig Returned
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="checklist.ncProgram" class="mr-2" />
                NC Program Returned
              </label>
            </div>

            <!-- Remarks -->
            <textarea
              v-model="return_remark"
              placeholder="Enter remarks about tool return..."
              class="w-full border p-2 rounded"
            ></textarea>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="!allChecked"
              class="px-4 py-2 rounded text-white"
              :class="allChecked ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-400 cursor-not-allowed'"
            >
              Submit Tool Return
            </button>
          </form>
        </div>

        <!-- New Tool Setup -->
        <div v-if="(user.role === 'tool' || user.role === 'admin') && changeover.status === 'Returned' && changeover.concurred_by && changeover.new_tool_by === null" class="mt-6 border-t pt-6">
          <h2 class="text-xl font-bold mb-4">Tool Return</h2>

          <form @submit.prevent="submitToolPrepare" class="space-y-4">
            <!-- Checklist -->
            <div class="space-y-2 mb-4">
              <label class="flex items-center">
                <input type="checkbox" v-model="tool_checklist.workInstruction" class="mr-2" />
                Prepare Work Instruction
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="tool_checklist.cuttingTool" class="mr-2" />
                Prepare Cutting Tool
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="tool_checklist.fixtureJig" class="mr-2" />
                Prepare Fixture/Jig
              </label>
              <label class="flex items-center">
                <input type="checkbox" v-model="tool_checklist.ncProgram" class="mr-2" />
                Prepare NC Program
              </label>
            </div>

            <!-- Remarks -->
            <textarea
              v-model="remark"
              placeholder="Enter remarks about new tool setup..."
              class="w-full border p-2 rounded"
            ></textarea>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="!allCheckedforTool"
              class="px-4 py-2 rounded text-white"
              :class="allCheckedforTool ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-400 cursor-not-allowed'"
            >
              Submit Tool Setup
            </button>
          </form>
        </div>


        <!-- Actions -->
        <div class="flex flex-wrap gap-4 mt-6 border-t pt-6">
          <button
            v-if="(user.role === 'leader' || user.role === 'admin') && changeover.concurred_by === null"
            @click="concurChangeover"
            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Concur
          </button>

          <button
            v-if="(user.role === 'tool' || user.role === 'admin') && changeover.status === 'Pending'"
            @click="acknowledgeChangeover"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Acknowledge
          </button>

          <button
            v-if="(user.role === 'tool' || user.role === 'admin') && changeover.tool_return_by && !changeover.confirm_and_received_by"
            @click="receiveTool"
            class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
          >
            Receive Tool
          </button>


          <button
            v-if="(user.role === 'user' || user.role === 'leader') && changeover.new_tool_by && changeover.status !== 'Completed' && changeover.completed_and_received_by === null"
            @click="completeRequest"
            class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
          >
            Complete Request
          </button>

          <button
            v-if="(user.role === 'admin')"
            @click="deleteRequest"
            class="bg-red-500 text-white self-end px-4 py-2 rounded hover:bg-red-600 ml-auto"
          >
            DELETE
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

const changeover = ref({})
const user = ref({ username: "", role: "" })
const isLoading = ref(true)

// Checklist state
const checklist = ref({
  workInstruction: false,
  cuttingTool: false,
  fixtureJig: false,
  ncProgram: false
})
const return_remark = ref("")

// Checklist state
const tool_checklist = ref({
  workInstruction: false,
  cuttingTool: false,
  fixtureJig: false,
  ncProgram: false
})
const remark = ref("")

// Enable submit only if all checked
const allChecked = computed(() => {
  return Object.values(checklist.value).every(Boolean)
})

// Enable submit only if all checked
const allCheckedforTool = computed(() => {
  return Object.values(tool_checklist.value).every(Boolean)
})

const formatDate = (dateStr) => {
  if (!dateStr) return "-"
  return new Date(dateStr).toLocaleString("en-MY")
}

async function fetchChangeover() {
  try {
    const res = await api.get(`/changeovers/${route.params.id}`)
    changeover.value = res.data
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

async function concurChangeover() {
  if (
      changeover.value.current_part_no.includes(",") ||
      changeover.value.next_part_no.includes(",")
    ) {
      const ok = window.confirm("Are you sure to concur more than 1 part?");
      if (!ok) return;   // stop function if user presses cancel
    }

  await api.put(`/changeovers/${route.params.id}/concur`)
  await fetchChangeover()

}

async function acknowledgeChangeover() {
  await api.put(`/changeovers/${route.params.id}/acknowledge`)
  await fetchChangeover()
}

async function submitToolReturn() {
  try {
    await api.put(`/changeovers/${route.params.id}/toolreturn`, {
      remark_return: return_remark.value
    })
    alert("Tool return submitted!")
    remark.value = ""
    checklist.value = {
      workInstruction: false,
      cuttingTool: false,
      fixtureJig: false,
      ncProgram: false
    }
    await fetchChangeover()
  } catch (err) {
    console.error(err)
    alert("Failed to submit tool return")
  }
}

async function submitToolPrepare() {
  try {
    await api.put(`/changeovers/${route.params.id}/toolprepare`, {
      remark: remark.value
    })
    alert("New Tool setup submitted!")
    remark.value = ""  // reset text
    tool_checklist.value = {   // reset checklist
      workInstruction: false,
      cuttingTool: false,
      fixtureJig: false,
      ncProgram: false
    }
    await fetchChangeover()
  } catch (err) {
    console.error(err)
    alert("Failed to submit tool setup")
  }
}

async function receiveTool() {
  await api.put(`/changeovers/${route.params.id}/toolreceived`)
  await fetchChangeover()
}

async function completeRequest() {
  await api.put(`/changeovers/${route.params.id}/toolcomplete`)
  await fetchChangeover()
}

async function deleteRequest() {
  if (window.confirm("Are you sure?")){
    try {
    await api.delete(`/changeovers/${route.params.id}`)
    alert("Changeover deleted!")
    //await fetchChangeover()
    router.push("/changeovers")
  } catch (err) {
    console.error("Error deleting changeover:", err);
  }};
  
}

let intervalId;

onMounted(() => {
  fetchUser();
  fetchChangeover();
  // Poll every 5 seconds
  intervalId = setInterval(() => {
    fetchChangeover();
  }, 3000);
});

onUnmounted(() => {
  // Clean up when leaving page
  clearInterval(intervalId);
});

</script>
