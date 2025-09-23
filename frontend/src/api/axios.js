import axios from "axios";

const api = axios.create({
  baseURL: "/api", // FastAPI backend
});

// Add token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    //console.log("Attaching token:", token); // debug
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
);

export default api;
