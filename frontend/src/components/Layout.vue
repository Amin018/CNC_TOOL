<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-gray-900 text-white p-4 z-40 transform transition-transform duration-300',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'fixed inset-y-0 left-0 w-64 md:translate-x-0 h-screen overflow-y-auto',
        'z-50 md:z-40'
      ]"
    >
      <img
        src="@/assets/logo.png"
        alt="Company Logo"
        class="hidden md:block mx-auto bg-auto mb-3 "
      />
      <h1 class="text-lg font-bold hidden md:block">CNC System</h1>
      <nav class="mt-6 space-y-2">
        <router-link
          v-for="item in navItems.filter(i => i.roles.includes(user.role))"
          :key="item.path"
          :to="item.path"
          class="block py-2 px-3 rounded hover:bg-gray-700 text-sm md:text-base"
          @click="sidebarOpen = false"
        >
          {{ item.name }}
        </router-link>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col md:ml-64">
      <!-- Top bar -->
      <header class="sticky top-0 z-40 flex items-center justify-between bg-white shadow px-4 sm:px-6 py-3">
        <!-- Hamburger (mobile only) -->
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="md:hidden text-gray-600 focus:outline-none"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <h1 class="text-sm sm:text-lg font-bold text-gray-700">SMEA-MachineShop</h1>

        <div class="flex items-center gap-2 sm:gap-4">
          <span class="text-xs sm:text-sm text-gray-600">{{ user.username }} ({{ user.role }})</span>
          <button
            @click="logout"
            class="bg-red-500 text-white px-2 py-1 sm:px-3 sm:py-1 rounded text-xs sm:text-sm hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </header>

      <!-- Routed page -->
      <main class="flex-1 bg-gray-100 p-2 sm:p-6 overflow-auto">
        <router-view />
      </main>
    </div>

    <!-- Overlay (mobile only) -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-white bg-opacity-50 z-30 md:hidden"
      @click="sidebarOpen = false"
    ></div>
  </div>
</template>


<script setup>
import { ref, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import api from "../api/axios"

const router = useRouter()
const route = useRoute()
const sidebarOpen = ref(false); // controls mobile sidebar

const user = ref({ username: "", role: "" })

// Navigation items
const navItems = [
  { name: "Dashboard", path: "/dashboard", roles: ["admin", "user", "tool", "leader"] },
  { name: "Changeovers", path: "/changeovers", roles: ["admin", "user", "tool", "leader"] },
  { name: "Parts", path: "/admin/parts", roles: ["admin", "user", "tool", "leader"] },
  { name: "Manage Users", path: "/admin/users", roles: ["admin"] },
  { name: "Tool Requests", path: "/tools", roles: ["admin", "user", "tool", "leader"] },
  { name: "Machines", path: "/machines", roles: ["admin", "user", "leader"] },
  
]

function goTo(path) {
  router.push(path)
}

function logout() {
  localStorage.removeItem("token")
  router.push("/login")
}

// Fetch logged-in user
async function fetchUser() {
  try {
    const res = await api.get("/auth/me")
    user.value = res.data
  } catch (err) {
    console.error(err)
    router.push("/login")
  }
}

// Watch route changes
onMounted(() => {
  fetchUser()
})
</script>

<style scoped>
/* Sidebar scroll fix */
aside {
  min-height: 100vh;
}
</style>
