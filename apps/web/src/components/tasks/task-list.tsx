"use client";

import { useEffect, useState, useCallback } from "react";
import { Task, CreateTaskInput, UpdateTaskInput, TaskStatus } from "@/lib/api/types";
import { fetchTasks, createTask, updateTask, deleteTask } from "@/lib/api/api";
import { TaskCard } from "./task-card";
import { CreateTaskDialog } from "./create-task-dialog";
import { EditTaskDialog } from "./edit-task-dialog";
import { DeleteTaskDialog } from "./delete-task-dialog";
import { Button } from "@/components/ui/button";
import { PlusIcon, Loader2Icon, InboxIcon } from "lucide-react";
import { toast } from "sonner";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create dialog state
  const [createOpen, setCreateOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  // Edit dialog state
  const [editTarget, setEditTarget] = useState<Task | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  // Delete dialog state
  const [deleteTarget, setDeleteTarget] = useState<Task | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadTasks = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Create
  async function handleCreate(data: CreateTaskInput) {
    setIsCreating(true);
    try {
      const newTask = await createTask(data);
      setTasks((prev) => [newTask, ...prev]);
      setCreateOpen(false);
      toast.success("Tarea creada exitosamente");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al crear la tarea"
      );
    } finally {
      setIsCreating(false);
    }
  }

  // Edit (full update)
  async function handleUpdate(id: number, data: UpdateTaskInput) {
    setIsUpdating(true);
    try {
      const updated = await updateTask(id, data);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
      setEditTarget(null);
      toast.success("Tarea actualizada");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al actualizar la tarea"
      );
    } finally {
      setIsUpdating(false);
    }
  }

  // Quick status change (from badge dropdown)
  async function handleStatusChange(task: Task, newStatus: TaskStatus) {
    try {
      const updated = await updateTask(task.id, {
        title: task.title,
        description: task.description,
        status: newStatus,
        priority: task.priority,
        dueDate: task.dueDate,
      });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
      toast.success(`Estado cambiado a ${newStatus === "PENDING" ? "Pendiente" : newStatus === "IN_PROGRESS" ? "En Progreso" : "Completada"}`);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al cambiar el estado"
      );
    }
  }

  // Delete
  async function handleDelete() {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await deleteTask(deleteTarget.id);
      setTasks((prev) => prev.filter((t) => t.id !== deleteTarget.id));
      setDeleteTarget(null);
      toast.success("Tarea eliminada");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error al eliminar la tarea"
      );
    } finally {
      setIsDeleting(false);
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center py-32">
        <Loader2Icon className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 py-32 text-center">
        <p className="text-muted-foreground">No se pudieron cargar las tareas</p>
        <p className="text-sm text-destructive">{error}</p>
        <Button variant="outline" onClick={() => { setLoading(true); loadTasks(); }}>
          Reintentar
        </Button>
      </div>
    );
  }

  return (
    <>
      {/* Empty state */}
      {tasks.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 py-32 text-center">
          <InboxIcon className="size-16 text-muted-foreground/50" />
          <div>
            <p className="text-lg font-medium">No hay tareas aún</p>
            <p className="text-sm text-muted-foreground">
              Presiona el botón + para crear tu primera tarea
            </p>
          </div>
        </div>
      ) : (
        /* Masonry grid */
        <div className="columns-1 gap-4 sm:columns-2 lg:columns-3">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onEdit={(t) => setEditTarget(t)}
              onDelete={(t) => setDeleteTarget(t)}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}

      {/* FAB - Floating Action Button */}
      <Button
        onClick={() => setCreateOpen(true)}
        className="fixed bottom-8 right-8 z-40 size-14 rounded-full shadow-lg hover:shadow-xl transition-shadow"
        size="icon-lg"
      >
        <PlusIcon className="size-7" />
      </Button>

      {/* Create Task Dialog */}
      <CreateTaskDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSubmit={handleCreate}
        isCreating={isCreating}
      />

      {/* Edit Task Dialog */}
      <EditTaskDialog
        task={editTarget}
        open={!!editTarget}
        onOpenChange={(open) => {
          if (!open) setEditTarget(null);
        }}
        onSubmit={handleUpdate}
        isUpdating={isUpdating}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteTaskDialog
        task={deleteTarget}
        open={!!deleteTarget}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
        onConfirm={handleDelete}
        isDeleting={isDeleting}
      />
    </>
  );
}
