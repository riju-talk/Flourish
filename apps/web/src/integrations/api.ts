import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ---- PLANTS ----
export async function getPlants() {
  const { data } = await api.get('/plants');
  return data.plants;
}

export async function createPlant(plant: any) {
  const { data } = await api.post('/plants', plant);
  return data;
}

export async function submitHealthCheck(plantId: string, healthCheck: any) {
  const { data } = await api.post(`/plants/${plantId}/health-check`, healthCheck);
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