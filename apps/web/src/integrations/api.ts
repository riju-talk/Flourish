import axios from 'axios'

/** API base URL */
const API_BASE_URL = 'http://localhost:8000'

/** Helper to build query strings */
const qs = (params: Record<string, any>) =>
  new URLSearchParams(params as Record<string, string>).toString()

// ---- PLANTS ----
export async function getPlants(userId: string) {
  const { data } = await axios.get(`${API_BASE_URL}/plants/${userId}`)
  return data.plants
}

export async function createPlant(plant: any) {
  const { data } = await axios.post(`${API_BASE_URL}/plants/`, plant)
  return data
}

export async function submitHealthCheck(plantId: string, healthCheck: any) {
  const { data } = await axios.post(
    `${API_BASE_URL}/plants/${plantId}/health-check`,
    healthCheck
  )
  return data
}

// ---- DASHBOARD ----
export async function getDashboardData(userId: string) {
  const { data } = await axios.get(`${API_BASE_URL}/dashboard/${userId}`)
  return data
}

// ---- TASKS ----
export async function getTodayTasks(userId: string) {
  const { data } = await axios.get(`${API_BASE_URL}/tasks/${userId}/today`)
  return data.tasks
}

export async function completeTask(taskId: string, notes?: string) {
  const { data } = await axios.post(`${API_BASE_URL}/tasks/${taskId}/complete`, {
    notes
  })
  return data
}

// ---- AI CHAT ----
export async function chatWithAI(messages: any[]) {
  const { data } = await axios.post(`${API_BASE_URL}/chat`, messages)
  return {
    response: data.response,
    suggestions: data.suggestions
  }
}

export async function analyzeImage(imageData: string, plantId?: string) {
  const { data } = await axios.post(`${API_BASE_URL}/analyze-image`, {
    image_data: imageData,
    plant_id: plantId
  })
  return data
}

// Legacy compatibility functions
export async function fetchChatMessages(email: string) {
  // For now, return empty array - implement Firebase integration later
  return []
}

export async function sendChatMessage(email: string, question: string, plant_type?: string, context?: any) {
  const messages = [{ role: 'user', content: question, timestamp: new Date() }]
  const response = await chatWithAI(messages)
  return {
    reply: response.response,
    suggestions: response.suggestions
  }
}

// Mock functions for calendar (implement with Firebase later)
export async function getCalendarEvents(start: string, end: string) {
  return []
}

export async function getCareTasks(params: any = {}) {
  return []
}