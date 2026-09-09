"use client";

import { useState, useEffect } from "react";
import {
  Task,
  UpdateTaskInput,
  TaskStatus,
  TaskPriority,
} from "@/lib/api/types";
import { uploadImage } from "@/lib/api/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ImageIcon, XIcon, Loader2Icon, RefreshCwIcon } from "lucide-react";
import { toast } from "sonner";

interface EditTaskDialogProps {
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (id: number, data: UpdateTaskInput) => void;
  isUpdating?: boolean;
}

export function EditTaskDialog({
  task,
  open,
  onOpenChange,
  onSubmit,
  isUpdating,
}: EditTaskDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("PENDING");
  const [priority, setPriority] = useState<TaskPriority>("MEDIUM");
  const [dueDate, setDueDate] = useState("");

  const [currentImgUrl, setCurrentImgUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Pre-fill form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description ?? "");
      setStatus(task.status);
      setPriority(task.priority);
      setDueDate(
        task.dueDate ? new Date(task.dueDate).toISOString().split("T")[0] : "",
      );
      setCurrentImgUrl(task.imgUrl ?? null);
      setImageFile(null);
      setImagePreview(null);
    }
  }, [task]);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast.error("Por favor selecciona un archivo de imagen");
        return;
      }
      if (imagePreview) URL.revokeObjectURL(imagePreview);
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setCurrentImgUrl(null);
    }
  }

  function removeImage() {
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImageFile(null);
    setImagePreview(null);
    setCurrentImgUrl(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task || !title.trim()) return;

    let finalImgUrl: string | null = currentImgUrl;

    if (imageFile) {
      setIsUploading(true);
      try {
        const uploadRes = await uploadImage(imageFile);
        finalImgUrl = uploadRes.url;
      } catch (err) {
        toast.error(
          err instanceof Error ? err.message : "Error al subir la imagen a S3",
        );
        setIsUploading(false);
        return;
      }
      setIsUploading(false);
    }

    onSubmit(task.id, {
      title: title.trim(),
      description: description.trim() || null,
      status,
      priority,
      dueDate: dueDate ? new Date(dueDate).toISOString() : null,
      imgUrl: finalImgUrl,
    });
  }

  const busy = isUpdating || isUploading;
  const activeImage = imagePreview || currentImgUrl;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="sm:max-w-lg max-h-[90vh] overflow-y-auto"
        showCloseButton
      >
        <DialogHeader>
          <DialogTitle>Editar Tarea</DialogTitle>
          <DialogDescription>
            Modifica los campos que desees y guarda los cambios.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-title" className="text-sm font-medium">
              Título <span className="text-destructive">*</span>
            </label>
            <Input
              id="edit-title"
              placeholder="Nombre de la tarea"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              autoFocus
            />
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-description" className="text-sm font-medium">
              Descripción
            </label>
            <Textarea
              id="edit-description"
              placeholder="Describe la tarea (opcional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
              className="min-h-24"
            />
          </div>

          {/* Image Section */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium">Imagen de la tarea</label>
            {activeImage ? (
              <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-muted/30">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={activeImage}
                  alt="Vista previa"
                  className="h-full w-full object-cover"
                />
                <div className="absolute top-2 right-2 flex gap-1.5">
                  <label
                    htmlFor="edit-image-replace"
                    className="flex size-7 items-center justify-center rounded-full bg-background/80 hover:bg-background cursor-pointer text-foreground shadow transition-colors"
                    title="Cambiar imagen"
                  >
                    <RefreshCwIcon className="size-3.5" />
                    <input
                      id="edit-image-replace"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleImageChange}
                    />
                  </label>
                  <Button
                    type="button"
                    variant="destructive"
                    size="icon-xs"
                    className="size-7 rounded-full"
                    onClick={removeImage}
                    title="Eliminar imagen"
                  >
                    <XIcon className="size-3.5" />
                  </Button>
                </div>
              </div>
            ) : (
              <label
                htmlFor="edit-image-upload"
                className="flex flex-col items-center justify-center gap-1.5 rounded-lg border border-dashed border-border py-4 text-sm text-muted-foreground hover:bg-muted/40 cursor-pointer transition-colors"
              >
                <ImageIcon className="size-6 text-muted-foreground/70" />
                <span className="font-medium text-foreground">
                  Agregar una imagen
                </span>
                <span className="text-xs text-muted-foreground">
                  PNG, JPG o WEBP (máx. 10MB)
                </span>
                <input
                  id="edit-image-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageChange}
                />
              </label>
            )}
          </div>

          {/* Status & Priority row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">Estado</label>
              <Select
                value={status}
                onValueChange={(v) => setStatus(v as TaskStatus)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PENDING">Pendiente</SelectItem>
                  <SelectItem value="IN_PROGRESS">En Progreso</SelectItem>
                  <SelectItem value="COMPLETED">Completada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">Prioridad</label>
              <Select
                value={priority}
                onValueChange={(v) => setPriority(v as TaskPriority)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="LOW">Baja</SelectItem>
                  <SelectItem value="MEDIUM">Media</SelectItem>
                  <SelectItem value="HIGH">Alta</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Due Date */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-dueDate" className="text-sm font-medium">
              Fecha límite
            </label>
            <Input
              id="edit-dueDate"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={busy}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={!title.trim() || busy}>
              {busy ? (
                <>
                  <Loader2Icon className="size-4 animate-spin mr-2" />
                  {isUploading ? "Subiendo a S3..." : "Guardando..."}
                </>
              ) : (
                "Guardar Cambios"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
