import axios from 'axios';

// API base URL - use environment variable or default to localhost for backend in Replit
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const storedUser = localStorage.getItem('flourish_user');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      // In real production, you'd use auth.currentUser.getIdToken()
      // But for this project, we'll assume the backend verifies the uid for simplicity 
      // or we handle token refresh in a more complex setup.
      config.headers.Authorization = `Bearer ${user.uid}`;
    }
    return config;
  },
  (error) => {
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

// Get calendar events (placeholder implementation)
export async function getCalendarEvents() {
  // This would be implemented to get calendar-style events
  return [];
}

// Get care tasks (alias for getTodayTasks)
export async function getCareTasks() {
  return getTodayTasks();
}