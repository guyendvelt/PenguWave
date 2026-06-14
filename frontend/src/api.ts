import { SecurityEvent, User } from "./types";

const API_URL = "http://localhost:3001";

// All requests send the session cookie (HttpOnly, set by the backend on login).
// No token is stored in JS — the cookie is the only credential.
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });

  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : null;

  if (!res.ok) {
    const message =
      (data && (data.error || data.message)) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data as T;
}

export function login(email: string, password: string): Promise<{ user: User }> {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getEvents(): Promise<SecurityEvent[]> {
  return request("/api/events");
}

export function getUsers(): Promise<User[]> {
  return request("/api/users");
}

export function createUser(user: {
  email: string;
  password: string;
  role: string;
}): Promise<User> {
  return request("/api/users", { method: "POST", body: JSON.stringify(user) });
}

export function deleteUser(id: string): Promise<{ message: string }> {
  return request(`/api/users/${id}`, { method: "DELETE" });
}
