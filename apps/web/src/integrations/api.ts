import axios from 'axios';

// API base URL - use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Firebase auth token
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('flourish_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('flourish_token');
      localStorage.removeItem('flourish_user');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// ---- PLANTS ----
export async function getPlants() {
  const { data } = await api.get('/plants');
  return data.plants;
}

export async function createAutonomousPlant(plantName: string, userLocation?: string) {
  const { data } = await api.post('/plants/autonomous', { plant_name: plantName, user_location: userLocation });
  return data;
}

export async function createPlant(plant: any) {
  const { data } = await api.post('/plants', plant);
  return data;
}

export async function submitHealthCheck(plantId: string, healthCheck: any) {
  const { data } = await api.post(`/plants/${plantId}/health-check`, healthCheck);
  return data;
}

export async function getPlantSchedule(plantId: string) {
  const { data } = await api.get(`/plants/${plantId}/schedule`);
  return data;
}

export async function completeCareTask(plantId: string, scheduleId: string, notes?: string) {
  const { data } = await api.post(`/plants/${plantId}/schedule/complete`, { schedule_id: scheduleId, notes });
  return data;
}

export async function getTodaySchedule() {
  const { data } = await api.get('/plants/calendar/today');
  return data;
}

export async function getWeekSchedule() {
  const { data } = await api.get('/plants/calendar/week');
  return data;
}

// ---- DASHBOARD ----
export async function getDashboardData() {
  const { data } = await api.get('/dashboard');
  return data;
}

// ---- TASKS ----
export async function getTodayTasks() {
  const { data } = await api.get('/tasks/today');
  return data.tasks;
}

export async function completeTask(taskId: string, notes?: string) {
  const { data } = await api.post(`/tasks/${taskId}/complete`, { notes });
  return data;
}

// ---- AI CHAT ----
export async function chatWithAI(messages: any[]) {
  const { data } = await api.post('/chat', messages);
  return {
    response: data.response,
    suggestions: data.suggestions,
  };
}

export async function analyzeImage(imageData: string, plantId?: string) {
  const { data } = await api.post('/chat/analyze-image', imageData);
  return data;
}

// ---- IMAGES ----
export async function getPlantImage(plantName: string, species: string = '') {
  const { data } = await api.get(`/images/plant/${plantName}?species=${species}`);
  return data.image_url;
}

// Generate tasks for a plant
export async function generateTasksForPlant(plantId: string) {
  const { data } = await api.post(`/tasks/generate/${plantId}`);
  return data;
}

// ---- DOCUMENTS ----
export async function analyzeDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/documents/analyze-document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function analyzeText(text: string) {
  const { data } = await api.post('/documents/analyze-text', { text });
  return data;
}

// ---- LEADERBOARD ----
export async function getLeaderboard(period: 'all_time' | 'monthly' | 'weekly' = 'all_time', limit: number = 100) {
  const { data } = await api.get(`/leaderboard/leaderboard?period=${period}&limit=${limit}`);
  return data;
}

export async function getUserStats() {
  const { data } = await api.get('/leaderboard/stats');
  return data;
}

// ---- NOTIFICATIONS ----
export async function getNotifications(unreadOnly: boolean = false, limit: number = 50) {
  const { data } = await api.get(`/notifications/notifications?unread_only=${unreadOnly}&limit=${limit}`);
  return data.notifications;
}

export async function markNotificationRead(notificationId: string) {
  const { data } = await api.post(`/notifications/notifications/${notificationId}/read`);
  return data;
}

export async function markAllNotificationsRead() {
  const { data } = await api.post('/notifications/notifications/read-all');
  return data;
}

export async function deleteNotification(notificationId: string) {
  const { data } = await api.delete(`/notifications/notifications/${notificationId}`);
  return data;
}

// ---- AGENTIC PLANT LOOKUP ----
export async function lookupPlant(plantName: string) {
  const { data } = await api.post('/plants/lookup', { plant_name: plantName });
  return data;
}

// ---- MCP INTEGRATION ----
export async function getWeatherData(lat: number, lon: number) {
  const { data } = await api.get(`/mcp/weather/${lat}/${lon}`);
  return data;
}

export async function getPlantInfoMCP(plantName: string) {
  const { data } = await api.get(`/mcp/plant-info/${plantName}`);
  return data;
}

export default api;

// Get calendar events (placeholder implementation)
export async function getCalendarEvents() {
  // This would be implemented to get calendar-style events
  return [];
}

// Get care tasks (alias for getTodayTasks)
export async function getCareTasks() {
  return getTodayTasks();
}

// ---- STORAGE / FILE UPLOADS ----
export async function uploadPlantImage(plantId: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post(`/storage/upload/plant-image/${plantId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/storage/upload/document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function uploadProfilePhoto(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/storage/upload/profile-photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

export async function deleteStorageFile(filePath: string) {
  const { data } = await api.delete(`/storage/delete/${encodeURIComponent(filePath)}`);
  return data;
}