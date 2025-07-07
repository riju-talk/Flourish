import axios from 'axios'

/** Core API base (no auth) */
const API_BASE_URL = 'http://[127.0.0.1]:8000/api'

/** Chat API base */
const CHAT_BASE_URL = 'https://localhost:8000/ai-chat'

/** Helper to build query strings */
const qs = (params: Record<string, any>) =>
  new URLSearchParams(params as Record<string, string>).toString()

// ---- PROFILE ----
export async function getMyProfile() {
  const { data } = await axios.get(`${API_BASE_URL}/profiles/me/`)
  return data
}

export async function updateMyProfile(payload: any) {
  const { data } = await axios.patch(
    `${API_BASE_URL}/profiles/me/`,
    payload
  )
  return data
}

// ---- PLANTS ----
export async function getPlants(
  params: { plant_type?: string; location?: string } = {}
) {
  const qsString = qs(params)
  const { data } = await axios.get(
    `${API_BASE_URL}/plants/${qsString ? `?${qsString}` : ''}`
  )
  return data
}

export async function createPlant(plant: any) {
  const { data } = await axios.post(`${API_BASE_URL}/plants/`, plant)
  return data
}

export async function getPlant(id: string) {
  const { data } = await axios.get(`${API_BASE_URL}/plants/${id}/`)
  return data
}

export async function updatePlant(id: string, plant: any) {
  const { data } = await axios.patch(
    `${API_BASE_URL}/plants/${id}/`,
    plant
  )
  return data
}

export async function deletePlant(id: string) {
  await axios.delete(`${API_BASE_URL}/plants/${id}/`)
}

// ---- CARE TASKS ----
export async function getCareTasks(
  params: { status?: string; plant?: string } = {}
) {
  const qsString = qs(params)
  const { data } = await axios.get(
    `${API_BASE_URL}/care-tasks/${qsString ? `?${qsString}` : ''}`
  )
  return data
}

export async function createCareTask(task: any) {
  const { data } = await axios.post(`${API_BASE_URL}/care-tasks/`, task)
  return data
}

export async function updateCareTask(id: string, task: any) {
  const { data } = await axios.patch(
    `${API_BASE_URL}/care-tasks/${id}/`,
    task
  )
  return data
}

export async function deleteCareTask(id: string) {
  await axios.delete(`${API_BASE_URL}/care-tasks/${id}/`)
}

// ---- CARE LOGS ----
export async function getPlantCareLogs(
  params: { plant?: string } = {}
) {
  const qsString = qs(params)
  const { data } = await axios.get(
    `${API_BASE_URL}/plant-care-logs/${qsString ? `?${qsString}` : ''}`
  )
  return data
}

export async function createPlantCareLog(log: any) {
  const { data } = await axios.post(
    `${API_BASE_URL}/plant-care-logs/`,
    log
  )
  return data
}

export async function updatePlantCareLog(id: string, log: any) {
  const { data } = await axios.patch(
    `${API_BASE_URL}/plant-care-logs/${id}/`,
    log
  )
  return data
}

export async function deletePlantCareLog(id: string) {
  await axios.delete(`${API_BASE_URL}/plant-care-logs/${id}/`)
}

// ---- CALENDAR ----
export async function getCalendarEvents(
  start: string,
  end: string,
  email?: string
) {
  const params: Record<string, any> = { start, end }
  if (email) params.email = email
  const { data } = await axios.get(
    `${API_BASE_URL}/calendar/?${qs(params)}`
  )
  return data
}

// ---- AI CHAT ----
/** Fetch full message history for an email */
export async function fetchChatMessages(email: string) {
  const { data } = await axios.get(CHAT_BASE_URL, {
    params: { email },
  })
  return data.messages
}

/** Send a new message; returns the assistant’s reply text */
export async function sendChatMessage(
    email: string,
    question: string,
    plant_type?: string,
    context?: Record<string, any>
  ) {
    const payload: any = { email, question }
    if (plant_type) payload.plant_type = plant_type
    if (context) payload.context = context
    
    console.log(payload)
    const { data } = await axios.post("https://localhost:8000/ai-chat/", payload)
    return {
      reply: data.response,
      suggestions: data.suggestions,
    }
} 