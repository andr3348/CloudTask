"use client";

import { Task, TaskStatus } from "@/lib/api/types";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardAction,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Trash2Icon, CalendarIcon, CircleIcon } from "lucide-react";

const statusConfig: Record<
  string,
  { label: string; className: string; dotColor: string }
> = {
  PENDING: {
    label: "Pendiente",
    className: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    dotColor: "text-amber-400",
  },
  IN_PROGRESS: {
    label: "En Progreso",
    className: "bg-blue-500/15 text-blue-400 border-blue-500/20",
    dotColor: "text-blue-400",
  },
  COMPLETED: {
    label: "Completada",
    className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    dotColor: "text-emerald-400",
  },
};

const priorityConfig: Record<string, { label: string; className: string }> = {
  LOW: { label: "Baja", className: "text-muted-foreground" },
  MEDIUM: { label: "Media", className: "text-amber-400" },
  HIGH: { label: "Alta", className: "text-red-400" },
};

interface TaskCardProps {
  task: Task;
  onDelete: (task: Task) => void;
  onEdit: (task: Task) => void;
  onStatusChange: (task: Task, newStatus: TaskStatus) => void;
}

export function TaskCard({ task, onDelete, onEdit, onStatusChange }: TaskCardProps) {
  const status = statusConfig[task.status] ?? statusConfig.PENDING;
  const priority = priorityConfig[task.priority] ?? priorityConfig.MEDIUM;

  const formattedDate = new Date(task.createdAt).toLocaleDateString("es-ES", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Card
      className="break-inside-avoid mb-4 bg-card hover:ring-foreground/20 transition-all cursor-pointer"
      onClick={() => onEdit(task)}
    >
      <CardHeader>
        <CardTitle className="line-clamp-2">{task.title}</CardTitle>
        <CardAction>
          {/* Status badge with dropdown to change status quickly */}
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <button
                  className="outline-none"
                  onClick={(e) => e.stopPropagation()}
                />
              }
            >
              <Badge className={`${status.className} cursor-pointer hover:opacity-80 transition-opacity`}>
                {status.label}
              </Badge>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
              <DropdownMenuGroup>
                <DropdownMenuLabel>Cambiar estado</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {(Object.entries(statusConfig) as [TaskStatus, typeof status][]).map(
                  ([key, config]) => (
                    <DropdownMenuItem
                      key={key}
                      onClick={() => {
                        if (key !== task.status) {
                          onStatusChange(task, key);
                        }
                      }}
                    >
                      <CircleIcon
                        className={`size-2.5 fill-current ${config.dotColor}`}
                      />
                      {config.label}
                      {key === task.status && (
                        <span className="ml-auto text-xs text-muted-foreground">
                          actual
                        </span>
                      )}
                    </DropdownMenuItem>
                  )
                )}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardAction>
      </CardHeader>

      {task.description && (
        <CardDescription className="px-6 line-clamp-4 text-muted-foreground">
          {task.description}
        </CardDescription>
      )}

      <CardFooter className="justify-between gap-2">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <CalendarIcon className="size-3" />
            {formattedDate}
          </span>
          <span className={priority.className}>● {priority.label}</span>
        </div>
        <Button
          variant="ghost"
          size="icon-xs"
          className="text-muted-foreground hover:text-destructive"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(task);
          }}
        >
          <Trash2Icon className="size-3.5" />
        </Button>
      </CardFooter>
    </Card>
  );
}
