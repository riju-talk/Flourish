import { supabase } from "@/integrations/supabase/client";

const API_BASE_URL = "http://127.0.0.1:8000/api"; 

// Helper function for making API calls
const fetchWithAuth = async (
  path: string,
  method: "GET" | "POST" | "PATCH" | "DELETE",
  body?: any
) => {
  const url = `${API_BASE_URL}${path}`;
  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'Something went wrong');
  }

  // For DELETE requests that don't return content
  if (response.status === 204) {
    return null;
  }

  return await response.json();
};

// ---- AUTH ----
export const exchangeSupabaseToken = async () => {
  const token = await getAccessToken();
  const res = await fetch(`${API_BASE_URL}/auth/supabase/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return await res.json();
};

// ---- PROFILE ----
export const getMyProfile = () => fetchWithAuth(`/profiles/me/`, "GET");
export const updateMyProfile = (data: any) => 
  fetchWithAuth(`/profiles/me/`, "PATCH", data);

// ---- PLANTS ----
export const getPlants = (params?: { plant_type?: string; location?: string }) =>
  fetchWithAuth(`/plants/?${new URLSearchParams(params || {})}`, "GET");

export const createPlant = (plant: any) =>
  fetchWithAuth(`/plants/`, "POST", plant);

export const getPlant = (id: string) =>
  fetchWithAuth(`/plants/${id}/`, "GET");

export const updatePlant = (id: string, plant: any) =>
  fetchWithAuth(`/plants/${id}/`, "PATCH", plant);

export const deletePlant = (id: string) =>
  fetchWithAuth(`/plants/${id}/`, "DELETE");

// ---- CARE TASKS ----
export const getCareTasks = (params?: { status?: string; plant?: string }) =>
  fetchWithAuth(`/care-tasks/?${new URLSearchParams(params || {})}`, "GET");

export const createCareTask = (task: any) =>
  fetchWithAuth(`/care-tasks/`, "POST", task);

export const updateCareTask = (id: string, task: any) =>
  fetchWithAuth(`/care-tasks/${id}/`, "PATCH", task);

export const deleteCareTask = (id: string) =>
  fetchWithAuth(`/care-tasks/${id}/`, "DELETE");

// ---- CARE LOGS ----
export const getPlantCareLogs = (params?: { plant?: string }) =>
  fetchWithAuth(`/plant-care-logs/?${new URLSearchParams(params || {})}`, "GET");

export const createPlantCareLog = (log: any) =>
  fetchWithAuth(`/plant-care-logs/`, "POST", log);

export const updatePlantCareLog = (id: string, log: any) =>
  fetchWithAuth(`/plant-care-logs/${id}/`, "PATCH", log);

export const deletePlantCareLog = (id: string) =>
  fetchWithAuth(`/plant-care-logs/${id}/`, "DELETE");

// ---- AI CHAT ----
export const createChatSession = (title: string) =>
  fetchWithAuth(`/ai-chat/sessions/`, "POST", { title });

export const updateChatSession = (id: string, data: any) =>
  fetchWithAuth(`/ai-chat/sessions/${id}/`, "PATCH", data);

export const deleteChatSession = (id: string) =>
  fetchWithAuth(`/ai-chat/sessions/${id}/`, "DELETE");

// ---- CALENDAR ----
export const getCalendarEvents = (start: string, end: string) =>
  fetchWithAuth(`/calendar/?start=${start}&end=${end}`, "GET");

// ---- AI (Advanced) ----
export async function getChatSessions() {
  const res = await fetch(`${API_BASE_URL}/ai-chat/sessions/`);
  if (!res.ok) throw new Error(`Error fetching sessions: ${res.status}`);
  return res.json();
}

export async function getChatMessages(session_id: string) {
  const res = await fetch(`${API_BASE_URL}/ai-chat/messages/?session=${session_id}`);
  if (!res.ok) throw new Error(`Error fetching messages: ${res.status}`);
  return res.json();
}

export async function sendChatMessage(payload: {
  session: string;
  content: string;
  is_user: boolean;
}) {
  const res = await fetch(`${API_BASE_URL}/ai-chat/messages/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Error sending message: ${res.status}`);
  return res.json();
}

export async function askAI({ question }: { question: string }) {
  const res = await fetch(`${API_BASE_URL}/ai/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Error asking AI: ${res.status}`);
  return res.json();
}

const getAccessToken = async (): Promise<string | null> => {
  const { data, error } = await supabase.auth.getSession();
  if (error || !data.session) return null;
  return data.session.access_token;
};

const authHeaders = async () => {
  const token = await getAccessToken();
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};
