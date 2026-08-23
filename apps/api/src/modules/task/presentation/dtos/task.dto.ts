import { TaskEntity } from '../../domain/entity/task.entity';

export class TaskDto {
  id: number;
  title: string;
  description?: string | null;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  dueDate?: Date | null;
  createdAt: Date;
  updatedAt: Date;

  static fromEntity(entity: TaskEntity): TaskDto {
    const dto = new TaskDto();
    dto.id = entity.id;
    dto.title = entity.title;
    dto.description = entity.description;
    dto.status = entity.status;
    dto.priority = entity.priority;
    dto.dueDate = entity.dueDate;
    dto.createdAt = entity.createdAt;
    dto.updatedAt = entity.updatedAt;
    return dto;
  }
}
