import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  signup: ({ name, email, password }) =>
    api
      .post("/auth/signup", { name, email, password })
      .then((r) => r.data),
  login: ({ email, password }) =>
    api.post("/auth/login", { email, password }).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
  update: (payload) => api.put("/auth/update", payload).then((r) => r.data),
  delete: () => api.delete("/auth/delete").then((r) => r.data),
  logout: () => Promise.resolve(null),
};

export const searchApi = {
  search: (query) =>
    api.get("/search", { params: { q: query } }).then((r) => r.data),
  history: () => Promise.resolve([]),
  suggestions: () => Promise.resolve([]),
};

export const uploadApi = {
  upload: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api
      .post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
  ask: ({ paperId, question }) =>
    api
      .post("/upload/ask", { paper_id: paperId, question })
      .then((r) => r.data),
  pdfUrl: (paperId) => `${baseURL}/papers/${paperId}/pdf`,
};

export const dashboardApi = {
  metrics: () => api.get("/dashboard/metrics").then((r) => r.data),
};

export const papersApi = {
  list: (params = {}) => api.get("/papers", { params }).then((r) => r.data),
  get: (id) => api.get(`/papers/${id}`).then((r) => r.data),
  create: ({ file, title, authors, abstract, summary, tags }) => {
    const formData = new FormData();
    if (file) formData.append("file", file);
    if (title) formData.append("title", title);
    if (authors) formData.append("authors", authors);
    if (abstract) formData.append("abstract", abstract);
    if (summary) formData.append("summary", summary);
    if (tags) formData.append("tags", Array.isArray(tags) ? tags.join(",") : tags);
    return api
      .post("/papers", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => r.data);
  },
  update: (id, payload) => api.put(`/papers/${id}`, payload).then((r) => r.data),
  delete: (id) => api.delete(`/papers/${id}`).then((r) => r.data),
};

export const savedApi = {
  list: (params = {}) => api.get("/papers/saved", { params }).then((r) => r.data),
  save: (paper) => api.post("/papers/save", paper).then((r) => r.data),
  update: (id, payload) => api.put(`/papers/save/${id}`, payload).then((r) => r.data),
  unsave: (id) => api.delete(`/papers/save/${id}`).then((r) => r.data),
};
