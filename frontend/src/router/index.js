import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../pages/LoginPage.vue";
import Layout from "../components/Layout.vue"
import Dashboard from "../pages/Dashboard.vue";
import AdminUsers from "../pages/AdminUsers.vue";
import ChangeoverList from "../pages/ChangeoverList.vue";
import CreateChangeover from "../pages/CreateChangeover.vue";
import PartsAdmin from "../pages/PartsAdmin.vue";
import ToolRequestList from "../pages/ToolRequestList.vue";
import CreateToolRequest from "../pages/CreateToolRequest.vue";
import ToolRequestDetail from "../pages/ToolRequestDetail.vue";
import PartDetail from "@/pages/PartDetail.vue";
import MachineList from "@/pages/MachineList.vue";


const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginPage },
  {
    path: "/",
    component: Layout,
    children: [
  { path: "/dashboard", component: Dashboard },
  { path: "/admin/Users", name: "AdminUsers", component: AdminUsers },
  { path: "/changeovers", component: ChangeoverList },
  { path: "/changeovers/new", component: CreateChangeover },
  { path: "/changeovers/:id", name: "ChangeoverDetail", component: () => import("../pages/ChangeoverDetail.vue")},
  { path: "/admin/parts", name: "PartsAdmin", component: PartsAdmin,},
  { path: "/parts/:id", name: "PartDetail", component: PartDetail },
  { path: "/tools", name: "ToolRequestList", component: ToolRequestList },
  { path: "/tools/new", name: "CreateToolRequest", component: CreateToolRequest },
  { path: "/tools/:id", name: "ToolRequestDetail", component: () => import("../pages/ToolRequestDetail.vue")},
  { path: "/machines", name: "MachineList", component: MachineList },

    ]
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

