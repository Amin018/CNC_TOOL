<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-lg sm:text-2xl font-bold">Tools Request</h1>

      <!-- Only user/leader can create -->
      <button
        v-if="user.role === 'user' || user.role === 'leader'"
        @click="router.push('/tools/new')"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm sm:text-base"
      >
        + New Tool
      </button>
    </div>


    <!-- Status Filter --> 
    <div class="grid grid-cols-2 gap-4 mb-4 max-w-md text-sm sm:text-base">
        <div class="flex items-center">
        <label class="w-32 font-medium">Filter by Status:</label>
        <select
          v-model="statusFilter"
          class="flex-1 border border-gray-300 rounded p-2"
        >
          <option value="">All</option>
          <option value="Pending">Pending</option>
          <option value="In_Progress">In Progress</option>
          <option value="Completed">Completed</option>
        </select>
      </div>

      <!-- Date Filter -->
      <div class="flex items-center">
        <label class="w-32 font-medium">Filter by Date:</label>
        <select
          v-model="dateFilter"
          class="flex-1 border border-gray-300 rounded p-2"
        >
          <option value="all">All</option>
          <option value="daily">Today</option>
          <option value="weekly">This Week</option>
          <option value="monthly">This Month</option>
        </select>
      </div>
    </div>

      <!-- Export (Admin only) -->
      <div v-if="user.role === 'admin'" class="mb-4 flex gap-2 items-center text-sm sm:text-base">
        <label class="font-medium">Export:</label>
        <select v-model="exportPeriod" class="border border-gray-300 rounded p-2">
          <option value="all">All</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>

        <button
          @click="exportTools"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Download CSV
        </button>
      </div>
    
    <!-- Table -->
    <div class="overflow-x-auto w-full">
      <table class="table-fixed border border-gray-200 w-full text-sm sm:text-base">
        <thead>
          <tr class="bg-gray-100 break-normal whitespace-normal ">
            <th class="px-4 py-2 border">ID</th>
            <th class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">Machine</th>
            <th class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">Part No</th>
            <th class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">Status</th>
            <th class="hidden lg:table-cell px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">Requested At</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="tool in filteredTools"
            :key="tool.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="goToDetail(tool.id)"
          >
            <td class="px-4 py-2 border">{{ tool.id }}</td>
            <td class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">{{ tool.machine_no }}</td>
            <td class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">{{ tool.part_no }}</td>
            <td class="px-4 py-2 border truncate max-w-[200px] overflow-hidden whitespace-nowrap">{{ tool.status }}</td>
            <td class="hidden lg:table-cell px-4 py-2 border">{{ formatDate(tool.time_requested) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";

const router = useRouter();
const tools = ref([]);
const statusFilter = ref("");
const user = ref({ username: "", role: "" })
const exportPeriod = ref("all");
const dateFilter = ref("all")

async function fetchUser() {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
    //console.log("STEP1 -> Fetched user:", user.value)
  } catch (err) {
    console.error("Error fetching user:", err)
  }
}

// Fetch data
const fetchTools = async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    console.warn("No token found, cannot fetch tools.");
    return;
  }
  try {
    const res = await api.get("/tools/");
    //console.log("Fetched tool:", res.data);
    tools.value = res.data.reverse(); 
  } catch (err) {
    console.error("Error fetching tools:", err);
  }
};

// Filtered list
const filteredTools = computed(() => {
  return tools.value.filter((c) => {
    // Status filter
    if (statusFilter.value && c.status !== statusFilter.value) {
      return false
    }

    // Date filter
    if (dateFilter.value !== "all" && c.time_requested) {
      const date = new Date(c.time_requested)
      const now = new Date()

      if (dateFilter.value === "daily") {
        return date.toDateString() === now.toDateString()
      }
      if (dateFilter.value === "weekly") {
        const weekAgo = new Date()
        weekAgo.setDate(now.getDate() - 7)
        return date >= weekAgo
      }
      if (dateFilter.value === "monthly") {
        return (
          date.getFullYear() === now.getFullYear() &&
          date.getMonth() === now.getMonth()
        )
      }
    }

    return true
  })
})


// Navigate to detail
const goToDetail = (id) => {
  router.push(`/tools/${id}`);
};

// Format dates
const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleString();
};

async function exportTools() {
  try {
    const response = await api.get(
      `admin/export/tools?period=${exportPeriod.value}`,
      { responseType: "blob" } // must be blob for files
    )

    // Create a temporary link and trigger download
    const blob = new Blob([response.data], { type: "text/csv" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `tools_${exportPeriod.value}.csv`
    link.click()
    URL.revokeObjectURL(link.href) // cleanup
  } catch (err) {
    console.error("Export failed:", err)
    alert("Failed to export tools")
  }
}

// Load on mount
let intervalId;

onMounted(async () => {
  try{
    await fetchUser();
    await fetchTools();
    intervalId = setInterval(() => {
      fetchTools();
    }, 10000);} 
  catch(err){
    console.error("Error during onMounted:", err)
  }
});

onUnmounted(() => {
  clearInterval(intervalId);
});
</script>

<style scoped>
table th,
table td {
  text-align: left;
}
</style>
