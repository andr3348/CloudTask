"use client";

import { useState } from "react";
import { CreateTaskInput, TaskStatus, TaskPriority } from "@/lib/api/types";
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
import { ImageIcon, XIcon, Loader2Icon } from "lucide-react";
import { toast } from "sonner";

interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateTaskInput) => void;
  isCreating?: boolean;
}

export function CreateTaskDialog({
  open,
  onOpenChange,
  onSubmit,
  isCreating,
}: CreateTaskDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("PENDING");
  const [priority, setPriority] = useState<TaskPriority>("MEDIUM");
  const [dueDate, setDueDate] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast.error("Por favor selecciona un archivo de imagen");
        return;
      }
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  }

  function removeImage() {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setImageFile(null);
    setImagePreview(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;

    let imgUrl: string | null = null;
    if (imageFile) {
      setIsUploading(true);
      try {
        const uploadRes = await uploadImage(imageFile);
        imgUrl = uploadRes.url;
      } catch (err) {
        toast.error(
          err instanceof Error ? err.message : "Error al subir la imagen a S3",
        );
        setIsUploading(false);
        return;
      }
      setIsUploading(false);
    }

    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      status,
      priority,
      dueDate: dueDate ? new Date(dueDate).toISOString() : null,
      imgUrl,
    });
  }

  function resetForm() {
    setTitle("");
    setDescription("");
    setStatus("PENDING");
    setPriority("MEDIUM");
    setDueDate("");
    removeImage();
  }

  function handleOpenChange(nextOpen: boolean) {
    if (!nextOpen) resetForm();
    onOpenChange(nextOpen);
  }

  const busy = isCreating || isUploading;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="sm:max-w-lg max-h-[90vh] overflow-y-auto"
        showCloseButton
      >
        <DialogHeader>
          <DialogTitle>Nueva Tarea</DialogTitle>
          <DialogDescription>
            Completa los campos para crear una nueva tarea.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="title" className="text-sm font-medium">
              Título <span className="text-destructive">*</span>
            </label>
            <Input
              id="title"
              placeholder="Nombre de la tarea"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              autoFocus
            />
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="description" className="text-sm font-medium">
              Descripción
            </label>
            <Textarea
              id="description"
              placeholder="Describe la tarea (opcional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
              className="min-h-24"
            />
          </div>

          {/* Image Upload */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium">Imagen de la tarea</label>
            {imagePreview ? (
              <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-muted/30">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imagePreview}
                  alt="Vista previa"
                  className="h-full w-full object-cover"
                />
                <Button
                  type="button"
                  variant="destructive"
                  size="icon-xs"
                  className="absolute top-2 right-2 rounded-full"
                  onClick={removeImage}
                >
                  <XIcon className="size-3.5" />
                </Button>
              </div>
            ) : (
              <label
                htmlFor="create-image-upload"
                className="flex flex-col items-center justify-center gap-1.5 rounded-lg border border-dashed border-border py-4 text-sm text-muted-foreground hover:bg-muted/40 cursor-pointer transition-colors"
              >
                <ImageIcon className="size-6 text-muted-foreground/70" />
                <span className="font-medium text-foreground">
                  Seleccionar imagen
                </span>
                <span className="text-xs text-muted-foreground">
                  PNG, JPG o WEBP (máx. 10MB)
                </span>
                <input
                  id="create-image-upload"
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
            <label htmlFor="dueDate" className="text-sm font-medium">
              Fecha límite
            </label>
            <Input
              id="dueDate"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={busy}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={!title.trim() || busy}>
              {busy ? (
                <>
                  <Loader2Icon className="size-4 animate-spin mr-2" />
                  {isUploading ? "Subiendo a S3..." : "Creando..."}
                </>
              ) : (
                "Crear Tarea"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
