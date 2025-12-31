<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <!-- Title -->
    <h1 class="text-xl sm:text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div v-for="(value, key) in statusCounts" :key="key" class="bg-white p-6 rounded-xl shadow" @click="goToChangeovers(key)" style="cursor: pointer;">
        <h2 class="text-lg font-semibold text-gray-600 capitalize">{{ key }}</h2>
        <p class="text-3xl font-bold text-gray-900">{{ value }}</p>
      </div>
    </div>

    <!-- Chart + Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chart -->
      <div class="bg-white p-6 rounded-xl shadow lg:col-span-2">
        <h2 class="text-xs md:text-base font-bold text-gray-800 mb-4">Weekly Trend</h2>
        <canvas id="changeoverChart"></canvas>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white p-6 rounded-xl shadow">
        <h2 class="text-xs md:text-base font-bold text-gray-800 mb-4">Recent Changeovers</h2>
        <ul class="divide-y divide-gray-200">
          <li
            v-for="item in recentChangeovers"
            :key="item.id"
            class="py-2"
          >
            <p class="text-gray-800 font-medium">
              {{ item.machine_no }} ({{ item.status }})
            </p>
            <p class="text-sm text-gray-500">
              Requested by {{ item.requested_by }} at {{ formatDate(item.time_requested) }}
            </p>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api/axios";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const router = useRouter();
const isMounted = ref(false);
let intervalId = null;

const statusCounts = ref({
  Pending: 0,
  In_Progress: 0,
  Returned: 0,
  Completed: 0
});

const recentChangeovers = ref([]);
const chartInstance = ref(null)

const formatDate = (dateStr) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleString();
};

async function fetchDashboardData() {
  try {
    const res = await api.get("/changeovers/");
    const data = res.data;

    // Count statuses
    statusCounts.value = {
      Pending: data.filter((c) => c.status === "Pending").length,
      In_Progress: data.filter((c) => c.status === "In_Progress").length,
      Returned: data.filter((c) => c.status === "Returned").length,
      Completed: data.filter((c) => c.status === "Completed").length
    };

    // Recent 5 changeovers
    recentChangeovers.value = data.slice(-5).reverse();

    // Chart Data (weekly trend: counts grouped by day)
    const grouped = {};
    data.forEach((c) => {
      const date = new Date(c.time_requested).toLocaleDateString();
      grouped[date] = (grouped[date] || 0) + 1;
    });

    const labels = Object.keys(grouped);
    const values = Object.values(grouped);

    
    const canvas = document.getElementById("changeoverChart");
    if (!canvas) return;

    if (chartInstance.value) {
      chartInstance.value.destroy();
    }

    chartInstance.value = new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Changeovers",
            data: values,
            borderColor: "rgb(59, 130, 246)", // Tailwind blue-500
            backgroundColor: "rgba(59, 130, 246, 0.8)",
            tension: 0.3,
            fill: true
          }
        ]
      },
      options: {
        indexAxis: 'x', 
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  } catch (err) {
    console.error("Error fetching dashboard:", err);
  }
}

async function goToChangeovers(status) {
  router.push({
    path: "/changeovers",
    query: { status }
  })
}



onMounted(() => {
  isMounted.value = true;
  fetchDashboardData();
  intervalId = setInterval(() => {
      fetchDashboardData();
      console.log("Dashboard data refreshed")
  }, 60000); // Refresh every 60 seconds
});

onUnmounted(() => {
  isMounted.value = false;
  if (intervalId){
    clearInterval(intervalId);
  }
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
});
</script>
