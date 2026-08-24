import { Task, CreateTaskInput, UpdateTaskInput } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api";

export async function fetchTasks(): Promise<Task[]> {
  const res = await fetch(`${API_BASE_URL}/tasks`, { cache: "no-store" });
  if (!res.ok) throw new Error("Error al obtener las tareas");
  return res.json();
}

export async function fetchTask(id: number): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Tarea no encontrada");
  return res.json();
}

export async function createTask(data: CreateTaskInput): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.message?.[0] || "Error al crear la tarea");
  }
  return res.json();
}

export async function updateTask(
  id: number,
  data: UpdateTaskInput
): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.message?.[0] || "Error al actualizar la tarea");
  }
  return res.json();
}

export async function deleteTask(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Error al eliminar la tarea");
}
